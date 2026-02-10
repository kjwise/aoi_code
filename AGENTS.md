# AGENTS.md — `aoi_code`

Scope: this repository.

This file is an example of a *Map surface*: local instructions for humans and agents.

## Commands

This repo is designed to be run via `make` from the repo root.

- `make all` — (Ch1) sync + validate
- `make sync` — (Ch1) propose/apply Map updates from Terrain
- `make validate` — (Ch1) enforce Map/Terrain alignment
- `make request` — (Ch2) render a diff-only request from template + context
- `make drift` — (Ch4) measure diff variance from a stochastic effector
- `make mission-dry-run` — (Ch5) print slice + validators + budgets
- `make graph` — (Ch6) build a tiny context graph snapshot
- `make slice` — (Ch6) emit a slice packet from an anchor
- `make branching-factor` — (Ch6) lint fan-out heuristics
- `make driver-demo` — (Ch7) resolve a driver from deterministic identity
- `make agents-suggest` — (Ch8) propose updates to AGENTS.md (Map-Updater demo)
- `make dream-scan` — (Ch9) read-only entropy scan (Depth 0)
- `make test` — run local unit tests (stdlib unittest)
- `make ratchet-check` — (Ch11) compare current metrics to baselines
- `make ratchet-baseline` — (Ch11) update baselines from current metrics
- `make clean` — remove build artifacts

## Notes

- Demos are designed to be local and auditable (no network calls).
- Build artifacts are written under `build/` (ignored by git).
