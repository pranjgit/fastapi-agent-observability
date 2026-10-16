# fastapi-agent-observability

An embeddable, local-first tracing dashboard for FastAPI applications using LangChain and LangGraph.
It mounts Jinja2/HTMX pages inside your app, uses the host application's authentication and admin
authorization, and stores traces in SQLite or PostgreSQL.

> MVP status: this is a starter implementation, not a drop-in replacement for LangSmith. Review
> authentication integration, data retention, redaction, migrations, and load behavior before production.

## Features

- Nested run/trace records with status, errors, timing, inputs and outputs.
- LangChain/LangGraph callback handler (`langchain-core` optional extra).
- Manual tracing context manager and decorator for non-LangChain code.
- Jinja2 dashboard and HTMX trace detail page.
- Host-provided `get_current_user` and `is_admin` callbacks; no second login system.
- SQLite by default; PostgreSQL via SQLAlchemy and the `postgres` extra.
- Best-effort tracing: application code can choose whether tracing failures are isolated.

## Install

```bash
pip install fastapi-agent-observability
# For LangChain/LangGraph callback integration:
pip install "fastapi-agent-observability[langchain]"
# For PostgreSQL:
pip install "fastapi-agent-observability[postgres]"
```

For local development from a checkout:

```bash
pip install -e ".[langchain,postgres,dev]"
pytest
```

## Mount in an existing FastAPI app

```python
from fastapi import FastAPI, Depends
from fastapi_agent_observability import (
    Observability, ObservabilityConfig, get_langchain_callback
)

app = FastAPI()

# These are your existing app functions/dependencies.
async def get_current_user():
    ...  # validate existing OAuth2/JWT/session and return trusted user

async def is_admin(user) -> bool:
    ...  # check your app's role/permission service

obs = Observability(
    ObservabilityConfig(
        app_name="my-agent-app",
        database_url="sqlite:///./observability.db",
        dashboard_path="/admin/observability",
    ),
    get_current_user=get_current_user,
    is_admin=is_admin,
)
obs.mount(app)

@app.post("/agent")
async def run_agent():
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Hello"}]},
        config={"callbacks": [get_langchain_callback(obs)]},
    )
    return result
```

The callback's constructor is deliberately simple; pass it to `config={"callbacks": [...]}` for
LangGraph or to a LangChain invoke call. For async graph invocation use `await graph.ainvoke(...)`.
LangChain callback coverage depends on the versions and integrations used.

### Auth contract

- `get_current_user` must validate the existing login/token and return a trusted user object.
- `is_admin(user)` must return a boolean. It may be synchronous or asynchronous.
- All dashboard and JSON routes run both checks. Unauthenticated behavior is delegated to the host
  dependency (for example, it may raise `401` or redirect to a login page); authenticated non-admins
  receive `403`.
- The library does not create OAuth clients, store passwords, or trust a role supplied by the browser.
- If your auth dependency expects `Depends(...)` or an `HTTPBearer` token, pass the dependency callable
  itself. FastAPI resolves it when the mounted endpoint declares `Depends(get_current_user)`.

### Storage and configuration

```python
ObservabilityConfig(
    app_name="my-agent-app",
    database_url="sqlite:///./observability.db",
    dashboard_path="/admin/observability",
    max_payload_chars=12000,
)
```

PostgreSQL example:

```python
database_url="postgresql+psycopg://obs_user:password@localhost:5432/observability"
```

Use a dedicated database/schema and a secret manager or environment variables for credentials.
`create_schema()` creates tables for the MVP. For managed production deployments, replace this with
Alembic migrations before upgrades. SQLite connections are configured for cross-thread use.

### Manual instrumentation

```python
with obs.tracer.start_run("retrieve_documents", run_type="tool", inputs={"query": q}) as run:
    docs = retriever.invoke(q)
    run.set_outputs({"count": len(docs)})
```

Or decorate a function:

```python
@obs.tracer.trace("calculate_plan", run_type="chain")
def calculate_plan(payload):
    return {"ok": True}
```

The context manager records failures and re-raises application exceptions. Do not put secrets,
credentials, raw PII, or large documents in inputs/outputs. Configure upstream redaction or pass
safe summaries. This MVP truncates serialized payloads but does not perform semantic PII detection.

### Dashboard

After mounting, open `/admin/observability`. The dashboard lists recent root traces and links to
hierarchical run details. The page uses HTMX from a CDN by default; for fully offline environments,
vendor HTMX locally and change the template script reference.

### Design notes / current limitations

- Synchronous SQLAlchemy writes are used for a simple, portable MVP. Under high concurrency, move
  persistence to a bounded queue/background worker or an async repository and define a drop policy.
- No built-in multi-tenant isolation, evaluation datasets, token/cost calculation, streaming event
  viewer, or OpenTelemetry exporter yet.
- The dashboard is intended for trusted admins. Inputs and outputs can contain sensitive data.
- The `langchain-core` callback captures common run lifecycle events; model-specific token usage is
  not normalized in this MVP.
- Pin and test dependency versions in your application. API compatibility may vary across LangChain versions.
