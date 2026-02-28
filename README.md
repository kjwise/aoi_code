# Architects of Intent — Companion Code (`aoi_code`)

This repository contains runnable examples for the book *Architects of Intent*.

The book keeps chapters readable by pushing implementation detail here.
Everything in this repo is designed to be small, local, and auditable (no network calls).

Run `make help` for a full menu of available targets.

## Quick Start

```bash
git clone https://github.com/kjwise/aoi_code.git
cd aoi_code
make all          # sync + validate (the MVF v0 loop)
make test         # run the unit test suite
```

Optional: the unified CLI (one command surface under `python3 -m aoi`):

```bash
python3 -m aoi --help
```

## Skill: Deterministic Make-Driven Multi-Repo Architecture

A companion, public guide: [`deterministic-make-driven-multi-repo-architecture.md`](skills/deterministic-make-driven-multi-repo-architecture.md)

## Chapter Map

Each `make` target maps to a chapter in the book. The table below shows the relationship.

| Chapter | Target(s) | What it demonstrates |
| :-- | :-- | :-- |
| Ch 1 — MVF v0 | `make all`, `make sync`, `make validate` | The minimum viable factory loop: Effector + Validator |
| Ch 2 — Deterministic Sandwich | `make request` | Template-driven `Prep`: structured context → diff-only request |
| Ch 4 — Stochastic Engine | `make drift` | Measuring stochastic variance across repeated runs |
| Ch 5 — Ouroboros Protocol | `make mission-dry-run` | Dry run: print slice + validators + budgets (no model call) |
| Ch 6 — Context Architecture | `make graph`, `make slice`, `make branching-factor` | Build a context graph, emit a slice packet, lint fan-out |
| Ch 7 — Mission Objects | `make driver-demo` | Resolve a driver from deterministic identity |
| Ch 8 — Map-Updaters | `make agents-suggest` | Propose updates to `AGENTS.md` from `Makefile` |
| Ch 9 — Dream Daemon | `make dream-scan` | Read-only entropy scan (Depth 0) |
| Ch 10 — Immutable Infrastructure | `governance/` | Break-glass template, kill-switch CI workflow |
| Ch 11 — Refactoring Under Guards | `make ratchet-check`, `make ratchet-baseline` | Monotonic ratchet: baseline capture + compare |

## Chapter 1: Minimum Viable Factory (MVF v0)

Run the loop:

```bash
make all
git diff --stat || true
```

What you should see:

- The **Effector** (`sync_public_interfaces.py`) updates `product/docs/architecture.md` so its `## Public Interfaces` section matches the public functions in `product/src/`.
- The **Validator** (`validate_map_alignment.py`) enforces Map/Terrain alignment and prints `map_terrain_sync=pass`.

To reset the demo back to the initial state:

```bash
git restore product/docs/architecture.md
```

## Chapter 2: Template-driven request (deterministic `Prep`)

Render a diff-only request from a structured context object + a template:

```bash
make request
```

This target runs two steps:

1. `build_doc_sync_context.py` extracts the current Map and Terrain into `build/doc_sync_context.json`.
2. `render_doc_sync_request.py` renders that context through `factory/templates/doc_sync_diff_request.txt`.

## Chapter 4: Stochastic drift measurement

Simulate a stochastic doc-sync effector and measure how many distinct diffs it emits:

```bash
make drift
```

## Chapter 5: Dry run (Plan Mode)

Print the bounded work packet (slice + validators + budgets) without calling any model:

```bash
make mission-dry-run
```

## Chapter 6: Context graph + slicing

Build a tiny graph snapshot and emit an example slice packet:

```bash
make graph              # build the graph
make slice              # emit a slice packet from an anchor
make branching-factor   # lint fan-out heuristics
```

## Chapter 7: Mission Objects (schema + templates + drivers)

Mission Object examples live under:

- `missions/schema/mission.schema.json` (demo schema)
- `missions/templates/` (template examples)
- `drivers/registry.json` (driver registry)

Demo driver resolution (deterministic identity → command):

```bash
make driver-demo
```

## Chapter 8: Map-Updaters (keeping instructions aligned)

Generate patch-style suggestions to keep `AGENTS.md` aligned with the repo's command panel:

```bash
make agents-suggest
ls build/update_agents
```

These suggestions are not applied automatically. Review and apply with `git apply <patchfile>`.

## Chapter 9: Dream scan (Depth 0)

Run a read-only entropy scan that emits a ranked worklist:

```bash
make dream-scan
```

By default, the repo is clean. Lower the threshold to see signals:

```bash
python3 -m aoi dream-scan --root . --cc-threshold 5
```

## Chapter 10–11: Governance templates + ratchets

Governance templates live under `governance/`:

- `BREAK_GLASS.md` — break-glass procedure template
- `ci/agent_merge_blocker.yml` — kill-switch CI workflow (branch-based)
- `ci/break_glass_checker.yml` — audit workflow for break-glass merges
- `ratchets.json` — ratchet configuration

Ratchets demo:

```bash
make ratchet-check      # compare current metrics to baselines
make ratchet-baseline   # update baselines (human-only action)
```

## Repository Layout

```text
aoi_code/
├── aoi/                       # Unified CLI package (`python3 -m aoi`)
├── AGENTS.md                  # Map surface: local instructions (Ch 8 demo)
├── core/                      # Step implementations (Chapter 10 topology)
├── dist/                      # Reserved (Chapter 10 topology)
├── Makefile                   # Command panel (all targets)
├── mk/                        # Reserved (Chapter 10 topology)
├── README.md                  # This file
├── drivers/                   # Driver registry (Ch 7)
├── examples/
│   ├── polyglot/              # Polyglot driver demo (Ch 7)
│   └── tax_service/           # Slicing example (Ch 6)
├── factory/
│   ├── templates/             # Prep templates (Ch 2)
│   └── tools/                 # Legacy-compatible wrappers (old entrypoints)
├── governance/                # Governance templates (Ch 10–11)
├── missions/                  # Mission Object examples (Ch 5, 7)
├── product/                   # Demo product (Map + Terrain)
│   ├── docs/architecture.md   # Map surface
│   └── src/                   # Terrain (source code)
├── tools/                     # Canonical entrypoints (Chapter 10 topology)
└── tests/                     # Unit tests
```

## Requirements

- Python 3.10+
- GNU Make
- No external dependencies (stdlib only)
