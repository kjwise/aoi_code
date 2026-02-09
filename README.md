# Architects of Intent — Companion Code (aoi_code)

This repository contains runnable examples for the book *Architects of Intent*.

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
