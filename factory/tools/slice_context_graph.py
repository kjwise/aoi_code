from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a tiny slice packet from a context graph snapshot (demo).")
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--anchor", required=True, help="Node id, e.g. path/to/file.py:test_name")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in graph.get("nodes", [])}

    if args.anchor not in nodes:
        raise SystemExit(f"anchor not found in graph: {args.anchor}")

    anchor_id = args.anchor
    anchor_path = Path(anchor_id.split(":", 1)[0])

    root = Path(graph.get("root", "."))

    map_paths: list[Path] = []
    terrain_paths: list[Path] = []

    # Heuristic for the book's worked tax example.
    if "/tests/" in str(anchor_path):
        terrain_paths.append(anchor_path)
        candidate_src = Path(str(anchor_path).replace("/tests/", "/src/").replace("test_", ""))
        if candidate_src.exists():
            terrain_paths.append(candidate_src)
        rules = root / "docs" / "tax_rules.md"
        if rules.exists():
            map_paths.append(rules)
    else:
        terrain_paths.append(anchor_path)

    out_lines: list[str] = []
    out_lines.append(f"# Slice Packet (demo)\n\n")
    out_lines.append(f"Anchor: `{anchor_id}`\n\n")

    if map_paths:
        out_lines.append("## Map\n\n")
        for p in map_paths:
            out_lines.append(f"### `{p}`\n\n")
            out_lines.append("```markdown\n")
            out_lines.append(_read(p))
            out_lines.append("```\n\n")

    out_lines.append("## Terrain\n\n")
    for p in terrain_paths:
        out_lines.append(f"### `{p}`\n\n")
        fence = "python" if p.suffix == ".py" else "text"
        out_lines.append(f"```{fence}\n")
        out_lines.append(_read(p))
        out_lines.append("```\n\n")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(out_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
