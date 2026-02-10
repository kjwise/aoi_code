from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure diff variance from a stochastic effector.")
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--doc", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1234, help="Base seed (run i uses seed+ i)")
    args = parser.parse_args()

    cmd_base = [
        sys.executable,
        "factory/tools/stochastic_sync_public_interfaces.py",
        "--src",
        str(args.src),
        "--doc",
        str(args.doc),
    ]

    unique: dict[str, int] = {}
    failures = 0

    for i in range(1, args.runs + 1):
        cmd = cmd_base + ["--seed", str(args.seed + i)]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            failures += 1
            continue
        h = _hash(p.stdout)
        unique.setdefault(h, i)

    u = len(unique)
    n = args.runs
    d = u / n if n else 0.0

    print(f"runs={n} unique_diffs={u} drift_coefficient={d:.3f} failures={failures}")
    if unique:
        examples = ", ".join(str(run) for run in sorted(unique.values())[:5])
        print(f"example_unique_runs={examples}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
