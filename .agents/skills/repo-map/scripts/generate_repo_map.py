#!/usr/bin/env python3
"""AST-based Repository Map Generator.

Extracts a concise, structured map of the codebase (directory hierarchy, classes,
methods, functions, signatures, docstrings, and templates) without loading full source files.
Saves the result to REPO_MAP.md to drastically reduce token consumption for AI agents.
"""

import ast
from pathlib import Path


def get_docstring_summary(node: ast.AST) -> str:
    """Return the first line of a docstring if present."""
    doc = ast.get_docstring(node)
    if not doc:
        return ""
    lines = [line.strip() for line in doc.splitlines() if line.strip()]
    return f" - *{lines[0]}*" if lines else ""


def format_arg(arg: ast.arg) -> str:
    """Format an argument with type annotation if present."""
    name = arg.arg
    if arg.annotation:
        return f"{name}: {ast.unparse(arg.annotation)}"
    return name


def format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Format a function signature string."""
    args = []
    # Positional args
    for a in node.args.posonlyargs:
        args.append(format_arg(a))
    if node.args.posonlyargs:
        args.append("/")
    for a in node.args.args:
        args.append(format_arg(a))
    if node.args.vararg:
        args.append(f"*{format_arg(node.args.vararg)}")
    elif node.args.kwonlyargs:
        args.append("*")
    for a in node.args.kwonlyargs:
        args.append(format_arg(a))
    if node.args.kwarg:
        args.append(f"**{format_arg(node.args.kwarg)}")

    sig = f"({', '.join(args)})"
    if node.returns:
        sig += f" -> {ast.unparse(node.returns)}"
    return sig


def parse_python_file(path: Path) -> dict:
    """Parse a python file into structured symbols using AST."""
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(path))
    except Exception as e:
        return {"error": str(e), "classes": [], "functions": []}

    classes = []
    functions = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases]
            base_str = f"({', '.join(bases)})" if bases else ""
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    prefix = "async " if isinstance(item, ast.AsyncFunctionDef) else ""
                    methods.append({
                        "name": item.name,
                        "line": item.lineno,
                        "sig": f"{prefix}{item.name}{format_signature(item)}",
                        "summary": get_docstring_summary(item),
                    })
            classes.append({
                "name": node.name,
                "line": node.lineno,
                "bases": base_str,
                "summary": get_docstring_summary(node),
                "methods": methods,
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "sig": f"{prefix}{node.name}{format_signature(node)}",
                "summary": get_docstring_summary(node),
            })

    total_lines = len(content.splitlines())
    return {
        "lines": total_lines,
        "classes": classes,
        "functions": functions,
        "docstring": get_docstring_summary(tree),
    }


def generate_repo_map(root_dir: Path) -> str:
    """Generate markdown repository map."""
    lines = [
        "# Repository Symbol & Architecture Map",
        "",
        "> **Notice for AI Agents:** Consult this map BEFORE opening or reading full source files.",
        "> It contains symbols, classes, method signatures, line numbers, and file hierarchies.",
        "> Update this map after modifying or adding code using `.agents/skills/repo-map/SKILL.md`.",
        "",
        "## File Hierarchy & Summary",
        "",
    ]

    # Directories to scan
    scan_dirs = ["src", "tests"]
    py_files = []
    other_files = []

    for d in scan_dirs:
        dir_path = root_dir / d
        if not dir_path.exists():
            continue
        for p in sorted(dir_path.rglob("*")):
            if p.is_file() and not any(part.startswith((".", "__")) for part in p.parts):
                rel = p.relative_to(root_dir)
                if p.suffix == ".py":
                    py_files.append((rel, p))
                else:
                    other_files.append((rel, p))

    # Add Non-Python files overview
    if other_files:
        lines.append("### Non-Python Assets & Templates")
        for rel, p in other_files:
            lines.append(f"- [`{rel}`](file://{p.resolve()}) ({p.stat().st_size} bytes)")
        lines.append("")

    # Add Python Files & Symbols
    lines.append("### Python Modules & Symbol Index")
    lines.append("")

    for rel, p in py_files:
        info = parse_python_file(p)
        file_link = f"[`{rel}`](file://{p.resolve()})"
        lines.append(f"#### {file_link} ({info.get('lines', 0)} lines){info.get('docstring', '')}")
        
        if info.get("error"):
            lines.append(f"- *Error parsing AST: {info['error']}*")
            continue

        if not info["classes"] and not info["functions"]:
            lines.append("- *(Module has top-level assignments/imports only)*")
            lines.append("")
            continue

        for cls in info["classes"]:
            cls_link = f"[`{cls['name']}`](file://{p.resolve()}#L{cls['line']})"
            lines.append(f"- **Class** {cls_link}`{cls['bases']}`{cls['summary']}")
            for m in cls["methods"]:
                m_link = f"[`{m['name']}`](file://{p.resolve()}#L{m['line']})"
                lines.append(f"  - {m_link}: `{m['sig']}`{m['summary']}")

        for fn in info["functions"]:
            fn_link = f"[`{fn['name']}`](file://{p.resolve()}#L{fn['line']})"
            lines.append(f"- **Function** {fn_link}: `{fn['sig']}`{fn['summary']}")

        lines.append("")

    return "\n".join(lines)


def main():
    root_dir = Path(__file__).resolve().parents[4]  # fastapi-agent-observability root
    output_path = root_dir / "REPO_MAP.md"
    repo_map_content = generate_repo_map(root_dir)
    output_path.write_text(repo_map_content, encoding="utf-8")
    print(f"Repository map successfully generated at: {output_path}")


if __name__ == "__main__":
    main()
