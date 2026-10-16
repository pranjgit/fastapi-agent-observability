from typing import Any

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:  # optional extra
    BaseCallbackHandler = object


class ObservabilityCallbackHandler(BaseCallbackHandler):
    """Capture common LangChain callback lifecycle events into the local trace store."""

    def __init__(self, observability):
        self.observability = observability
        self._handles: dict[str, Any] = {}

    def on_chain_start(self, serialized, inputs, *, run_id, parent_run_id=None, name=None, **kwargs):
        self._start("chain", serialized, inputs, run_id, parent_run_id, name)

    def on_tool_start(self, serialized, input_str, *, run_id, parent_run_id=None, name=None, **kwargs):
        self._start("tool", serialized, {"input": input_str}, run_id, parent_run_id, name)

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id=None, name=None, **kwargs):
        self._start("llm", serialized, {"prompts": prompts}, run_id, parent_run_id, name)

    def on_chat_model_start(self, serialized, messages, *, run_id, parent_run_id=None, name=None, **kwargs):
        self._start("llm", serialized, {"messages": messages}, run_id, parent_run_id, name)

    def _start(self, run_type, serialized, inputs, run_id, parent_run_id, name):
        metadata = serialized or {}
        display_name = name or metadata.get("name") or metadata.get("id", [run_type])[-1]
        handle = self.observability.tracer.start_run(
            str(display_name), run_type, inputs,
            run_id=str(run_id),
            parent_run_id=str(parent_run_id) if parent_run_id else None,
            trace_id=self._trace_for_parent(parent_run_id, run_id),
        )
        self._handles[str(run_id)] = handle

    def _trace_for_parent(self, parent_run_id, run_id):
        if parent_run_id and str(parent_run_id) in self._handles:
            return self._handles[str(parent_run_id)].trace_id
        return str(run_id)

    def on_chain_end(self, outputs, *, run_id, **kwargs):
        self._finish(run_id, outputs=outputs)

    def on_tool_end(self, output, *, run_id, **kwargs):
        self._finish(run_id, outputs={"output": output})

    def on_llm_end(self, response, *, run_id, **kwargs):
        self._finish(run_id, outputs={"response": str(response)})

    def on_chain_error(self, error, *, run_id, **kwargs):
        self._finish(run_id, error=error)

    def on_tool_error(self, error, *, run_id, **kwargs):
        self._finish(run_id, error=error)

    def on_llm_error(self, error, *, run_id, **kwargs):
        self._finish(run_id, error=error)

    def _finish(self, run_id, outputs=None, error=None):
        handle = self._handles.pop(str(run_id), None)
        if not handle:
            return
        if error is not None:
            handle.set_error(error)
        if outputs is not None:
            handle.set_outputs(outputs)
        handle.finish("error" if error is not None else "success")


def get_langchain_callback(observability):
    """Return a callback handler for LangChain chains and LangGraph execution."""
    if BaseCallbackHandler is object:
        raise ImportError(
            "Install the optional integration with: pip install 'fastapi-agent-observability[langchain]'"
        )
    return ObservabilityCallbackHandler(observability)
