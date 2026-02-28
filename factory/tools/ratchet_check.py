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
    parser.add_argument("--json", action="store_true", help="Emit structured findings JSON")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    ratchets = config.get("ratchets", {})

    findings: list[dict[str, object]] = []

    for name, spec in ratchets.items():
        direction = spec["direction"]
        tolerance = float(spec.get("tolerance", 0.0))
        baseline = _read_value(Path(spec["baseline_file"]))
        current = _read_value(Path(spec["current_file"]))

        if direction == "up":
            if current < baseline - tolerance:
                findings.append(
                    {
                        "file_path": str(args.config),
                        "error_code": "ratchet_violation",
                        "metric": name,
                        "direction": "up",
                        "baseline": baseline,
                        "current": current,
                        "tolerance": tolerance,
                        "suggested_fix": "If the drop is intended, update the baseline (human-only). Otherwise, fix the regression.",
                    }
                )
        elif direction == "down":
            if current > baseline + tolerance:
                findings.append(
                    {
                        "file_path": str(args.config),
                        "error_code": "ratchet_violation",
                        "metric": name,
                        "direction": "down",
                        "baseline": baseline,
                        "current": current,
                        "tolerance": tolerance,
                        "suggested_fix": "If the increase is intended, update the baseline (human-only). Otherwise, fix the regression.",
                    }
                )
        else:
            findings.append(
                {
                    "file_path": str(args.config),
                    "error_code": "unknown_direction",
                    "metric": name,
                    "direction": direction,
                    "suggested_fix": "Fix governance/ratchets.json so direction is 'up' or 'down'.",
                }
            )

    if findings:
        if args.json:
            print(json.dumps(findings, indent=2, sort_keys=True))
            return 1

        for f in findings:
            metric = f.get("metric", "<unknown>")
            direction = f.get("direction", "<unknown>")
            baseline = f.get("baseline")
            current = f.get("current")
            tol = f.get("tolerance", 0.0)
            code = f.get("error_code", "ratchet_violation")
            print(
                f"[ratchet] FAIL error_code={code} metric={metric} direction={direction} baseline={baseline} current={current} tol={tol}"
            )
        return 1

    if args.json:
        print("[]")
    else:
        print("[ratchet] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
