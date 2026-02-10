from __future__ import annotations

import argparse
import ast
import difflib
import random
from pathlib import Path


def _public_functions(src_root: Path) -> list[tuple[str, list[str]]]:
    functions: list[tuple[str, list[str]]] = []
    for path in sorted(src_root.rglob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
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


def _format_signature(name: str, args: list[str], style: str) -> str:
    if style == "plain":
        return f"{name}({', '.join(args)})"

    if style == "typed":
        typed_args = [f"{a}: {_guess_type(a)}" for a in args]
        return f"{name}({', '.join(typed_args)})"

    if style == "described":
        base = f"{name}({', '.join(args)})"
        description = name.replace("_", " ").capitalize() + "."
        return f"{base}` — {description}"  # caller will wrap backticks

    raise ValueError(f"unknown style: {style}")


def _rewrite_public_interfaces_block(doc_text: str, functions: list[tuple[str, list[str]]]) -> str:
    lines = doc_text.splitlines(keepends=True)
    heading = "## Public Interfaces"

    start = next((i for i, line in enumerate(lines) if line.rstrip() == heading), None)
    if start is None:
        raise ValueError(f"Heading not found: {heading}")

    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )

    styles = ["plain", "typed", "plain", "described"]
    items = functions[:]
    if random.random() < 0.4:
        random.shuffle(items)
    else:
        items.sort(key=lambda t: t[0])

    replacement = [heading + "\n", "\n"]
    for name, args in items:
        style = random.choice(styles)
        if style == "described":
            sig = _format_signature(name, args, "plain")
            desc = name.replace("_", " ").capitalize() + "."
            replacement.append(f"- `{sig}` — {desc}\n")
        elif style == "typed":
            typed_args = [f"{a}: {_guess_type(a)}" for a in args]
            replacement.append(f"- `{name}({', '.join(typed_args)})`\n")
        else:
            replacement.append(f"- `{name}({', '.join(args)})`\n")

        if random.random() < 0.6:
            replacement.append("\n")

    return "".join(lines[:start] + replacement + lines[end:])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Demo stochastic Effector: introduce formatting variance in a Map surface."
    )
    parser.add_argument("--src", type=Path, required=True, help="Source root (Terrain)")
    parser.add_argument("--doc", type=Path, required=True, help="Docs file (Map)")
    parser.add_argument("--apply", action="store_true", help="Apply the diff to the Map file")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (for reproducible drift)")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    before = args.doc.read_text(encoding="utf-8")
    after = _rewrite_public_interfaces_block(before, _public_functions(args.src))

    if before == after:
        print("[stochastic_effector] no drift detected")
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
        print(f"[stochastic_effector] applied patch to {args.doc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
