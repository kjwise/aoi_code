from __future__ import annotations

import argparse
import json
import py_compile
from pathlib import Path


def _count_tests(tests_root: Path) -> int:
    if not tests_root.exists():
        return 0

    count = 0
    for path in sorted(tests_root.rglob("*.py")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("def test_"):
                count += 1
    return count


def _count_syntax_errors(root: Path) -> int:
    errors = 0
    for path in sorted(root.rglob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError:
            errors += 1
    return errors


def _write_metric(out_dir: Path, name: str, value: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{name}.json").write_text(
        json.dumps({"value": value}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect demo metrics for ratchets (no external deps).")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    test_count = _count_tests(args.root / "tests")
    syntax_errors = _count_syntax_errors(args.root)

    _write_metric(args.out_dir, "test_count", test_count)
    _write_metric(args.out_dir, "python_syntax_errors", syntax_errors)

    print(f"[metrics] test_count={test_count} python_syntax_errors={syntax_errors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
