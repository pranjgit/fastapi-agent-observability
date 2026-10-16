# Rule: Workflow & Token Efficiency

## 1. Token-Efficiency Principles (Low Token Consumption)

To optimize cost, context window space, and speed, every agent working in this repository MUST follow these rules:

1. **Check Maps & State Before Files**:
   - **Step 1**: Read [`CURRENT_STATE.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/CURRENT_STATE.md) to understand current implementation status, limitations, and invariants.
   - **Step 2**: Read [`REPO_MAP.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/REPO_MAP.md) to locate exact classes, functions, line numbers, and file relationships.
   - **Do NOT** blindly read entire source files or run exhaustive directory scans when `REPO_MAP.md` already contains the symbol signatures and line numbers.

2. **Targeted Reading with Line Ranges**:
   - When inspecting code, specify `StartLine` and `EndLine` using the line numbers obtained from `REPO_MAP.md` or `grep_search`.
   - Never view entire files over 100 lines if you only need a single method or class definition.

3. **Grep Before Listing**:
   - Use `grep_search` with specific identifiers or symbols rather than traversing folders.

---

## 2. Mandatory Post-Implementation Updates

After completing any feature implementation, refactor, or bugfix:
1. **Update [`CURRENT_STATE.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/CURRENT_STATE.md)**:
   - Reflect changes to features, test counts, or known issues.
2. **Regenerate [`REPO_MAP.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/REPO_MAP.md)**:
   - Execute the repo map generator:
     ```bash
     ../.env/bin/python .agents/skills/repo-map/scripts/generate_repo_map.py
     ```
3. **Run Tests**:
   - Execute the test suite:
     ```bash
     ../.env/bin/pytest tests
     ```
