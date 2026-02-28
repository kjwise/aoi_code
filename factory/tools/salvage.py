from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="List Salvage Protocol quarantine runs.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(".sdac/workflow-quarantine"),
        help="Quarantine root directory",
    )
    args = parser.parse_args()

    root = args.root
    if not root.exists():
        print("[salvage] none")
        return 0

    runs = sorted(p for p in root.iterdir() if p.is_dir())
    if not runs:
        print("[salvage] none")
        return 0

    for run in runs:
        diffs = sorted(run.glob("*.diff"))
        findings = sorted(run.glob("*.findings.json"))
        print(f"{run} diffs={len(diffs)} findings={len(findings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
