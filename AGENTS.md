<!-- AGENTS.md: Mirrors GEMINI.md for Antigravity and Agent configurations -->
# Antigravity Project Instructions: fastapi-agent-observability

Refer to [GEMINI.md](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/GEMINI.md) for full project architecture, invariants, and guidelines.

## Quick Summary
- **Project Root**: `/home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability`
- **Virtual Environment**: Located at `../.env`
- **Mandatory References**:
  - [`PROJECT_CONTEXT.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/PROJECT_CONTEXT.md)
  - [`CURRENT_STATE.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/CURRENT_STATE.md)
  - [`REPO_MAP.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/REPO_MAP.md)
- **Test Command**: `../.env/bin/pytest tests`
- **Lint Command**: `../.env/bin/ruff check .`
- **Update Protocol**: After modifying code, update `CURRENT_STATE.md` and regenerate `REPO_MAP.md` using `../.env/bin/python .agents/skills/repo-map/scripts/generate_repo_map.py`.
