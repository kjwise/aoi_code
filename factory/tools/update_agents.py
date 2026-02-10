from __future__ import annotations

import argparse
import difflib
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    p = start
    if p.is_file():
        p = p.parent

    for parent in [p] + list(p.parents):
        if (parent / "Makefile").exists():
            return parent
    return Path.cwd()


def _find_agents_file(start: Path, root: Path) -> Path:
    p = start
    if p.is_file():
        p = p.parent

    for parent in [p] + list(p.parents):
        candidate = parent / "AGENTS.md"
        if candidate.exists():
            return candidate
        if parent == root:
            break

    return root / "AGENTS.md"


def _parse_make_help(help_text: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for raw in help_text.splitlines():
        line = raw.strip()
        if not line.startswith("make "):
            continue

        parts = line.split(None, 2)
        if len(parts) < 2:
            continue

        target = parts[1]
        desc = parts[2].strip() if len(parts) >= 3 else ""
        items.append((target, desc))

    return items


def _render_commands_section(items: list[tuple[str, str]]) -> list[str]:
    lines: list[str] = []
    lines.append("This repo is designed to be run via `make` from the repo root.")
    lines.append("")

    for target, desc in items:
        if desc:
            lines.append(f"- `make {target}` — {desc}")
        else:
            lines.append(f"- `make {target}`")

    return lines


def _upsert_section(full_text: str, heading: str, new_body_lines: list[str]) -> str:
    lines = full_text.splitlines()

    try:
        start = lines.index(heading)
    except ValueError:
        if lines and lines[-1].strip() != "":
            lines.append("")
        lines.extend([heading, ""] + new_body_lines)
        return "\n".join(lines) + "\n"

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break

    new_lines = lines[: start + 1]
    new_lines.append("")
    new_lines.extend(new_body_lines)
    if end < len(lines):
        new_lines.append("")
        new_lines.extend(lines[end:])

    return "\n".join(new_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Propose patch-style updates to the nearest AGENTS.md file (Map-Updater demo)."
        )
    )
    parser.add_argument("--path", type=Path, required=True, help="A changed file path (used for scoping).")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("build/update_agents"),
        help="Directory to write patch suggestions into.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the update directly to AGENTS.md instead of writing a patch suggestion.",
    )
    args = parser.parse_args()

    changed_path = Path(args.path)
    root = _find_repo_root(changed_path.resolve())
    agents_path = _find_agents_file(changed_path.resolve(), root)

    help_text = subprocess.check_output(["make", "help"], cwd=root, text=True)
    items = _parse_make_help(help_text)

    old_text = ""
    if agents_path.exists():
        old_text = agents_path.read_text(encoding="utf-8")

    new_text = _upsert_section(old_text, "## Commands", _render_commands_section(items))

    if old_text == new_text:
        print("[update_agents] no drift detected (AGENTS.md matches Makefile help)")
        return 0

    rel_agents = agents_path
    try:
        rel_agents = agents_path.relative_to(root)
    except ValueError:
        pass

    diff_lines = list(
        difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            fromfile=str(rel_agents),
            tofile=str(rel_agents),
            lineterm="",
        )
    )
    patch_text = "\n".join(diff_lines) + "\n"

    if args.apply:
        agents_path.write_text(new_text, encoding="utf-8")
        print(f"[update_agents] applied updates to {rel_agents}")
        return 0

    out_dir = args.out_dir
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"update_agents_{stamp}.patch"
    out_path.write_text(patch_text, encoding="utf-8")

    try:
        rel_out = out_path.relative_to(root)
    except ValueError:
        rel_out = out_path

    print(f"[update_agents] wrote patch suggestions to {rel_out}")
    print("[update_agents] apply with: git apply <patchfile>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
