# Rule: Authentication & Security Guidelines

## 1. Authentication Contract
- The `Observability` constructor accepts `get_current_user` and `is_admin`.
- In all endpoints registered by `Observability.mount()`, authenticate via:
  ```python
  user: Any = Depends(self.get_current_user)
  ```
- Verify authorization using `self._authorize(user)`:
  ```python
  allowed = self.is_admin(user)
  if inspect.isawaitable(allowed):
      allowed = await allowed
  if not allowed:
      raise HTTPException(status_code=403, detail="Administrator access required")
  ```

## 2. Security Boundaries & Data Hygiene
- **Admin Only**: The dashboard (`/admin/observability`) and traces API (`/admin/observability/api/traces`) expose sensitive internal state (prompts, responses, function arguments, error traces). Both HTML and JSON endpoints must enforce admin authorization.
- **Credential Protection**: Application instrumentation must avoid capturing passwords, bearer tokens, API keys, or raw PII in trace inputs/outputs.
- **SQL Injection Prevention**: Never use raw string formatting for queries. Always use SQLAlchemy 2.0 type-safe expressions (`select()`, `where()`).
- **Database Connection Safety**: SQLite connections must enable `check_same_thread=False` to prevent thread affinity crashes under FastAPI's async worker threads.
