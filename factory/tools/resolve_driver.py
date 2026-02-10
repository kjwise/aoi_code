from __future__ import annotations

import argparse
import json
from pathlib import Path


def _detect_language(target: Path) -> str:
    path = target
    if path.is_file():
        path = path.parent

    for parent in [path] + list(path.parents):
        if (parent / "pyproject.toml").exists() or (parent / "requirements.txt").exists():
            return "python"
        if (parent / "package.json").exists():
            return "javascript"
    return "python"  # conservative default for this demo repo


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve an action to a concrete command via deterministic identity.")
    parser.add_argument("--registry", type=Path, default=Path("drivers/registry.json"))
    parser.add_argument("--action", default="run_tests")
    parser.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    language = _detect_language(args.target)

    for rule in registry.get(args.action, []):
        if rule.get("match", {}).get("language") == language:
            print(json.dumps({"action": args.action, "language": language, "cmd": rule.get("cmd")}, indent=2))
            return 0

    raise SystemExit(f"no driver for action={args.action} language={language}")


if __name__ == "__main__":
    raise SystemExit(main())
