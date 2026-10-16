# Rule: Coding Standards & Best Practices

## 1. Python & Typing
- Target Python 3.10+.
- Use modern type annotations:
  - Union: `str | None` instead of `Optional[str]`
  - Collections: `list[str]`, `dict[str, Any]` from builtins, `Callable`, `Iterator` from `collections.abc`
  - Explicit function return types (`-> None`, `-> dict[str, Any]`, etc.)
- Use Ruff (`line-length = 100`) for formatting and linting (`../.env/bin/ruff check .`).

## 2. FastAPI Patterns
- Use `APIRouter` for grouping endpoints.
- Endpoints return `HTMLResponse` for template views or standard Python dicts/Pydantic models for JSON APIs.
- Keep route handlers asynchronous (`async def`) when calling async auth functions or template rendering.

## 3. SQLAlchemy 2.0 ORM
- Use `DeclarativeBase` and `Mapped[...]` with `mapped_column(...)`.
- Use the modern 2.0 query syntax:
  - `session.scalars(select(RunRecord).where(...))`
  - `session.get(RunRecord, run_id)`
- All sessions must be acquired via the context manager (`with self.database.session() as session:`).

## 4. Tracing & ContextVars
- Store active run IDs and trace IDs in Python's native `contextvars`:
  - `_current_run_id`
  - `_current_trace_id`
- Always capture the previous token when `.set(...)` is called and `.reset(token)` on context exit to guarantee clean cleanup even if exceptions occur.
