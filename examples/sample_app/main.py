from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from fastapi_agent_observability import Observability, ObservabilityConfig

from .agents import AgentWorkflows
from .auth import get_current_user, is_admin
from .config import settings

# 1. Initialize Observability extension
obs_config = ObservabilityConfig(
    app_name=settings.app_name,
    database_url=settings.database_url,
    dashboard_path=settings.dashboard_path,
    max_payload_chars=settings.max_payload_chars,
    default_page_size=settings.default_page_size,
)

obs = Observability(
    config=obs_config,
    get_current_user=get_current_user,
    is_admin=is_admin,
)

agents = AgentWorkflows(obs)


# 2. FastAPI Lifespan Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup
    obs.create_schema()
    yield


# 3. Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Sample FastAPI application instrumented with fastapi-agent-observability",
    version="1.0.0",
    lifespan=lifespan,
)

# 4. Mount Observability dashboard and API
obs.mount(app)


# ------------------------------------------------------------------------------
# Request / Response Models
# ------------------------------------------------------------------------------
class ResearchRequest(BaseModel):
    topic: str = Field(default="Autonomous AI Agent Architectures", description="Research subject")
    depth: str = Field(default="standard", description="'standard' or 'deep'")


class CalculationRequest(BaseModel):
    expression: str = Field(default="(125 * 4) + (350 / 5) - 20", description="Arithmetic math expression")
    target_unit: str = Field(default="standard", description="'standard', 'scientific', or 'percentage'")


class FailingTaskRequest(BaseModel):
    fail_step: str = Field(
        default="external_api",
        description="'external_api' (simulate 504) or 'llm_quota' (simulate 429)",
    )


class LoginRequest(BaseModel):
    api_key: str = Field(default="admin-secret-key-123", description="Admin or User API token")


# ------------------------------------------------------------------------------
# Agent Execution Endpoints
# ------------------------------------------------------------------------------
@app.post("/api/agents/research", tags=["AI Agents"])
async def trigger_research_agent(payload: ResearchRequest):
    """Run a multi-step research agent (Search Tool -> Ranker -> LLM Synthesis)."""
    try:
        result = agents.run_research(payload.topic, payload.depth)
        return {
            "status": "success",
            "message": "Research agent workflow completed successfully",
            "data": result,
            "trace_url": f"{settings.dashboard_path}/traces/{result['root_run_id']}?token={settings.admin_api_key}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/agents/calculate", tags=["AI Agents"])
async def trigger_calculation_agent(payload: CalculationRequest):
    """Run a calculation agent (Expression Parser -> Evaluation -> Unit Formatter)."""
    try:
        result = agents.run_calculation(payload.expression, payload.target_unit)
        return {
            "status": "success",
            "message": "Calculation completed",
            "data": result,
            "trace_url": f"{settings.dashboard_path}/traces/{result['root_run_id']}?token={settings.admin_api_key}",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/agents/failing-task", tags=["AI Agents"])
async def trigger_failing_agent(payload: FailingTaskRequest):
    """
    Run an agent that encounters a simulated downstream failure.
    Demonstrates automatic error capture and stack recording in observability traces.
    """
    try:
        agents.run_failing_task(payload.fail_step)
        return {"status": "unexpected_success"}
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error_captured",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "dashboard_note": (
                    f"This error was automatically recorded in the trace store. "
                    f"Check {settings.dashboard_path}?token={settings.admin_api_key} to view the trace."
                ),
            },
        )


@app.post("/api/agents/langchain", tags=["AI Agents"])
async def trigger_langchain_agent(query: str = "Explain agent telemetry"):
    """Run LangChain agent callback integration if langchain-core is available."""
    result = await agents.run_langchain_demo(query)
    return result


# ------------------------------------------------------------------------------
# Authentication Helper Endpoints (Cookie management for browser testing)
# ------------------------------------------------------------------------------
@app.post("/api/auth/login", tags=["Auth Helpers"])
async def login(payload: LoginRequest, response: Response):
    """
    Sets a browser session cookie for the token so you can click and view the
    dashboard without query parameters.
    """
    if payload.api_key not in (settings.admin_api_key, settings.user_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

    response.set_cookie(
        key="token",
        value=payload.api_key,
        httponly=True,
        samesite="lax",
    )
    role = "admin" if payload.api_key == settings.admin_api_key else "user"
    return {"status": "authenticated", "role": role}


@app.post("/api/auth/logout", tags=["Auth Helpers"])
async def logout(response: Response):
    """Clears the authentication cookie."""
    response.delete_cookie(key="token")
    return {"status": "logged_out"}


# ------------------------------------------------------------------------------
# Health & Status Endpoint
# ------------------------------------------------------------------------------
@app.get("/api/health", tags=["System"])
async def health_check():
    """Returns application status and trace count."""
    from sqlalchemy import func, select

    from fastapi_agent_observability.storage.models import RunRecord

    with obs.database.session() as session:
        trace_count = session.scalar(
            select(func.count(RunRecord.id)).where(RunRecord.parent_run_id.is_(None))
        ) or 0
        total_runs = session.scalar(select(func.count(RunRecord.id))) or 0

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "database_url": settings.database_url,
        "dashboard_path": settings.dashboard_path,
        "total_traces": trace_count,
        "total_spans": total_runs,
        "dev_mode_auto_admin": settings.dev_mode_auto_admin,
    }


# ------------------------------------------------------------------------------
# Interactive Home Test Console
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home_test_console(request: Request):
    """Interactive developer console to trigger agent runs and test observability."""
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{settings.app_name} · Developer Testbed</title>
  <style>
    :root {{
      --bg: #0b0f19;
      --card-bg: rgba(22, 30, 49, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --success: #10b981;
      --danger: #ef4444;
      --code-bg: #030712;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: radial-gradient(circle at top left, #1e1b4b 0%, #0b0f19 50%, #030712 100%);
      color: var(--text);
      min-height: 100vh;
      padding: 2.5rem 1.5rem;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    header {{ margin-bottom: 2.5rem; }}
    h1 {{ font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.02em; }}
    .subtitle {{ color: var(--text-muted); font-size: 1.05rem; }}
    
    .status-bar {{
      display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1.25rem;
    }}
    .badge {{
      display: inline-flex; align-items: center; gap: 0.5rem;
      background: rgba(255, 255, 255, 0.05); border: 1px solid var(--card-border);
      padding: 0.4rem 0.85rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 500;
    }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--success); }}
    
    .grid {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;
      margin-bottom: 2rem;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 1.5rem;
      backdrop-filter: blur(12px);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
      display: flex; flex-direction: column;
    }}
    .card h2 {{ font-size: 1.25rem; margin-bottom: 0.6rem; color: #fff; }}
    .card p {{ font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1.2rem; line-height: 1.45; }}
    
    label {{ display: block; font-size: 0.82rem; font-weight: 600; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.35rem; }}
    input, select {{
      width: 100%; padding: 0.65rem 0.85rem; background: #030712; border: 1px solid var(--card-border);
      border-radius: 8px; color: #fff; font-size: 0.9rem; margin-bottom: 1rem;
    }}
    input:focus, select:focus {{ outline: none; border-color: var(--accent); }}
    
    .btn {{
      display: inline-flex; justify-content: center; align-items: center; gap: 0.5rem;
      background: var(--accent); color: #fff; border: none; border-radius: 8px;
      padding: 0.7rem 1.2rem; font-size: 0.9rem; font-weight: 600; cursor: pointer;
      transition: background 0.15s ease, transform 0.1s ease; text-decoration: none;
    }}
    .btn:hover {{ background: var(--accent-hover); transform: translateY(-1px); }}
    .btn:active {{ transform: translateY(0); }}
    .btn-secondary {{ background: rgba(255, 255, 255, 0.08); border: 1px solid var(--card-border); color: #fff; }}
    .btn-secondary:hover {{ background: rgba(255, 255, 255, 0.15); }}
    .btn-danger {{ background: var(--danger); }}
    .btn-danger:hover {{ background: #dc2626; }}
    
    .actions-bar {{
      display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem;
      background: var(--card-bg); border: 1px solid var(--card-border);
      padding: 1.2rem; border-radius: 12px; align-items: center; justify-content: space-between;
    }}
    .actions-group {{ display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }}
    
    #console-box {{
      background: var(--code-bg); border: 1px solid var(--card-border);
      border-radius: 12px; padding: 1.2rem; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.85rem; min-height: 160px; max-height: 420px; overflow-y: auto; color: #e5e7eb;
      white-space: pre-wrap; word-break: break-word;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>AI Agent Observability Testbed</h1>
      <p class="subtitle">Sample FastAPI app integrating the <code>fastapi-agent-observability</code> embeddable tracing dashboard.</p>
      
      <div class="status-bar">
        <span class="badge"><span class="dot"></span> App: {settings.app_name}</span>
        <span class="badge"><span class="dot"></span> Storage: SQLite (<code>{settings.database_url}</code>)</span>
        <span class="badge"><span class="dot"></span> Mounted at: <code>{settings.dashboard_path}</code></span>
      </div>
    </header>

    <div class="actions-bar">
      <div>
        <strong style="display:block; font-size:1rem; margin-bottom:0.25rem;">Observability Dashboard Access</strong>
        <span style="color:var(--text-muted); font-size:0.85rem;">Requires admin role. Click direct authenticated link or test forbidden user.</span>
      </div>
      <div class="actions-group">
        <a class="btn" href="{settings.dashboard_path}?token={settings.admin_api_key}" target="_blank">
          Open Traces Dashboard (Admin) ↗
        </a>
        <a class="btn btn-secondary" href="{settings.dashboard_path}?token={settings.user_api_key}" target="_blank" title="Tests 403 Forbidden">
          Test Non-Admin (403) ↗
        </a>
        <a class="btn btn-secondary" href="/docs" target="_blank">
          Open Swagger /docs ↗
        </a>
      </div>
    </div>

    <div class="grid">
      <!-- 1. Research Agent Card -->
      <div class="card">
        <h2>1. Research Agent</h2>
        <p>Runs a 3-tier hierarchical trace: Root Chain &rarr; Search Tool &rarr; Content Ranker &rarr; LLM Synthesis.</p>
        <label>Topic</label>
        <input type="text" id="research-topic" value="Multi-Agent Systems & Tracing" />
        <label>Search Depth</label>
        <select id="research-depth">
          <option value="standard">Standard (3 documents)</option>
          <option value="deep">Deep (5 documents)</option>
        </select>
        <button class="btn" onclick="runResearch()">Execute Research Agent</button>
      </div>

      <!-- 2. Math Calculation Agent Card -->
      <div class="card">
        <h2>2. Math / Tool Agent</h2>
        <p>Demonstrates tool-level arithmetic evaluation and unit formatting spans.</p>
        <label>Expression</label>
        <input type="text" id="math-expression" value="(45 * 12) + 250 / 5" />
        <label>Formatting</label>
        <select id="math-unit">
          <option value="standard">Standard Decimal</option>
          <option value="scientific">Scientific Notation</option>
          <option value="percentage">Percentage</option>
        </select>
        <button class="btn" onclick="runCalculate()">Execute Math Agent</button>
      </div>

      <!-- 3. Failing Agent Card -->
      <div class="card">
        <h2>3. Error Handling Agent</h2>
        <p>Triggers a failure to verify that errors, exception types, and stack traces are captured in red.</p>
        <label>Failure Mode</label>
        <select id="fail-mode">
          <option value="external_api">Upstream 504 Gateway Timeout</option>
          <option value="llm_quota">LLM 429 Rate Limit Error</option>
        </select>
        <button class="btn btn-danger" onclick="runFailing()">Trigger Failing Task</button>
      </div>
    </div>

    <div class="card" style="margin-bottom: 2rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <h2>Execution Output & Trace Link</h2>
        <button class="btn btn-secondary" style="padding:0.35rem 0.75rem; font-size:0.8rem;" onclick="clearConsole()">Clear</button>
      </div>
      <div id="console-box">// Click any agent above to trigger execution. Output and trace links will appear here...</div>
    </div>
  </div>

  <script>
    const consoleBox = document.getElementById('console-box');

    function log(msg) {{
      consoleBox.innerText = typeof msg === 'object' ? JSON.stringify(msg, null, 2) : msg;
    }}

    function clearConsole() {{
      consoleBox.innerText = '// Console cleared.';
    }}

    async function runResearch() {{
      log('Executing Research Agent... (waiting for response)');
      const topic = document.getElementById('research-topic').value;
      const depth = document.getElementById('research-depth').value;
      try {{
        const res = await fetch('/api/agents/research', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ topic, depth }})
        }});
        const data = await res.json();
        log(data);
      }} catch (err) {{
        log('Error: ' + err.message);
      }}
    }}

    async function runCalculate() {{
      log('Executing Math Agent... (evaluating expression)');
      const expression = document.getElementById('math-expression').value;
      const target_unit = document.getElementById('math-unit').value;
      try {{
        const res = await fetch('/api/agents/calculate', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ expression, target_unit }})
        }});
        const data = await res.json();
        log(data);
      }} catch (err) {{
        log('Error: ' + err.message);
      }}
    }}

    async function runFailing() {{
      log('Triggering Failing Agent... (simulating upstream failure)');
      const fail_step = document.getElementById('fail-mode').value;
      try {{
        const res = await fetch('/api/agents/failing-task', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ fail_step }})
        }});
        const data = await res.json();
        log(data);
      }} catch (err) {{
        log('Error: ' + err.message);
      }}
    }}
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html)


# Entry point for direct execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
