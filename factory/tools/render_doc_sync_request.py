from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a diff-only request from template + context.")
    parser.add_argument("--context", type=Path, required=True, help="Context JSON")
    parser.add_argument("--template", type=Path, required=True, help="Template text")
    args = parser.parse_args()

    context = json.loads(args.context.read_text(encoding="utf-8"))
    template = args.template.read_text(encoding="utf-8")

    signatures = context.get("extracted_signatures", [])
    signatures_block = "\n".join(f"- `{s}`" for s in signatures)

    rendered = template.format(
        task_id=context.get("task_id", ""),
        target_file=context.get("target_file", ""),
        allowed_heading=context.get("allowed_heading", ""),
        signatures_block=signatures_block,
        current_block=context.get("current_block", "").rstrip(),
    )

    print(rendered.rstrip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
