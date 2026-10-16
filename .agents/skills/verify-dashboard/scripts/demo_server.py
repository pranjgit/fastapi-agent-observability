"""Minimal demo host FastAPI application to verify fastapi-agent-observability."""

import sys
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi_agent_observability import Observability, ObservabilityConfig

app = FastAPI(title="Demo Host App with Observability")

# Simulated host authentication dependency
async def get_current_user(x_user_role: str | None = Header(default=None), admin: bool = Query(default=False)):
    if x_user_role == "anonymous":
        raise HTTPException(status_code=401, detail="Authentication required")
    role = "admin" if (admin or x_user_role == "admin") else "user"
    return {"id": "user-42", "role": role}

def is_admin(user: dict) -> bool:
    return user.get("role") == "admin"

# Configure and mount Observability
config = ObservabilityConfig(
    app_name="Demo Agent Service",
    database_url="sqlite:///./demo_observability.db",
    dashboard_path="/admin/observability",
)

obs = Observability(config, get_current_user=get_current_user, is_admin=is_admin)
obs.create_schema()
obs.mount(app)

@app.post("/agent/run")
async def run_agent(task: str = "summarize-report"):
    with obs.tracer.start_run("agent_coordinator", run_type="chain", inputs={"task": task}) as root:
        with obs.tracer.start_run("search_tool", run_type="tool", inputs={"query": task}) as tool_run:
            tool_run.set_outputs({"results": ["Doc 1", "Doc 2"]})
        
        with obs.tracer.start_run("llm_reasoning", run_type="llm", inputs={"prompt": f"Summarize {task}"}) as llm_run:
            llm_run.set_outputs({"response": "Summary output completed successfully."})

        result = {"status": "success", "task": task}
        root.set_outputs(result)
        return result

if __name__ == "__main__":
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is required to run the standalone demo server.")
        print("Install it using: ../.env/bin/pip install uvicorn")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🚀 Starting demo observability server on http://127.0.0.1:8000")
    print("📊 View dashboard: http://127.0.0.1:8000/admin/observability?admin=true")
    print("⚡ Trigger a trace: curl -X POST http://127.0.0.1:8000/agent/run?admin=true")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
