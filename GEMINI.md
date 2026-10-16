# Antigravity Project Instructions: fastapi-agent-observability

## 1. Project Mission & Root Structure

- **Project Root**: `/home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability`
- **Virtual Environment**: Located at `../.env` (Python 3.12)
- **Objective**: Embeddable, local-first observability and tracing dashboard for FastAPI apps (LangChain, LangGraph, and manual python instrumentation).

---

## 2. Mandatory Pre-Implementation Reading (Token Efficiency Protocol)

To minimize token consumption and maintain code accuracy, **every agent MUST follow this sequence before making any changes or reading full code files**:

1. **Read [`PROJECT_CONTEXT.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/PROJECT_CONTEXT.md)**:
   - Scope, core requirements, architecture invariants, and non-goals.
2. **Read [`CURRENT_STATE.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/CURRENT_STATE.md)**:
   - Current module completion status, test health, and known limitations.
3. **Consult [`REPO_MAP.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/REPO_MAP.md)**:
   - Contains the complete AST symbol index, class definitions, function signatures, and exact line numbers.
   - **Do NOT** read full files or list extensive directories when `REPO_MAP.md` provides the exact target lines. Use targeted `view_file` ranges or `grep_search`.

---

## 3. Core Architectural Invariants

1. **Host-Delegated Authentication & Authorization**:
   - The library **must never** create its own authentication, session management, or login tables.
   - Authentication is delegated to host's `get_current_user` dependency via `Depends(self.get_current_user)`.
   - Authorization is delegated to the host's `is_admin(user)` callable (sync or async).
   - Authenticated non-admins receive `403 Forbidden`; unauthenticated requests are handled by host dependency (e.g., 401).
2. **Best-Effort & Isolated Tracing**:
   - Observability failures must **never** crash host business logic.
   - Exceptions inside `_persist_start` and `_persist_finish` are suppressed.
3. **Local-First & Lightweight**:
   - SQLite by default with cross-thread safety (`check_same_thread=False`).
   - PostgreSQL supported via SQLAlchemy 2.0 with the `postgres` extra (`psycopg`).
   - Server-rendered UI via Jinja2 + HTMX; no heavyweight client SPA frameworks.
4. **Data Safety & Payloads**:
   - Serialized inputs/outputs are truncated according to `max_payload_chars` (default 12,000, minimum 256).
   - Sensitive credentials, secret tokens, and raw PII should not be stored.

---

## 4. Directory Layout

```text
/home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/
├── .agents/                                # Antigravity customization root
│   ├── rules/                              # Workflow, coding & security rules
│   │   ├── workflow_and_token_efficiency.md# Token-saving and update protocols
│   │   ├── architecture.md                 # System architecture invariants
│   │   ├── auth_and_security.md            # Auth contract and security rules
│   │   └── coding_standards.md             # Python 3.10+, SQLAlchemy, FastAPI standards
│   └── skills/                             # Actionable runbooks & procedures
│       ├── repo-map/                       # Codebase AST map generator
│       ├── run-tests/                      # Pytest execution & verification
│       ├── lint-and-format/                # Ruff linting & formatting
│       └── verify-dashboard/               # Local test server & dashboard validation
├── PROJECT_CONTEXT.md                      # Scope, requirements, features, context
├── CURRENT_STATE.md                        # Current state, test status, limitations
├── REPO_MAP.md                             # AST symbol index (updated by repo-map skill)
├── pyproject.toml                          # Build config, dependencies & tools (Hatchling)
├── README.md                               # Project documentation & usage guide
├── .gitignore                              # Git exclusion rules
├── src/
│   └── fastapi_agent_observability/
│       ├── __init__.py                     # Public package exports
│       ├── config.py                       # ObservabilityConfig dataclass
│       ├── extension.py                    # Observability core class & router mounting
│       ├── storage/
│       │   ├── database.py                 # Database engine & session context manager
│       │   └── models.py                   # SQLAlchemy 2.0 RunRecord model & indexes
│       ├── tracing/
│       │   ├── recorder.py                 # Tracer, RunHandle context manager, contextvars
│       │   └── langchain.py                # LangChain / LangGraph callback handler
│       └── dashboard/
│           └── templates/
│               ├── index.html              # Traces list dashboard (Jinja2 + HTMX)
│               └── trace_detail.html       # Run execution hierarchy & payloads
└── tests/
    ├── test_auth_dashboard.py              # Auth delegation & permissions tests
    └── test_tracing.py                     # Context tracking & execution hierarchy tests
```

---

## 5. Development & Verification Commands

All commands should be run from this directory:

### Running Tests:
```bash
../.env/bin/pytest tests -v
```

### Linting and Formatting:
```bash
../.env/bin/ruff check .
../.env/bin/ruff format .
```

### Regenerating Repo Map:
```bash
../.env/bin/python .agents/skills/repo-map/scripts/generate_repo_map.py
```

---

## 6. Mandatory Post-Implementation Protocol

After completing any change, you **MUST**:
1. Run and pass all tests: `../.env/bin/pytest tests`
2. Run lint check: `../.env/bin/ruff check .`
3. Update [`CURRENT_STATE.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/CURRENT_STATE.md) with what was added, modified, or fixed.
4. Regenerate [`REPO_MAP.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/REPO_MAP.md) via `../.env/bin/python .agents/skills/repo-map/scripts/generate_repo_map.py`.
