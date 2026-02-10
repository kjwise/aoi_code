from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

HEADING = "## Public Interfaces"


def _public_function_signatures(src_root: Path) -> list[str]:
    signatures: set[str] = set()
    for path in sorted(src_root.rglob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
        for node in module.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                args = [a.arg for a in node.args.args]
                signatures.add(f"{node.name}({', '.join(args)})")
    return sorted(signatures)


def _extract_heading_block(doc_text: str, heading: str) -> str:
    lines = doc_text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.rstrip() == heading), None)
    if start is None:
        raise ValueError(f"Heading not found: {heading}")

    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return "".join(lines[start:end]).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a structured context object for a doc-sync request."
    )
    parser.add_argument("--src", type=Path, required=True, help="Source root (Terrain)")
    parser.add_argument("--doc", type=Path, required=True, help="Docs file (Map)")
    parser.add_argument("--out", type=Path, required=True, help="Output JSON path")
    parser.add_argument(
        "--task-id", default="doc_sync:public_interfaces", help="Task id for tracing"
    )
    args = parser.parse_args()

    doc_text = args.doc.read_text(encoding="utf-8")
    context = {
        "task_id": args.task_id,
        "target_file": str(args.doc),
        "allowed_heading": HEADING,
        "extracted_signatures": _public_function_signatures(args.src),
        "current_block": _extract_heading_block(doc_text, HEADING),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"[prep] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
