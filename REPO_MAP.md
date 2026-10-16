# Repository Symbol & Architecture Map

> **Notice for AI Agents:** Consult this map BEFORE opening or reading full source files.
> It contains symbols, classes, method signatures, line numbers, and file hierarchies.
> Update this map after modifying or adding code using `.agents/skills/repo-map/SKILL.md`.

## File Hierarchy & Summary

### Non-Python Assets & Templates
- [`src/fastapi_agent_observability/dashboard/templates/index.html`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/dashboard/templates/index.html) (1421 bytes)
- [`src/fastapi_agent_observability/dashboard/templates/trace_detail.html`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/dashboard/templates/trace_detail.html) (1614 bytes)

### Python Modules & Symbol Index

#### [`src/fastapi_agent_observability/config.py`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/config.py) (18 lines)
- **Class** [`ObservabilityConfig`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/config.py#L5)``
  - [`__post_init__`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/config.py#L12): `__post_init__(self) -> None`

#### [`src/fastapi_agent_observability/extension.py`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/extension.py) (123 lines)
- **Class** [`Observability`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/extension.py#L16)`` - *Embeddable observability extension that delegates identity to the host application.*
  - [`__init__`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/extension.py#L19): `__init__(self, config: ObservabilityConfig, *, get_current_user: Callable[..., Any], is_admin: Callable[[Any], Any]) -> None`
  - [`create_schema`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/extension.py#L34): `create_schema(self) -> None` - *Convenience for local development/tests. Prefer Alembic migrations in production.*
  - [`_authorize`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/extension.py#L38): `async _authorize(self, user: Any) -> Any`
  - [`mount`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/extension.py#L46): `mount(self, app: FastAPI) -> None` - *Mount protected HTML and JSON endpoints into the host FastAPI app.*
  - [`_serialize_run`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/extension.py#L109): `_serialize_run(run: RunRecord) -> dict[str, Any]`

#### [`src/fastapi_agent_observability/storage/database.py`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/storage/database.py) (33 lines)
- **Class** [`Database`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/storage/database.py#L10)``
  - [`__init__`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/storage/database.py#L11): `__init__(self, url: str)`
  - [`create_schema`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/storage/database.py#L20): `create_schema(self) -> None`
  - [`session`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/storage/database.py#L24): `session(self) -> Iterator[Session]`

#### [`src/fastapi_agent_observability/storage/models.py`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/storage/models.py) (29 lines)
- **Class** [`Base`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/storage/models.py#L6)`(DeclarativeBase)`
- **Class** [`RunRecord`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/storage/models.py#L10)`(Base)`

#### [`src/fastapi_agent_observability/tracing/langchain.py`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py) (79 lines)
- **Class** [`ObservabilityCallbackHandler`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L9)`(BaseCallbackHandler)` - *Capture common LangChain callback lifecycle events into the local trace store.*
  - [`__init__`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L12): `__init__(self, observability)`
  - [`on_chain_start`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L16): `on_chain_start(self, serialized, inputs, *, run_id, parent_run_id, name, **kwargs)`
  - [`on_tool_start`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L19): `on_tool_start(self, serialized, input_str, *, run_id, parent_run_id, name, **kwargs)`
  - [`on_llm_start`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L22): `on_llm_start(self, serialized, prompts, *, run_id, parent_run_id, name, **kwargs)`
  - [`on_chat_model_start`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L25): `on_chat_model_start(self, serialized, messages, *, run_id, parent_run_id, name, **kwargs)`
  - [`_start`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L28): `_start(self, run_type, serialized, inputs, run_id, parent_run_id, name)`
  - [`_trace_for_parent`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L39): `_trace_for_parent(self, parent_run_id, run_id)`
  - [`on_chain_end`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L44): `on_chain_end(self, outputs, *, run_id, **kwargs)`
  - [`on_tool_end`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L47): `on_tool_end(self, output, *, run_id, **kwargs)`
  - [`on_llm_end`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L50): `on_llm_end(self, response, *, run_id, **kwargs)`
  - [`on_chain_error`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L53): `on_chain_error(self, error, *, run_id, **kwargs)`
  - [`on_tool_error`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L56): `on_tool_error(self, error, *, run_id, **kwargs)`
  - [`on_llm_error`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L59): `on_llm_error(self, error, *, run_id, **kwargs)`
  - [`_finish`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L62): `_finish(self, run_id, outputs, error)`
- **Function** [`get_langchain_callback`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/langchain.py#L73): `get_langchain_callback(observability)` - *Return a callback handler for LangChain chains and LangGraph execution.*

#### [`src/fastapi_agent_observability/tracing/recorder.py`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py) (134 lines)
- **Class** [`RunHandle`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L32)`(AbstractContextManager)`
  - [`__init__`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L33): `__init__(self, tracer: 'Tracer', name: str, run_type: str, inputs: Any, *, parent_run_id: str | None, trace_id: str | None, run_id: str | None)`
  - [`__enter__`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L54): `__enter__(self)`
  - [`set_outputs`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L59): `set_outputs(self, outputs: Any) -> None`
  - [`set_error`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L62): `set_error(self, error: Any) -> None`
  - [`finish`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L65): `finish(self, status: str | None) -> None`
  - [`__exit__`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L83): `__exit__(self, exc_type, exc, tb)`
- **Class** [`Tracer`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L90)``
  - [`__init__`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L91): `__init__(self, database: Database, config: ObservabilityConfig)`
  - [`start_run`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L95): `start_run(self, name: str, run_type: str, inputs: Any, **ids) -> RunHandle`
  - [`trace`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L98): `trace(self, name: str, run_type: str)`
  - [`_persist_start`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L109): `_persist_start(self, handle: RunHandle) -> None`
  - [`_persist_finish`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L123): `_persist_finish(self, run_id, status, ended_at, latency_ms, outputs_json, error) -> None`
- **Function** [`_json`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/src/fastapi_agent_observability/tracing/recorder.py#L22): `_json(value: Any, max_chars: int) -> str`

#### [`tests/test_auth_dashboard.py`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/tests/test_auth_dashboard.py) (41 lines)
- **Function** [`test_dashboard_reuses_host_auth_and_blocks_non_admin`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/tests/test_auth_dashboard.py#L6): `test_dashboard_reuses_host_auth_and_blocks_non_admin(tmp_path)`
- **Function** [`test_dashboard_uses_existing_auth_dependency`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/tests/test_auth_dashboard.py#L27): `test_dashboard_uses_existing_auth_dependency(tmp_path)`

#### [`tests/test_tracing.py`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/tests/test_tracing.py) (47 lines)
- **Function** [`make_obs`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/tests/test_tracing.py#L5): `make_obs(tmp_path)`
- **Function** [`test_manual_trace_persists_success`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/tests/test_tracing.py#L15): `test_manual_trace_persists_success(tmp_path)`
- **Function** [`test_manual_trace_records_error_and_reraises`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/tests/test_tracing.py#L35): `test_manual_trace_records_error_and_reraises(tmp_path)`
