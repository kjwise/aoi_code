from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _allocate_run_dir(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    base = root / f"run_{_run_id()}"
    if not base.exists():
        base.mkdir()
        return base

    # Collision is unlikely, but make it deterministic if it happens.
    for i in range(1, 1000):
        d = Path(f"{base}_{i:03d}")
        if not d.exists():
            d.mkdir()
            return d

    raise RuntimeError("failed to allocate quarantine directory")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the MVF v0 loop (sync + validate) and salvage near-misses on failure."
    )
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--doc", type=Path, required=True)
    parser.add_argument(
        "--effector",
        type=str,
        default="tools/sync_public_interfaces.py",
        help="Effector script path (called with --src/--doc/--apply)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional seed forwarded to effectors that support --seed",
    )
    parser.add_argument(
        "--quarantine-dir",
        type=Path,
        default=Path(".sdac/workflow-quarantine"),
        help="Where failed attempts are stored",
    )
    args = parser.parse_args()

    before = args.doc.read_text(encoding="utf-8")

    effector_cmd = [
        sys.executable,
        args.effector,
        "--src",
        str(args.src),
        "--doc",
        str(args.doc),
        "--apply",
    ]
    if args.seed is not None:
        effector_cmd += ["--seed", str(args.seed)]

    effector = subprocess.run(
        effector_cmd,
        capture_output=True,
        text=True,
    )
    if effector.stdout:
        print(effector.stdout, end="" if effector.stdout.endswith("\n") else "\n")
    if effector.stderr:
        print(effector.stderr, file=sys.stderr, end="" if effector.stderr.endswith("\n") else "\n")

    validate_plain = subprocess.run(
        [
            sys.executable,
            "tools/validate_map_alignment.py",
            "--src",
            str(args.src),
            "--doc",
            str(args.doc),
        ],
        capture_output=True,
        text=True,
    )
    if validate_plain.stdout:
        print(
            validate_plain.stdout,
            end="" if validate_plain.stdout.endswith("\n") else "\n",
        )
    if validate_plain.stderr:
        print(
            validate_plain.stderr,
            file=sys.stderr,
            end="" if validate_plain.stderr.endswith("\n") else "\n",
        )

    if effector.returncode == 0 and validate_plain.returncode == 0:
        return 0

    findings = subprocess.run(
        [
            sys.executable,
            "tools/validate_map_alignment.py",
            "--src",
            str(args.src),
            "--doc",
            str(args.doc),
            "--json",
        ],
        capture_output=True,
        text=True,
    )

    # Restore the Map surface (safe by default) and salvage evidence for humans.
    args.doc.write_text(before, encoding="utf-8")

    run_dir = _allocate_run_dir(args.quarantine_dir)
    (run_dir / "attempt-1.diff").write_text(effector.stdout or "", encoding="utf-8")
    (run_dir / "attempt-1.findings.json").write_text(findings.stdout or "[]\n", encoding="utf-8")

    if effector.stderr:
        (run_dir / "attempt-1.effector.stderr.txt").write_text(effector.stderr, encoding="utf-8")
    if validate_plain.stderr:
        (run_dir / "attempt-1.validator.stderr.txt").write_text(
            validate_plain.stderr, encoding="utf-8"
        )

    print(f"[salvage] stored failed attempt under {run_dir}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

