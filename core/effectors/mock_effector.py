from __future__ import annotations

import argparse
import ast
import difflib
import sys
from pathlib import Path


def _public_functions(src_root: Path) -> list[tuple[str, list[str]]]:
    functions: list[tuple[str, list[str]]] = []
    for path in sorted(src_root.rglob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in module.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                functions.append((node.name, [a.arg for a in node.args.args]))
    return functions


def _guess_type(arg: str) -> str:
    a = arg.lower()
    if "country" in a:
        return "str"
    if a in {"amount", "rate", "tax", "income"}:
        return "float"
    if a in {"n", "count", "limit"}:
        return "int"
    return "Any"


def _rewrite_public_interfaces_block(
    doc_text: str, functions: list[tuple[str, list[str]]], variant: str
) -> str:
    lines = doc_text.splitlines(keepends=True)
    heading = "## Public Interfaces"

    start = next((i for i, line in enumerate(lines) if line.rstrip() == heading), None)
    if start is None:
        raise ValueError(f"Heading not found: {heading}")

    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )

    sigs = [f"{name}({', '.join(args)})" for name, args in sorted(functions)]

    if variant == "pass":
        out_sigs = sigs
    elif variant == "typed":
        typed = []
        for name, args in sorted(functions):
            typed_args = [f"{a}: {_guess_type(a)}" for a in args]
            typed.append(f"{name}({', '.join(typed_args)})")
        out_sigs = typed
    elif variant == "duplicates":
        out_sigs = sigs[:]
        if out_sigs:
            out_sigs.insert(0, out_sigs[0])
    elif variant == "missing":
        out_sigs = sigs[:-1] if sigs else []
    elif variant == "extra":
        out_sigs = sigs[:] + ["invented()"]
    else:
        raise ValueError(f"unknown variant: {variant}")

    replacement = [heading + "\n", "\n"]
    for sig in out_sigs:
        replacement.append(f"- `{sig}`\n")
        replacement.append("\n")

    return "".join(lines[:start] + replacement + lines[end:])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline mock Effector: emit a fixed set of diff variants (some valid, some invalid)."
    )
    parser.add_argument("--src", type=Path, required=True, help="Source root (Terrain)")
    parser.add_argument("--doc", type=Path, required=True, help="Docs file (Map)")
    parser.add_argument("--apply", action="store_true", help="Apply the diff to the Map file")
    parser.add_argument("--seed", type=int, default=0, help="Select variant deterministically")
    args = parser.parse_args()

    variants = ["pass", "typed", "duplicates", "missing", "extra"]
    variant = variants[args.seed % len(variants)]

    before = args.doc.read_text(encoding="utf-8")
    after = _rewrite_public_interfaces_block(before, _public_functions(args.src), variant=variant)

    if before == after:
        print("[mock_effector] no drift detected")
        return 0

    diff = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile=str(args.doc),
        tofile=str(args.doc),
        lineterm="",
    )
    print("\n".join(diff))
    print(f"[mock_effector] variant={variant}", file=sys.stderr)

    if args.apply:
        args.doc.write_text(after, encoding="utf-8")
        print(f"[mock_effector] applied patch to {args.doc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

