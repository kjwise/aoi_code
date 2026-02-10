from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


def _md_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            stripped = line.lstrip("#").strip()
            if stripped:
                headings.append(stripped)
    return headings


def _imports(module: ast.AST) -> list[str]:
    imported: list[str] = []
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            imported.extend([n.name for n in node.names])
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    return sorted(set(imported))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a tiny context graph snapshot (demo).")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    nodes: list[dict] = []
    edges: list[dict] = []

    for path in sorted(args.root.rglob("*")):
        if path.is_dir():
            continue

        if path.suffix not in {".py", ".md"}:
            continue

        rel = str(path)
        nodes.append({"id": rel, "kind": "file", "path": rel})

        if path.suffix == ".py":
            module = ast.parse(path.read_text(encoding="utf-8"))
            for node in module.body:
                if isinstance(node, ast.FunctionDef):
                    sym_id = f"{rel}:{node.name}"
                    nodes.append({"id": sym_id, "kind": "symbol", "path": rel, "name": node.name})
                    edges.append({"src": rel, "dst": sym_id, "kind": "contains"})

            for mod in _imports(module):
                edges.append({"src": rel, "dst": mod, "kind": "imports"})

        if path.suffix == ".md":
            for heading in _md_headings(path.read_text(encoding="utf-8")):
                sec_id = f"{rel}#{heading}"
                nodes.append({"id": sec_id, "kind": "doc_section", "path": rel, "name": heading})
                edges.append({"src": rel, "dst": sec_id, "kind": "contains"})

    graph = {"root": str(args.root), "nodes": nodes, "edges": edges}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[graph] wrote {args.out} nodes={len(nodes)} edges={len(edges)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
