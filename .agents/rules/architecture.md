# Rule: Architectural Invariants

## Core Principles

1. **Project Root & Scope**:
   - The project root is `/home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability`.
   - The virtual environment is located at `../.env`.
   - Always run commands relative to this project root directory.

2. **Embeddable Library, Not a Standalone Server**:
   - `fastapi-agent-observability` is imported and mounted into a host FastAPI application via `obs.mount(app)`.
   - Never assume the library controls the main FastAPI app lifecycle, server binding, or deployment setup.

3. **Host-Delegated Authentication & Authorization**:
   - The library must never introduce user databases, token issuing, session cookies, or password management.
   - Authentication must rely on the host-provided `get_current_user` dependency.
   - Authorization must rely on the host-provided `is_admin(user)` callable.
   - Non-admin authenticated users must receive `403 Forbidden`.
   - Unauthenticated requests must be handled naturally by the host's dependency (e.g. `401 Unauthorized` or redirect).

4. **Telemetry Isolation & Non-Interference**:
   - Tracing must follow a best-effort failure isolation model.
   - Telemetry persistence errors inside `_persist_start` and `_persist_finish` must never fail the underlying business execution.
   - Application errors within traced blocks must be recorded in the trace status/error field and re-raised to preserve standard application exception behavior.

5. **Payload Truncation & Memory Safety**:
   - Inputs and outputs must be JSON-serialized and truncated to `config.max_payload_chars`.
   - Large blobs (e.g. full vector documents, binary data) must not be stored in plaintext database fields without truncation.
