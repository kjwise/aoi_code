from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure diff variance from a stochastic effector.")
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--doc", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1234, help="Base seed (run i uses seed+ i)")
    parser.add_argument("--mock", action="store_true", help="Use offline mock Effector variants")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run Validator against each applied candidate (temp file, no working tree writes)",
    )
    args = parser.parse_args()

    effector = "tools/stochastic_sync_public_interfaces.py"
    if args.mock:
        effector = "tools/mock_effector.py"

    cmd_base = [
        sys.executable,
        effector,
        "--src",
        str(args.src),
        "--doc",
        str(args.doc),
    ]

    unique: dict[str, int] = {}
    failures = 0
    rejects = 0
    passes = 0

    doc_path = args.doc
    tmpdir: str | None = None
    if args.validate:
        tmpdir = tempfile.mkdtemp(prefix="aoi_code_drift_")
        doc_path = Path(tmpdir) / args.doc.name

    for i in range(1, args.runs + 1):
        seed = args.seed + i

        if args.validate:
            shutil.copyfile(args.doc, doc_path)

        cmd = cmd_base[:-1] + [str(doc_path), "--seed", str(seed)]
        if args.validate:
            cmd.append("--apply")

        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            failures += 1
            continue

        h = _hash(p.stdout)
        unique.setdefault(h, i)

        if args.validate:
            v = subprocess.run(
                [
                    sys.executable,
                    "factory/tools/validate_map_alignment.py",
                    "--src",
                    str(args.src),
                    "--doc",
                    str(doc_path),
                ],
                capture_output=True,
                text=True,
            )
            if v.returncode == 0:
                passes += 1
            else:
                rejects += 1

    if tmpdir is not None:
        shutil.rmtree(tmpdir, ignore_errors=True)

    u = len(unique)
    n = args.runs
    d = u / n if n else 0.0

    tail = ""
    if args.validate:
        tail = f" passes={passes} rejects={rejects}"

    print(f"runs={n} unique_diffs={u} drift_coefficient={d:.3f} failures={failures}{tail}")
    if unique:
        examples = ", ".join(str(run) for run in sorted(unique.values())[:5])
        print(f"example_unique_runs={examples}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
