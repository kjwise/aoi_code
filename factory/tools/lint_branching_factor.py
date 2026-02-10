from __future__ import annotations

import argparse
from pathlib import Path


def _count_headings(md: Path, prefix: str = "### ") -> int:
    return sum(1 for line in md.read_text(encoding="utf-8").splitlines() if line.startswith(prefix))


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint basic branching-factor heuristics (demo).")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--max-children", type=int, default=10)
    parser.add_argument("--max-headings", type=int, default=12)
    args = parser.parse_args()

    warnings = 0

    for d in sorted(p for p in args.root.rglob("*") if p.is_dir()):
        children = [c for c in d.iterdir() if c.name not in {"__pycache__", ".git"}]
        if len(children) > args.max_children:
            print(f"[warn] branching_factor_too_high path={d} children={len(children)}")
            warnings += 1

    for md in sorted(args.root.rglob("*.md")):
        h = _count_headings(md)
        if h > args.max_headings:
            print(f"[warn] doc_fanout_too_high file={md} headings={h}")
            warnings += 1

    if warnings == 0:
        print("[OK] branching factor within heuristics")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
