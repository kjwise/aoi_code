from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import Counter
from pathlib import Path

PUBLIC_INTERFACES_HEADING = "## Public Interfaces"

_SIGNATURE_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*\((?:[A-Za-z_][A-Za-z0-9_]*(?:,\s*[A-Za-z_][A-Za-z0-9_]*)*)?\)$"
)


def _python_files(src_root: Path) -> list[Path]:
    return sorted(src_root.rglob("*.py"))


def _public_function_signatures(src_root: Path) -> list[str]:
    """Extract public top-level function signatures via AST.

    The Validator measures independently from the Effector (which uses a lightweight
    text extractor). This reduces correlated failure modes.
    """

    signatures: list[str] = []
    errors: list[str] = []

    for path in _python_files(src_root):
        module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in module.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name.startswith("_"):
                continue

            if node.args.posonlyargs or node.args.kwonlyargs or node.args.vararg or node.args.kwarg:
                errors.append(f"{path}: unsupported signature shape for MVF demo: {node.name}")
                continue

            args = [a.arg for a in node.args.args]
            sig = f"{node.name}({', '.join(args)})"
            if _SIGNATURE_RE.fullmatch(sig) is None:
                errors.append(f"{path}: malformed signature: {sig!r}")
                continue

            signatures.append(sig)

    if errors:
        raise ValueError("\n".join(errors))

    counts = Counter(signatures)
    dupes = sorted(sig for sig, count in counts.items() if count > 1)
    if dupes:
        raise ValueError(f"duplicate signatures in Terrain: {dupes}")

    return sorted(signatures)


def _map_signatures(doc_text: str) -> list[str]:
    lines = doc_text.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.strip() == PUBLIC_INTERFACES_HEADING),
        None,
    )
    if start is None:
        return []
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    block = "\n".join(lines[start:end])
    return re.findall(r"`([^`]+\([^`]*\))`", block)


def main() -> int:
    parser = argparse.ArgumentParser(description="MVF demo Validator: Map/Terrain sync.")
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--doc", type=Path, required=True)
    args = parser.parse_args()

    try:
        terrain = _public_function_signatures(args.src)
    except ValueError as e:
        print("[validator] map_terrain_sync_fail", file=sys.stderr)
        for line in str(e).splitlines():
            print(f"  {line}", file=sys.stderr)
        return 1

    map_sigs_raw = _map_signatures(args.doc.read_text(encoding="utf-8"))
    invalid_map_sigs = [s for s in map_sigs_raw if _SIGNATURE_RE.fullmatch(s) is None]
    if invalid_map_sigs:
        print("[validator] map_terrain_sync_fail", file=sys.stderr)
        print(f"  malformed_signatures_in_map={invalid_map_sigs}", file=sys.stderr)
        return 1

    map_counts = Counter(map_sigs_raw)
    map_dupes = sorted(sig for sig, count in map_counts.items() if count > 1)
    if map_dupes:
        print("[validator] map_terrain_sync_fail", file=sys.stderr)
        print(f"  duplicate_signatures_in_map={map_dupes}", file=sys.stderr)
        return 1

    map_sigs = sorted(map_sigs_raw)

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
