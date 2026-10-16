import time
from fastapi_agent_observability import Observability, ObservabilityConfig


def make_obs(tmp_path):
    obs = Observability(
        ObservabilityConfig(database_url=f"sqlite:///{tmp_path / 'test.db'}"),
        get_current_user=lambda: {"role": "admin"},
        is_admin=lambda user: user["role"] == "admin",
    )
    obs.create_schema()
    return obs


def test_manual_trace_persists_success(tmp_path):
    obs = make_obs(tmp_path)
    with obs.tracer.start_run("root", inputs={"q": "hello"}) as root:
        with obs.tracer.start_run("child", run_type="tool") as child:
            child.set_outputs({"ok": True})
        root.set_outputs({"answer": "world"})

    from sqlalchemy import select
    from fastapi_agent_observability.storage.models import RunRecord
    with obs.database.session() as session:
        rows = session.scalars(select(RunRecord)).all()
    assert len(rows) == 2
    root_row = next(row for row in rows if row.name == "root")
    child_row = next(row for row in rows if row.name == "child")
    assert root_row.status == "success"
    assert root_row.latency_ms is not None
    assert child_row.parent_run_id == root_row.id
    assert child_row.trace_id == root_row.trace_id


def test_manual_trace_records_error_and_reraises(tmp_path):
    obs = make_obs(tmp_path)
    try:
        with obs.tracer.start_run("broken"):
            raise ValueError("bad input")
    except ValueError:
        pass
    from sqlalchemy import select
    from fastapi_agent_observability.storage.models import RunRecord
    with obs.database.session() as session:
        row = session.scalars(select(RunRecord)).one()
    assert row.status == "error"
    assert "bad input" in row.error
