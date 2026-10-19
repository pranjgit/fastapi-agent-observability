import contextvars
import inspect
import json
import time
import uuid
from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from functools import wraps
from typing import Any

from ..config import ObservabilityConfig
from ..storage.database import Database
from ..storage.models import RunRecord

_current_run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "observability_current_run_id", default=None
)
_current_trace_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "observability_current_trace_id", default=None
)


def _json(value: Any, max_chars: int) -> str:
    try:
        rendered = json.dumps(value, default=str, ensure_ascii=False)
    except Exception:
        rendered = json.dumps({"unserializable": type(value).__name__})
    if len(rendered) > max_chars:
        rendered = rendered[: max_chars - 20] + '… [truncated]'
    return rendered


class RunHandle(AbstractContextManager):
    def __init__(
        self, tracer: "Tracer", name: str, run_type: str, inputs: Any = None,
        *, parent_run_id: str | None = None, trace_id: str | None = None,
        run_id: str | None = None,
    ):
        self.tracer = tracer
        self.id = run_id or str(uuid.uuid4())
        self.parent_run_id = parent_run_id if parent_run_id is not None else _current_run_id.get()
        self.trace_id = trace_id or _current_trace_id.get() or str(uuid.uuid4())
        self.name = name[:255]
        self.run_type = run_type[:50]
        self.started_at = datetime.now(timezone.utc)
        self._started_clock = time.perf_counter()
        self._parent_token = None
        self._trace_token = None
        self._closed = False
        self._inputs = _json(inputs, tracer.config.max_payload_chars) if inputs is not None else None
        self._outputs = None
        self._error = None
        self.tracer._persist_start(self)

    def __enter__(self):
        self._parent_token = _current_run_id.set(self.id)
        self._trace_token = _current_trace_id.set(self.trace_id)
        return self

    def set_outputs(self, outputs: Any) -> None:
        self._outputs = _json(outputs, self.tracer.config.max_payload_chars)

    def set_error(self, error: Any) -> None:
        self._error = str(error)[: self.tracer.config.max_payload_chars]

    def finish(self, status: str | None = None) -> None:
        if self._closed:
            return
        ended = datetime.now(timezone.utc)
        self.tracer._persist_finish(
            self.id,
            status=status or ("error" if self._error else "success"),
            ended_at=ended,
            latency_ms=(time.perf_counter() - self._started_clock) * 1000,
            outputs_json=self._outputs,
            error=self._error,
        )
        self._closed = True
        if self._parent_token is not None:
            _current_run_id.reset(self._parent_token)
        if self._trace_token is not None:
            _current_trace_id.reset(self._trace_token)

    def __exit__(self, exc_type, exc, tb):
        if exc is not None:
            self.set_error(f"{type(exc).__name__}: {exc}")
        self.finish("error" if exc is not None else None)
        return False


class Tracer:
    def __init__(self, database: Database, config: ObservabilityConfig):
        self.database = database
        self.config = config

    def start_run(self, name: str, run_type: str = "chain", inputs: Any = None, **ids) -> RunHandle:
        return RunHandle(self, name, run_type, inputs, **ids)

    def trace(self, name: str, run_type: str = "chain"):
        def decorator(fn: Callable):
            if inspect.iscoroutinefunction(fn):
                @wraps(fn)
                async def async_wrapper(*args, **kwargs):
                    with self.start_run(name, run_type, {"args": args, "kwargs": kwargs}) as run:
                        result = await fn(*args, **kwargs)
                        run.set_outputs(result)
                        return result
                return async_wrapper

            @wraps(fn)
            def wrapper(*args, **kwargs):
                with self.start_run(name, run_type, {"args": args, "kwargs": kwargs}) as run:
                    result = fn(*args, **kwargs)
                    run.set_outputs(result)
                    return result
            return wrapper
        return decorator

    def _persist_start(self, handle: RunHandle) -> None:
        try:
            with self.database.session() as session:
                session.add(RunRecord(
                    id=handle.id, trace_id=handle.trace_id,
                    parent_run_id=handle.parent_run_id, name=handle.name,
                    run_type=handle.run_type, status="running",
                    started_at=handle.started_at, inputs_json=handle._inputs,
                ))
        except Exception:
            # Observability should not fail the business operation due to storage errors.
            # Replace with a logger/metrics hook in production deployments.
            pass

    def _persist_finish(self, run_id, status, ended_at, latency_ms, outputs_json, error) -> None:
        try:
            with self.database.session() as session:
                record = session.get(RunRecord, run_id)
                if record:
                    record.status = status
                    record.ended_at = ended_at
                    record.latency_ms = latency_ms
                    record.outputs_json = outputs_json
                    record.error = error
        except Exception:
            pass
