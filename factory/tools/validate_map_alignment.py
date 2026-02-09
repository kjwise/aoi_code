from __future__ import annotations

import argparse
import ast
import re
import sys
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


def _map_signatures(doc_text: str) -> list[str]:
    lines = doc_text.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.strip() == "## Public Interfaces"),
        None,
    )
    if start is None:
        return []
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    block = "\n".join(lines[start:end])
    matches = re.findall(r"`([^`]+\([^`]*\))`", block)
    return sorted(set(matches))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MVF demo Validator: Map/Terrain sync."
    )
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--doc", type=Path, required=True)
    args = parser.parse_args()

    terrain = _public_function_signatures(args.src)
    map_sigs = _map_signatures(args.doc.read_text(encoding="utf-8"))

    missing = [s for s in terrain if s not in map_sigs]
    extra = [s for s in map_sigs if s not in terrain]

    if missing or extra:
        print("[validator] map_terrain_sync_fail", file=sys.stderr)
        if missing:
            print(f"  missing_in_map={missing}", file=sys.stderr)
        if extra:
            print(f"  extra_in_map={extra}", file=sys.stderr)
        return 1

    print("[validator] map_terrain_sync=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
