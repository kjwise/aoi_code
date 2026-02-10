from __future__ import annotations

import argparse
import json
from pathlib import Path


def _estimate_tokens(text: str) -> int:
    # Rough heuristic: ~4 chars/token for English-like text.
    return max(1, len(text) // 4)


def _heading_ref(heading: str) -> str:
    # "## Public Interfaces" -> "Public Interfaces"
    return heading.lstrip('#').strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dry run a Mission: print slice + validators + budgets (no model call)."
    )
    parser.add_argument("--mission", type=Path, required=True)
    args = parser.parse_args()

    mission = json.loads(args.mission.read_text(encoding="utf-8"))

    mission_id = mission.get("mission_id", "<missing>")
    goal = mission.get("goal", "<missing>")

    scope = mission.get("scope", {})
    target_file = scope.get("target_file")
    allowed_heading = scope.get("allowed_heading")

    slice_spec = mission.get("slice", {})
    terrain_roots = [Path(p) for p in slice_spec.get("terrain_roots", [])]
    map_files = [Path(p) for p in slice_spec.get("map_files", [])]

    slice_text = ""
    for root in terrain_roots:
        for p in sorted(root.rglob("*.py")):
            slice_text += p.read_text(encoding="utf-8")

    for p in map_files:
        slice_text += p.read_text(encoding="utf-8")

    budgets = mission.get("budgets", {})
    validators = mission.get("validators", [])

    print(f"[DRY RUN] mission_id={mission_id}")
    print(f"[DRY RUN] goal={goal}")

    print("[DRY RUN] slice:")
    if target_file and allowed_heading:
        print(f"  - {target_file}#{_heading_ref(allowed_heading)}")
    for root in terrain_roots:
        print(f"  - {root}/**/*.py")

    print(f"[DRY RUN] token_estimate={_estimate_tokens(slice_text)}")

    print("[DRY RUN] validators:")
    for v in validators:
        print(f"  - {v.get('name', 'validator')}: {v.get('cmd', '<missing cmd>')}")

    if budgets:
        print("[DRY RUN] budgets:")
        for k, v in budgets.items():
            print(f"  - {k}={v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
