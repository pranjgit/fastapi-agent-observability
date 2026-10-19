import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, select

from .config import ObservabilityConfig
from .storage.database import Database
from .storage.models import RunRecord
from .tracing.recorder import Tracer


class Observability:
    """Embeddable observability extension that delegates identity to the host application."""

    def __init__(
        self,
        config: ObservabilityConfig,
        *,
        get_current_user: Callable[..., Any],
        is_admin: Callable[[Any], Any],
    ) -> None:
        self.config = config
        self.get_current_user = get_current_user
        self.is_admin = is_admin
        self.database = Database(config.database_url)
        self.tracer = Tracer(self.database, config)
        template_dir = Path(__file__).parent / "dashboard" / "templates"
        self.templates = Jinja2Templates(directory=str(template_dir))

    def create_schema(self) -> None:
        """Convenience for local development/tests. Prefer Alembic migrations in production."""
        self.database.create_schema()

    async def _authorize(self, user: Any) -> Any:
        allowed = self.is_admin(user)
        if inspect.isawaitable(allowed):
            allowed = await allowed
        if not allowed:
            raise HTTPException(status_code=403, detail="Administrator access required")
        return user

    def mount(self, app: FastAPI) -> None:
        """Mount protected HTML and JSON endpoints into the host FastAPI app."""
        router = APIRouter()

        @router.get("", response_class=HTMLResponse, name="observability_dashboard")
        async def dashboard(
            request: Request,
            user: Any = Depends(self.get_current_user),
        ):
            await self._authorize(user)
            with self.database.session() as session:
                traces = session.scalars(
                    select(RunRecord)
                    .where(RunRecord.parent_run_id.is_(None))
                    .order_by(desc(RunRecord.started_at))
                    .limit(self.config.default_page_size)
                ).all()
                rows = [self._serialize_run(run) for run in traces]
            return self.templates.TemplateResponse(
                request=request,
                name="index.html",
                context={"app_name": self.config.app_name, "traces": rows},
            )

        @router.get("/traces/{run_id}", response_class=HTMLResponse, name="observability_trace")
        async def trace_detail(
            request: Request,
            run_id: str,
            user: Any = Depends(self.get_current_user),
        ):
            await self._authorize(user)
            with self.database.session() as session:
                record = session.get(RunRecord, run_id)
                if record is None:
                    raise HTTPException(status_code=404, detail="Trace not found")
                children = session.scalars(
                    select(RunRecord)
                    .where(RunRecord.trace_id == record.trace_id)
                    .order_by(RunRecord.started_at)
                ).all()
                payload = self._serialize_run(record)
                child_rows = [self._serialize_run(child) for child in children]
            return self.templates.TemplateResponse(
                request=request,
                name="trace_detail.html",
                context={"app_name": self.config.app_name, "trace": payload, "runs": child_rows},
            )

        @router.get("/api/traces")
        async def list_traces(user: Any = Depends(self.get_current_user)):
            await self._authorize(user)
            with self.database.session() as session:
                records = session.scalars(
                    select(RunRecord)
                    .where(RunRecord.parent_run_id.is_(None))
                    .order_by(desc(RunRecord.started_at))
                    .limit(self.config.default_page_size)
                ).all()
                return {"items": [self._serialize_run(r) for r in records]}

        app.include_router(router, prefix=self.config.dashboard_path)

    @staticmethod
    def _serialize_run(run: RunRecord) -> dict[str, Any]:
        return {
            "id": run.id,
            "trace_id": run.trace_id,
            "parent_run_id": run.parent_run_id,
            "name": run.name,
            "run_type": run.run_type,
            "status": run.status,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "ended_at": run.ended_at.isoformat() if run.ended_at else None,
            "latency_ms": run.latency_ms,
            "inputs_json": run.inputs_json,
            "outputs_json": run.outputs_json,
            "error": run.error,
        }
