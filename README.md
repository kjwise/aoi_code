# Architects of Intent — Companion Code (`aoi_code`)

This repository contains runnable examples for the book *Architects of Intent*.

The book keeps chapters readable by pushing implementation detail here.
Everything in this repo is designed to be small, local, and auditable (no network calls).

Run `make help` for a menu.

## Chapter 1: Minimum Viable Factory (MVF v0)

Run the loop:

```bash
make all
git diff --stat || true
```

What you should see:

- The **Effector** updates `product/docs/architecture.md` so its `## Public Interfaces` section matches the public functions in `product/src/`.
- The **Validator** enforces Map/Terrain alignment and prints `map_terrain_sync=pass`.

To reset the demo back to the initial state:

```bash
git restore product/docs/architecture.md
```

## Chapter 2: Template-driven request (deterministic `Prep`)

Render a diff-only request from a structured context object + a template:

```bash
make request
```

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
make graph
make slice
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

These suggestions are not applied automatically.

## Chapter 9: Dream scan (Depth 0)

Run a read-only entropy scan that emits a ranked worklist:

```bash
make dream-scan
```

## Chapter 10–11: Governance templates + ratchets

- Governance templates live under `governance/`.
- Ratchets demo:

```bash
make ratchet-check
# To update baselines (human-only action):
make ratchet-baseline
```
