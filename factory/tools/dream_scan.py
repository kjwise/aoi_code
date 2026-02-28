from __future__ import annotations

import argparse
import ast
from pathlib import Path


def _function_complexity(fn: ast.FunctionDef) -> int:
    branch_nodes = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.BoolOp, ast.Match)
    return sum(1 for n in ast.walk(fn) if isinstance(n, branch_nodes))


def main() -> int:
    parser = argparse.ArgumentParser(description="Depth 0 Dream scan (read-only entropy signals).")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cc-threshold", type=int, default=30)
    parser.add_argument("--file-lines", type=int, default=500)
    args = parser.parse_args()

    signals: list[str] = []

    for path in sorted(args.root.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if len(text.splitlines()) > args.file_lines:
            signals.append(f"signal=file_too_large file={path} lines={len(text.splitlines())}")

        try:
            module = ast.parse(text)
        except SyntaxError:
            signals.append(f"signal=syntax_error file={path}")
            continue

        for node in module.body:
            if isinstance(node, ast.FunctionDef):
                cc = _function_complexity(node)
                if cc >= args.cc_threshold:
                    signals.append(
                        f"signal=complexity_high file={path} symbol={node.name} cc={cc}"
                    )

    for line in sorted(signals):
        print(line)

    if not signals:
        print("[dream] no signals")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
