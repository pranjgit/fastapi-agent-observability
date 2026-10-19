import sys
from pathlib import Path

# Ensure repository root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from examples.sample_app.main import app, obs, settings
from fastapi_agent_observability.storage.models import RunRecord


@pytest.fixture(scope="module")
def client():
    # Run lifespan setup
    obs.create_schema()
    with TestClient(app) as test_client:
        yield test_client


def test_home_console_rendered(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Agent Observability Testbed" in response.text
    assert "Open Traces Dashboard (Admin)" in response.text


def test_research_agent_records_hierarchical_traces(client):
    response = client.post(
        "/api/agents/research",
        json={"topic": "FastAPI Agent Observability", "depth": "standard"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    root_run_id = data["data"]["root_run_id"]
    trace_id = data["data"]["trace_id"]
    assert root_run_id is not None
    assert trace_id is not None

    # Check database rows
    with obs.database.session() as session:
        runs = session.scalars(
            select(RunRecord).where(RunRecord.trace_id == trace_id)
        ).all()

    # Should contain root and 3 children: search, rank, llm
    assert len(runs) == 4
    names = {r.name for r in runs}
    assert "research_agent_workflow" in names
    assert "search_knowledge_base" in names
    assert "rank_and_filter" in names
    assert "llm_synthesize_report" in names

    root = next(r for r in runs if r.name == "research_agent_workflow")
    assert root.status == "success"
    assert root.parent_run_id is None
    assert root.latency_ms > 0
    assert "FastAPI Agent Observability" in root.inputs_json


def test_calculation_agent_records_traces(client):
    response = client.post(
        "/api/agents/calculate",
        json={"expression": "10 * 5 + 2", "target_unit": "standard"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["value"] == 52.0

    trace_id = data["data"]["trace_id"]
    with obs.database.session() as session:
        runs = session.scalars(
            select(RunRecord).where(RunRecord.trace_id == trace_id)
        ).all()
    assert len(runs) >= 2


def test_failing_task_captures_error(client):
    response = client.post(
        "/api/agents/failing-task",
        json={"fail_step": "external_api"},
    )
    assert response.status_code == 500
    data = response.json()
    assert data["status"] == "error_captured"
    assert "ConnectionResetError" in data["error_type"]

    # Verify that an error record was persisted in the database
    with obs.database.session() as session:
        error_runs = session.scalars(
            select(RunRecord).where(RunRecord.status == "error")
        ).all()
    assert len(error_runs) >= 1
    recent_error = error_runs[-1]
    assert "504 Gateway Timeout" in recent_error.error


def test_observability_auth_matrix(client):
    dashboard_path = settings.dashboard_path

    # 1. Unauthenticated request -> 401
    res_unauth = client.get(dashboard_path)
    assert res_unauth.status_code == 401

    # 2. Non-admin user token -> 403 Forbidden
    res_non_admin = client.get(
        dashboard_path,
        headers={"Authorization": f"Bearer {settings.user_api_key}"},
    )
    assert res_non_admin.status_code == 403
    assert "Administrator access required" in res_non_admin.text

    # 3. Admin token via query parameter -> 200 OK HTML
    res_admin_query = client.get(f"{dashboard_path}?token={settings.admin_api_key}")
    assert res_admin_query.status_code == 200
    assert "Observability" in res_admin_query.text

    # 4. Admin token via Header -> 200 OK API
    res_admin_api = client.get(
        f"{dashboard_path}/api/traces",
        headers={"Authorization": f"Bearer {settings.admin_api_key}"},
    )
    assert res_admin_api.status_code == 200
    api_data = res_admin_api.json()
    assert "items" in api_data
    assert len(api_data["items"]) >= 1

    # 5. Admin trace detail view
    first_trace_id = api_data["items"][0]["id"]
    res_detail = client.get(
        f"{dashboard_path}/traces/{first_trace_id}",
        headers={"X-API-Key": settings.admin_api_key},
    )
    assert res_detail.status_code == 200
    assert "Execution hierarchy" in res_detail.text


def test_auth_login_cookie(client):
    # Log in via cookie endpoint
    login_res = client.post(
        "/api/auth/login",
        json={"api_key": settings.admin_api_key},
    )
    assert login_res.status_code == 200
    assert login_res.json()["role"] == "admin"

    # Now request dashboard with cookie automatically sent
    res = client.get(settings.dashboard_path)
    assert res.status_code == 200

    # Log out
    client.post("/api/auth/logout")


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_traces"] >= 1
