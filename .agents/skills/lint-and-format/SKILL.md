---
name: lint-and-format
description: Run Ruff checks and formatting across the fastapi-agent-observability codebase. Use this skill before committing or completing tasks to ensure code quality.
---

# Lint and Format Skill

This skill checks and auto-formats Python code using `ruff` according to the workspace configurations.

## Commands

### 1. Check code style and common issues
```bash
../.env/bin/ruff check .
```

### 2. Auto-fix safe issues
```bash
../.env/bin/ruff check --fix .
```

### 3. Format code
```bash
../.env/bin/ruff format .
```

## Note on FastAPI B008
FastAPI uses `Depends(...)` in function argument defaults by design. When configuring `ruff`, `B008` should be ignored for FastAPI route handlers.
