from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read_value(path: Path) -> float:
    data = json.loads(path.read_text(encoding="utf-8"))
    return float(data["value"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Check monotonic ratchets against baselines (demo).")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    ratchets = config.get("ratchets", {})

    failures: list[str] = []

    for name, spec in ratchets.items():
        direction = spec["direction"]
        tolerance = float(spec.get("tolerance", 0.0))
        baseline = _read_value(Path(spec["baseline_file"]))
        current = _read_value(Path(spec["current_file"]))

        if direction == "up":
            if current < baseline - tolerance:
                failures.append(
                    f"ratchet_violation metric={name} direction=up baseline={baseline} current={current} tol={tolerance}"
                )
        elif direction == "down":
            if current > baseline + tolerance:
                failures.append(
                    f"ratchet_violation metric={name} direction=down baseline={baseline} current={current} tol={tolerance}"
                )
        else:
            failures.append(f"unknown_direction metric={name} direction={direction}")

    if failures:
        for f in failures:
            print(f"[ratchet] FAIL {f}")
        return 1

    print("[ratchet] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
