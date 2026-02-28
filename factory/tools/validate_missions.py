from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _parse_scalar(text: str) -> object:
    t = text.strip()
    if t.startswith('"') and t.endswith('"') and len(t) >= 2:
        return t[1:-1]
    if t.startswith("'") and t.endswith("'") and len(t) >= 2:
        return t[1:-1]
    if t.lower() in {"true", "false"}:
        return t.lower() == "true"
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?\d+\.\d+", t):
        return float(t)
    return t


def _yaml_minimal_load(text: str) -> object:
    lines = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        if raw.lstrip().startswith("#"):
            continue
        lines.append(raw.rstrip("\n"))

    def parse_block(i: int, indent: int) -> tuple[object, int]:
        # Find the first line at this indent to decide list vs dict.
        j = i
        while j < len(lines):
            if len(lines[j]) - len(lines[j].lstrip(" ")) < indent:
                return {}, j
            if lines[j].strip():
                break
            j += 1
        if j >= len(lines):
            return {}, j

        is_list = lines[j].startswith(" " * indent + "- ")
        if is_list:
            out: list[object] = []
            while j < len(lines):
                cur_indent = len(lines[j]) - len(lines[j].lstrip(" "))
                if cur_indent < indent:
                    break
                if not lines[j].startswith(" " * indent + "- "):
                    break
                item_text = lines[j][indent + 2 :].strip()
                j += 1
                if item_text == "":
                    item, j = parse_block(j, indent + 2)
                    out.append(item)
                    continue
                if ":" in item_text and not item_text.startswith(("'", '"')):
                    k, v = item_text.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if v == "":
                        nested, j = parse_block(j, indent + 4)
                        out.append({k: nested})
                    else:
                        out.append({k: _parse_scalar(v)})
                    continue
                out.append(_parse_scalar(item_text))
            return out, j

        out_dict: dict[str, object] = {}
        while j < len(lines):
            cur_indent = len(lines[j]) - len(lines[j].lstrip(" "))
            if cur_indent < indent:
                break
            if cur_indent != indent:
                raise ValueError(f"unexpected indentation: {lines[j]!r}")

            line = lines[j].strip()
            if ":" not in line:
                raise ValueError(f"expected key: value, got: {line!r}")
            key, rest = line.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            j += 1

            if rest == "":
                val, j = parse_block(j, indent + 2)
                out_dict[key] = val
            else:
                out_dict[key] = _parse_scalar(rest)
        return out_dict, j

    obj, _ = parse_block(0, 0)
    return obj


def _load_mission(path: Path) -> dict[str, object]:
    if path.suffix in {".json"}:
        return json.loads(path.read_text(encoding="utf-8"))

    if path.suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except Exception:  # pragma: no cover
            yaml = None

        if yaml is not None:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        else:
            loaded = _yaml_minimal_load(path.read_text(encoding="utf-8"))

        if not isinstance(loaded, dict):
            raise ValueError("mission YAML must be a mapping at root")
        return loaded

    raise ValueError(f"unsupported mission format: {path}")


def _require_str(obj: dict[str, object], key: str, where: str) -> str:
    v = obj.get(key)
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{where}: missing/invalid {key!r} (expected non-empty string)")
    return v


def _require_dict(obj: dict[str, object], key: str, where: str) -> dict[str, object]:
    v = obj.get(key)
    if not isinstance(v, dict):
        raise ValueError(f"{where}: missing/invalid {key!r} (expected object)")
    return v  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Mission Object templates (stdlib-only).")
    parser.add_argument("--root", type=Path, default=Path("missions/templates"))
    parser.add_argument("--schema", type=Path, default=Path("missions/schema/mission.schema.json"))
    args = parser.parse_args()

    mission_dir = args.root.parent if args.root.name == "templates" else Path("missions")
    paths = []
    paths.extend(
        p
        for p in mission_dir.glob("*.json")
        if p.is_file() and p.name != "mission.schema.json"
    )
    paths.extend(
        p for p in args.root.rglob("*") if p.is_file() and p.suffix in {".json", ".yaml", ".yml"}
    )
    paths = sorted(set(paths))
    if not paths:
        print(f"[missions] no templates found under {args.root}")
        return 0

    errors: list[str] = []
    seen_ids: dict[str, Path] = {}

    for p in paths:
        where = str(p)
        try:
            mission = _load_mission(p)
            mid = _require_str(mission, "mission_id", where)
            _require_str(mission, "goal", where)
            scope = _require_dict(mission, "scope", where)

            if mid in seen_ids:
                errors.append(f"{where}: duplicate mission_id={mid!r} (also in {seen_ids[mid]})")
            else:
                seen_ids[mid] = p

            # Basic hygiene: if a mission points at a file, it should exist.
            file_key = None
            for k in ("target_file", "file"):
                if k in scope:
                    file_key = k
                    break
            if file_key is not None and isinstance(scope.get(file_key), str):
                target = Path(scope[file_key])  # type: ignore[arg-type]
                if not target.exists():
                    errors.append(f"{where}: scope.{file_key} points to missing path: {target}")
        except Exception as e:
            errors.append(f"{where}: {e}")

    if errors:
        for e in errors:
            print(f"[missions] FAIL {e}", file=sys.stderr)
        return 1

    print(f"[missions] PASS templates={len(paths)} schema={args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
