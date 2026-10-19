from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from fastapi_agent_observability import Observability, ObservabilityConfig


def test_dashboard_reuses_host_auth_and_blocks_non_admin(tmp_path):
    app = FastAPI()

    async def current_user():
        return {"role": "viewer"}

    def is_admin(user):
        return user["role"] == "admin"

    obs = Observability(
        ObservabilityConfig(database_url=f"sqlite:///{tmp_path / 'auth.db'}"),
        get_current_user=current_user,
        is_admin=is_admin,
    )
    obs.create_schema()
    obs.mount(app)
    client = TestClient(app)
    response = client.get("/admin/observability")
    assert response.status_code == 403


def test_dashboard_uses_existing_auth_dependency(tmp_path):
    app = FastAPI()

    async def current_user():
        raise HTTPException(status_code=401, detail="Existing auth required")

    obs = Observability(
        ObservabilityConfig(database_url=f"sqlite:///{tmp_path / 'auth2.db'}"),
        get_current_user=current_user,
        is_admin=lambda user: True,
    )
    obs.create_schema()
    obs.mount(app)
    response = TestClient(app).get("/admin/observability")
    assert response.status_code == 401
