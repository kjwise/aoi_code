# Deterministic Make-Driven Multi-Repo Architecture

## Core Idea

In an AI-first environment, the repository is the architectural unit.

Each repo is:
- A single bounded capability
- A versioned contract surface
- A deterministic execution unit
- A composable building block

The enforcement mechanism is simple:

> Every repository is Git-initialized, Make-driven, structurally uniform, and independently operable.

---

## Non-Negotiable Invariants

Every repo MUST:

- Be `git init`’ed
- Expose all operations via `make`
- Keep orchestration in `Makefile` + `mk/*.mk`
- Keep execution logic in `scripts/`
- Be independently buildable and testable
- Publish a contract (if externally consumed)

If it cannot be fully operated via `make`, it violates the architecture.

## Why This Matters

### 1. Context Discipline

Small, focused repos:
- Reduce human cognitive load
- Reduce AI token/context overhead
- Bound blast radius of change

Context is the primary scaling constraint. Repos are context containers.

### 2. Uniform Control Surface

Every repo responds to:

```
make init
make build
make test
make contract-check
make release
```

No tool drift.  
No tribal knowledge.  
No per-repo mental reconfiguration.

Agents and humans operate predictably.

### 3. Explicit Orchestration

Make defines:
- Command taxonomy
- Dependency graph
- Execution order

Scripts implement work.

Never bury orchestration logic inside scripts.

Make = architectural intent  
Scripts = replaceable workers

## Required Structure

```text
repo/
├── Makefile
├── mk/
│   ├── build.mk
│   ├── test.mk
│   ├── release.mk
│   ├── contract.mk
│   └── dev.mk
├── scripts/
├── contract/
├── src/
├── tests/
├── README.md
└── CHANGELOG.md
```

### Rules

- Root `Makefile` only includes `mk/*.mk`.
- `.mk` files group capability domains.
- Scripts are small and single-purpose.
- No cross-repo internal imports.
- Version everything that crosses a boundary.

## Multi-Repo Is the Default

Always prefer a new repo per bounded capability.

Reasons:
- Context isolation
- Independent versioning
- Clear ownership
- Explicit contracts
- Mechanical composition

Merge repos only if:
- The boundary is artificial
- Independent versioning is impossible
- Atomic cross-change is architecturally required

Convenience is not a valid reason.

## Definition of a Proper Component

A component is a repo that:

- Has a single purpose
- Exposes a versioned contract
- Produces a releasable artifact
- Can be built and tested in isolation
- Can be consumed without reading its internals

If an agent cannot discover how to build and test it from `make`, it is not a component.

## Architectural Pattern

Intent (Make graph)  
→ Implementation (scripts)  
→ Artifact (build output)  
→ Contract (external surface)

Architecture becomes composition of deterministic execution units — not entangled directories.

## Mantras

- “Context is a resource. Guard it.”
- “If you can’t `make` it, you can’t scale it.”
- “Contracts are stable; internals are disposable.”
- “Composition is architecture.”
