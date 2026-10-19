# Sample FastAPI Agent Observability Application

This directory contains a complete, production-ready sample FastAPI application integrating **`fastapi-agent-observability`**.

It demonstrates:
- Mounting the embeddable observability dashboard (`/admin/observability`) inside a host FastAPI app.
- Host-delegated authentication and authorization (`get_current_user` and `is_admin`).
- Multi-step hierarchical agent tracing (Root Chain &rarr; Tools &rarr; LLM calls) with inputs, outputs, and latencies.
- Automatic capture and visualization of agent runtime errors.
- Optional integration with `langchain-core` callbacks (`get_langchain_callback(obs)`).
- An interactive developer testbed console at `/`.

---

## 🚀 Quickstart

### 1. Configure Environment Variables

Edit `.env` (or copy from `.env.example`):

```bash
# Available in this directory:
cp .env.example .env
```

Key variables:
- `ADMIN_API_KEY`: Secret key for accessing the admin dashboard (default: `admin-secret-key-123`).
- `USER_API_KEY`: Secret key for a standard non-admin user to test `403 Forbidden` behavior (default: `user-secret-key-456`).
- `DATABASE_URL`: Tracing SQLite database (default: `sqlite:///./observability.db`) or PostgreSQL.
- `DASHBOARD_PATH`: Dashboard prefix (default: `/admin/observability`).
- `DEV_MODE_AUTO_ADMIN`: Set to `true` if you want local development without any auth header.

### 2. Start the Server

From the repository root or this directory, using the project virtual environment:

```bash
# From workspace root:
.env/bin/uvicorn examples.sample_app.main:app --reload --port 8000
```

### 3. Open the Interactive Test Console

Navigate to:
👉 **`http://127.0.0.1:8000/`**

From this interactive page, you can:
- Execute the **Research Agent** (hierarchical search + summarization).
- Execute the **Math / Calculation Agent** (tool execution and formatting).
- Trigger the **Failing Agent** (verifying error capture in the trace store).
- Click **Open Traces Dashboard (Admin)** to view all traces and drill into span hierarchies.
- Click **Test Non-Admin (403)** to verify role-based access control.
- Open the interactive API documentation at **`/docs`**.

---

## 🔒 Authentication & Permissions

The library completely offloads authentication to the host app. In this sample:
- Dashboard routes (`/admin/observability`, `/admin/observability/traces/{run_id}`, `/admin/observability/api/traces`) enforce admin access.
- You can pass authentication in 4 ways:
  1. **Header**: `Authorization: Bearer admin-secret-key-123`
  2. **Header**: `X-API-Key: admin-secret-key-123`
  3. **Query parameter**: `?token=admin-secret-key-123`
  4. **Cookie**: Log in via `POST /api/auth/login` with `{"api_key": "admin-secret-key-123"}`

---

## 🧪 Testing with cURL

### Run Research Agent
```bash
curl -X POST http://127.0.0.1:8000/api/agents/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Autonomous AI Agents", "depth": "standard"}'
```

### Run Calculation Agent
```bash
curl -X POST http://127.0.0.1:8000/api/agents/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "(50 * 4) + 12", "target_unit": "standard"}'
```

### Fetch Recorded Traces (JSON API)
```bash
curl -X GET http://127.0.0.1:8000/admin/observability/api/traces \
  -H "Authorization: Bearer admin-secret-key-123"
```

### Test 403 Forbidden Access (Non-admin)
```bash
curl -i -X GET http://127.0.0.1:8000/admin/observability \
  -H "Authorization: Bearer user-secret-key-456"
```
*(Returns `HTTP/1.1 403 Forbidden`)*
