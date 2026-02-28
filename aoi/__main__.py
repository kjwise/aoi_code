from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(script_rel: str, argv: list[str]) -> int:
    script = ROOT / script_rel
    if not script.exists():
        raise FileNotFoundError(f"missing tool: {script_rel}")
    p = subprocess.run([sys.executable, str(script), *argv])
    return int(p.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(prog="aoi", description="Architects of Intent companion CLI.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sync = sub.add_parser("sync", help="(Ch1) sync Map from Terrain (apply)")
    p_sync.add_argument("--src", default="product/src")
    p_sync.add_argument("--doc", default="product/docs/architecture.md")
    p_sync.add_argument(
        "--no-apply",
        dest="apply",
        action="store_false",
        help="Emit diff only (do not modify the Map file)",
    )
    p_sync.set_defaults(apply=True)

    p_validate = sub.add_parser("validate", help="(Ch1) validate Map/Terrain alignment")
    p_validate.add_argument("--src", default="product/src")
    p_validate.add_argument("--doc", default="product/docs/architecture.md")
    p_validate.add_argument("--json", action="store_true", help="Emit structured findings JSON")

    p_all = sub.add_parser("all", help="(Ch1) run sync + validate (Salvage Protocol on failure)")
    p_all.add_argument("--src", default="product/src")
    p_all.add_argument("--doc", default="product/docs/architecture.md")
    p_all.add_argument("--effector", default="tools/sync_public_interfaces.py")
    p_all.add_argument("--seed", type=int, default=None)
    p_all.add_argument("--quarantine-dir", default=".sdac/workflow-quarantine")

    p_request = sub.add_parser("request", help="(Ch2) build context + render diff-only request")
    p_request.add_argument("--src", default="product/src")
    p_request.add_argument("--doc", default="product/docs/architecture.md")
    p_request.add_argument("--out", default="build/doc_sync_context.json")
    p_request.add_argument(
        "--template",
        default="factory/templates/doc_sync_diff_request.txt",
    )

    p_drift = sub.add_parser("drift", help="(Ch4) measure diff variance")
    p_drift.add_argument("--src", default="product/src")
    p_drift.add_argument("--doc", default="product/docs/architecture.md")
    p_drift.add_argument("--runs", type=int, default=10)
    p_drift.add_argument("--seed", type=int, default=1234)
    p_drift.add_argument("--mock", action="store_true", help="Use offline mock Effector variants")
    p_drift.add_argument("--validate", action="store_true", help="Validate each applied candidate")

    p_mission = sub.add_parser("mission-dry-run", help="(Ch5) print slice + validators + budgets")
    p_mission.add_argument("--mission", default="missions/update_public_interfaces.json")

    p_graph = sub.add_parser("graph", help="(Ch6) build context graph snapshot")
    p_graph.add_argument("--root", default="examples/tax_service")
    p_graph.add_argument("--out", default="build/context_graph.json")

    p_slice = sub.add_parser("slice", help="(Ch6) emit a slice packet from an anchor")
    p_slice.add_argument("--graph", default="build/context_graph.json")
    p_slice.add_argument(
        "--anchor",
        default="examples/tax_service/tests/test_tax_service.py:test_calculate_income_tax_high_earner_scenario",
    )
    p_slice.add_argument("--out", default="build/slice_packet.md")

    p_bf = sub.add_parser("branching-factor", help="(Ch6) lint fan-out heuristics")
    p_bf.add_argument("--root", default="examples/tax_service")

    p_driver = sub.add_parser("driver-demo", help="(Ch7) resolve a driver from deterministic identity")
    p_driver.add_argument("--action", default="run_tests")
    p_driver.add_argument("--target", default="product/src")

    p_agents = sub.add_parser("agents-suggest", help="(Ch8) propose updates to AGENTS.md")
    p_agents.add_argument("--path", default="Makefile")

    p_dream = sub.add_parser("dream-scan", help="(Ch9) read-only entropy scan (Depth 0)")
    p_dream.add_argument("--root", default=".")
    p_dream.add_argument("--cc-threshold", type=int, default=30)
    p_dream.add_argument("--file-lines", type=int, default=500)

    sub.add_parser("validate-missions", help="(Ch7) validate Mission Object templates")
    sub.add_parser("salvage", help="List quarantined near-misses")

    sub.add_parser("test", help="Run unit tests (stdlib unittest)")

    p_metrics = sub.add_parser("metrics", help="Collect metrics for ratchets")
    p_metrics.add_argument("--root", default=".")
    p_metrics.add_argument("--out-dir", default=".metrics/current")

    p_ratchet = sub.add_parser("ratchet-check", help="(Ch11) compare current metrics to baselines")
    p_ratchet.add_argument("--config", default="governance/ratchets.json")
    p_ratchet.add_argument("--json", action="store_true")

    p_baseline = sub.add_parser("ratchet-baseline", help="(Ch11) update baselines from current metrics")
    p_baseline.add_argument("--config", default="governance/ratchets.json")
    p_baseline.add_argument("--yes", action="store_true")

    args = parser.parse_args()

    if args.cmd == "sync":
        argv = ["--src", args.src, "--doc", args.doc]
        if args.apply:
            argv.append("--apply")
        return _run("tools/sync_public_interfaces.py", argv)

    if args.cmd == "validate":
        argv = ["--src", args.src, "--doc", args.doc]
        if args.json:
            argv.append("--json")
        return _run("tools/validate_map_alignment.py", argv)

    if args.cmd == "all":
        argv = [
            "--src",
            args.src,
            "--doc",
            args.doc,
            "--effector",
            args.effector,
            "--quarantine-dir",
            args.quarantine_dir,
        ]
        if args.seed is not None:
            argv += ["--seed", str(args.seed)]
        return _run("tools/run_mvf_all.py", argv)

    if args.cmd == "request":
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        rc = _run(
            "factory/tools/build_doc_sync_context.py",
            ["--src", args.src, "--doc", args.doc, "--out", args.out],
        )
        if rc != 0:
            return rc
        return _run(
            "factory/tools/render_doc_sync_request.py",
            ["--context", args.out, "--template", args.template],
        )

    if args.cmd == "drift":
        argv = [
            "--src",
            args.src,
            "--doc",
            args.doc,
            "--runs",
            str(args.runs),
            "--seed",
            str(args.seed),
        ]
        if args.mock:
            argv.append("--mock")
        if args.validate:
            argv.append("--validate")
        return _run("factory/tools/measure_drift.py", argv)

    if args.cmd == "mission-dry-run":
        rc = _run("factory/tools/validate_missions.py", [])
        if rc != 0:
            return rc
        return _run("factory/tools/mission_dry_run.py", ["--mission", args.mission])

    if args.cmd == "graph":
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        return _run("factory/tools/build_context_graph.py", ["--root", args.root, "--out", args.out])

    if args.cmd == "slice":
        return _run(
            "factory/tools/slice_context_graph.py",
            ["--graph", args.graph, "--anchor", args.anchor, "--out", args.out],
        )

    if args.cmd == "branching-factor":
        return _run("factory/tools/lint_branching_factor.py", ["--root", args.root])

    if args.cmd == "driver-demo":
        return _run(
            "factory/tools/resolve_driver.py",
            ["--action", args.action, "--target", args.target],
        )

    if args.cmd == "agents-suggest":
        return _run("factory/tools/update_agents.py", ["--path", args.path])

    if args.cmd == "dream-scan":
        return _run(
            "factory/tools/dream_scan.py",
            [
                "--root",
                args.root,
                "--cc-threshold",
                str(args.cc_threshold),
                "--file-lines",
                str(args.file_lines),
            ],
        )

    if args.cmd == "validate-missions":
        return _run("factory/tools/validate_missions.py", [])

    if args.cmd == "salvage":
        return _run("factory/tools/salvage.py", [])

    if args.cmd == "test":
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        p = subprocess.run(cmd)
        return int(p.returncode)

    if args.cmd == "metrics":
        Path(args.out_dir).mkdir(parents=True, exist_ok=True)
        return _run(
            "factory/tools/collect_metrics.py",
            ["--root", args.root, "--out-dir", args.out_dir],
        )

    if args.cmd == "ratchet-check":
        m = _run(
            "factory/tools/collect_metrics.py",
            ["--root", ".", "--out-dir", ".metrics/current"],
        )
        if m != 0:
            return m
        argv = ["--config", args.config]
        if args.json:
            argv.append("--json")
        return _run("factory/tools/ratchet_check.py", argv)

    if args.cmd == "ratchet-baseline":
        m = _run(
            "factory/tools/collect_metrics.py",
            ["--root", ".", "--out-dir", ".metrics/current"],
        )
        if m != 0:
            return m
        argv = ["--config", args.config]
        if args.yes:
            argv.append("--yes")
        return _run("factory/tools/ratchet_update_baseline.py", argv)

    raise RuntimeError(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
