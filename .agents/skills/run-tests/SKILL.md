---
name: run-tests
description: Run the pytest suite for fastapi-agent-observability using the virtual environment. Use this skill whenever verifying code changes, testing authentication integration, or testing trace persistence.
---

# Run Tests Skill

This skill executes the test suite for `fastapi-agent-observability` from the project root using the virtual environment at `../.env`.

## Commands

### 1. Run all tests
```bash
../.env/bin/pytest tests -v
```

### 2. Run specific test files
- **Auth and Dashboard endpoints**:
  ```bash
  ../.env/bin/pytest tests/test_auth_dashboard.py -v
  ```
- **Tracing context and hierarchy**:
  ```bash
  ../.env/bin/pytest tests/test_tracing.py -v
  ```

## Verification Checklist
- [ ] All tests exit with code `0`.
- [ ] Temporary databases created via `tmp_path` are cleaned up.
- [ ] No regression in status codes (`401` for unauthenticated, `403` for non-admin, `200` for admin).
