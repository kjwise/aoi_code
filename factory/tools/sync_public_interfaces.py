from __future__ import annotations

import argparse
import ast
import difflib
from pathlib import Path


def _public_function_signatures(src_root: Path) -> list[str]:
    signatures: set[str] = set()
    for path in sorted(src_root.rglob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
        for node in module.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                args = [a.arg for a in node.args.args]
                signatures.add(f"{node.name}({', '.join(args)})")
    return sorted(signatures)


def _rewrite_public_interfaces_block(doc_text: str, signatures: list[str]) -> str:
    lines = doc_text.splitlines(keepends=True)
    heading = "## Public Interfaces"

    start = next((i for i, line in enumerate(lines) if line.rstrip() == heading), None)
    if start is None:
        raise ValueError(f"Heading not found: {heading}")

    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )

    replacement = [heading + "\n", "\n"]
    for sig in signatures:
        replacement.append(f"- `{sig}`\n")
        replacement.append("\n")

    return "".join(lines[:start] + replacement + lines[end:])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MVF demo Effector: sync Public Interfaces in Map from Terrain."
    )
    parser.add_argument("--src", type=Path, required=True, help="Source root (Terrain)")
    parser.add_argument("--doc", type=Path, required=True, help="Docs file (Map)")
    parser.add_argument(
        "--apply", action="store_true", help="Apply the diff to the Map file"
    )
    args = parser.parse_args()

    signatures = _public_function_signatures(args.src)
    before = args.doc.read_text(encoding="utf-8")
    after = _rewrite_public_interfaces_block(before, signatures)

    if before == after:
        print("[effector] no drift detected (Map matches Terrain)")
        return 0

    diff = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile=str(args.doc),
        tofile=str(args.doc),
        lineterm="",
    )
    print("\n".join(diff))

    if args.apply:
        args.doc.write_text(after, encoding="utf-8")
        print(f"[effector] applied patch to {args.doc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
