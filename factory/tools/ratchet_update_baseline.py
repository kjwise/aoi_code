from __future__ import annotations

import argparse
import shutil
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Update ratchet baselines from current metrics (human-only).")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--yes", action="store_true", help="Actually write baselines")
    args = parser.parse_args()

    if not args.yes:
        raise SystemExit("Refusing to update baselines without --yes")

    config = json.loads(args.config.read_text(encoding="utf-8"))
    ratchets = config.get("ratchets", {})

    for name, spec in ratchets.items():
        src = Path(spec["current_file"])
        dst = Path(spec["baseline_file"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"[ratchet] baseline_updated metric={name} file={dst}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
