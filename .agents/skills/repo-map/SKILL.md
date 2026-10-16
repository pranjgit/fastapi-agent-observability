---
name: repo-map
description: Regenerate the repository AST symbol map (REPO_MAP.md). Use this skill after completing feature implementations or code modifications so subsequent agents can navigate code without re-reading files.
---

# Repo Map Skill

This skill scans the project using AST parsing and regenerates [`REPO_MAP.md`](file:///home/pranjal/projects/fastapi-agent-observability/fastapi-agent-observability/REPO_MAP.md) at the project root.

## Usage

Run the generator script using the virtual environment:
```bash
../.env/bin/python .agents/skills/repo-map/scripts/generate_repo_map.py
```

## When to run:
- **After every feature addition or modification**: Ensures the symbol index, function signatures, and line numbers in `REPO_MAP.md` remain strictly accurate.
- **Before ending any implementation turn**: Part of the mandatory post-change update protocol.
