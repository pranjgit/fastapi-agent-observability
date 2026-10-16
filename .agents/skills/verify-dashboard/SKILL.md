---
name: verify-dashboard
description: Run a demo host FastAPI server and test the mounted observability dashboard and endpoints. Use this skill to verify UI rendering, HTMX integration, or manual tracing.
---

# Verify Dashboard Skill

This skill allows you to spin up a local FastAPI server mounting `fastapi-agent-observability` to verify dashboard rendering and tracing execution.

## Steps

### 1. Launch the demo server
Run the provided demo script:
```bash
../.env/bin/python .agents/skills/verify-dashboard/scripts/demo_server.py
```

### 2. Generate sample traces
In another terminal or via curl:
```bash
curl -X POST "http://127.0.0.1:8000/agent/run?admin=true"
```

### 3. Check dashboard response
- **Admin authorized (200 OK)**:
  ```bash
  curl -s "http://127.0.0.1:8000/admin/observability?admin=true" | grep -i "Observability"
  ```
- **Non-admin blocked (403 Forbidden)**:
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8000/admin/observability"
  ```
  Expected output: `403`
- **Unauthenticated blocked (401 Unauthorized)**:
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" -H "X-User-Role: anonymous" "http://127.0.0.1:8000/admin/observability"
  ```
  Expected output: `401`
