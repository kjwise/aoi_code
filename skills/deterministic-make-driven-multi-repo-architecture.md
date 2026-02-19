---
name: "deterministic-make-driven-multi-repo-architecture"
description: "Provide reusable governance and design guidance for organizing repos as Make-driven, bounded capability units with explicit contracts and predictable operations. Use this for advice on architecture, repo decomposition, Make target standards, and component ownership models."
---

# Deterministic Multi-Repo Architecture

Use this guidance when planning repo boundaries, operations standards, and component architecture.

## Core Idea

In a Make-first architecture, the repository is the architectural unit.

- A repo is a single bounded capability.
- A repo has a versioned contract surface.
- A repo is an independently operable execution unit.
- A repo is structurally uniform and Make-driven.

*A repo is operable, contractual, and independently releasable — or it is not a repo.*

## Repo Boundaries: When to Split and When Not To

- Split only when a capability has an independent release cadence, a distinct consumer, or a separately ownable contract. If none apply, keep it in the parent repo.
- Premature decomposition is an anti-pattern. Splitting before a contract is stable creates cross-repo churn with no architectural benefit.
- Rule of thumb: if the new repo's `contract/` directory would be empty or unstable for more than one release cycle, do not split yet.

## Non-Negotiable Invariants

- Each repo is Git-initialized.
- All operations are exposed through `make` targets.
- Orchestration is in `Makefile` and `mk/*.mk`.
- Execution logic is in `scripts/`.
- Repos are independently buildable and testable.
- Publicly consumed repos publish a contract.
- Once a commit is referenced in any downstream `deps.lock`, that commit is immutable. Force-pushing or rewriting history on a repo that has consumers is a violation of this model.
- If a repo cannot be fully operated via `make`, it violates this model.

## Cross-Repo Dependency Rules

`Intent (Make graph) -> Implementation (scripts) -> Artifact (build output) -> Contract v1.2.0 (external surface)` — the version is part of the artifact, not an afterthought.

### Declaration

Dependencies are declared in a `deps.lock` file at the repo root. The file is version-controlled and has one entry per line:

```text
repo-name <repo-url> <full-40-char-SHA>
```

`<repo-url>` may be SSH or HTTPS. No ranges, no tags, no branch names. Tags are mutable; SHAs are not.

### Resolution

`make init` reads `deps.lock`, clones or fetches each repo into `.deps/` (gitignored), and checks out the pinned SHA. If the SHA is not reachable, `make init` fails loudly and prints the offending line. Shallow clones (`--depth 1`) are acceptable after the SHA is confirmed reachable.

### Updating a Pin

Pins are updated manually and deliberately, never automatically:

```bash
make dep-update REPO=repo-name SHA=<new-sha>
```

This target updates `deps.lock`, runs `make contract-check` against the new version locally, and refuses to write the new SHA if `contract-check` fails.

### What You Consume

A dependent repo imports only from the pinned repo's `contract/` directory, never from `src/`. This is enforced by convention and documented in `contract-check`.

### Direct Dependencies Only

Undeclared transitive consumption is disallowed. A repo may declare only what it directly consumes.

### Auditing

`git log deps.lock` provides a full, auditable history of every dependency bump. No registry is required. Repos that declare `deps.lock` must expose a `make dep-audit` target that reports how far each pin is behind that dependency's `main`, supporting deliberate security patch management.

## Why this exists

- Context discipline: small, focused repos reduce cognitive and token/context overhead.
- Uniform control surface: `make` is deterministic and predictable.
- Explicit orchestration: make defines command taxonomy and execution order.

## Required make surface

- `make init`
- `make build`
- `make test`
- `make contract-check`
- `make release`
- `make dep-audit` (required when `deps.lock` is present; may be a no-op otherwise)

Avoid per-repo command drift. No tribal knowledge.

## Required structure

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
│   ├── schema.json        # machine-readable contract (or openapi.yaml, jsonschema, etc.)
│   ├── VERSION            # semver string, e.g. "1.2.0"
│   └── CHANGELOG.md       # contract-level changes only
├── src/
├── tests/
├── README.md
└── CHANGELOG.md
```

Governance rules:
- Root `Makefile` should include only `mk/*.mk`.
- `.mk` files should group capability domains.
- Scripts should be single-purpose and small.
- No cross-repo internal imports.
- Version and constrain everything across boundaries.

## Definition of a proper component

A valid component has:
- Single purpose.
- A versioned contract.
- A releasable artifact.
- Independent build/test capability.
- Consumability without reading internals.

A versioned contract must include:
- A machine-readable schema.
- A semver version string.
- A stability classification (`stable`, `experimental`, or `deprecated`) recorded in schema metadata.

`make contract-check` must validate the schema and compare the current contract version against the last published version, failing loudly on mismatch.

## Practical Patterns (From a Real Make-First Repo)

These are concrete patterns that make Make-driven repos easier to operate and compose. Use them when you need more than high-level principles.

### 1) Split deterministic vs. non-deterministic workflows

- Keep the stable repo control surface deterministic (`Makefile` + `mk/*.mk`).
- Put AI / network / human-in-the-loop steps behind an explicit entrypoint, e.g. `Makefile.ai` invoked as `make -f Makefile.ai <target>`.
- `Makefile.ai` includes `mk/vars.mk` only, not the full core Makefile, to avoid pulling in build logic with side effects.
- Secrets are passed as environment variables, never hardcoded.
- Required variables are validated with explicit errors when AI targets are enabled.

Validation pattern:

```make
ifeq ($(USE_AI),1)
ifndef OPENAI_API_KEY
  $(error OPENAI_API_KEY is not set)
endif
endif
```

- AI targets are opt-in in CI, guarded by `USE_AI` so standard pipelines remain deterministic by default.

Minimal file skeleton:

```make
# Makefile.ai - AI-assisted targets only
include mk/vars.mk

.PHONY: generate-contract
generate-contract: ## Generate contract draft via LLM (requires USE_AI=1)
ifeq ($(USE_AI),1)
	scripts/generate_contract.sh
else
	$(error Set USE_AI=1 to run AI targets)
endif
```

Why: prevents `make build` / `make test` from depending on models, API keys, or flaky external tools.

### 2) Make `help` the default contract browser

- Set `.DEFAULT_GOAL := help`.
- Document targets with `## ...` and generate help by grepping `$(MAKEFILE_LIST)`.

Minimal pattern:

```make
.PHONY: help
help: ## Show targets
	@grep -h -E '^[a-zA-Z._-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}' | \
		sort
```

This turns the Make target list into a stable, self-updating contract surface.

### 3) Centralize variables and export what tools need

- Put paths + tool executables in a single include (e.g. `mk/vars.mk`).
- Export only the variables that downstream scripts require so `make` and `python -m ...` agree by default.
- Prefer override-by-env over editing defaults.

### 4) Model pipelines as an explicit DAG

- Represent intermediate artifacts as file targets (not just phony targets).
- Use dependencies to express ordering, then expose a meta-target (e.g. `build-web-full`) as the user-facing entrypoint.
- Keep side effects in scripts; keep orchestration in Make.

### 5) Hermetic builds via Docker (when host toolchains vary)

- Pin platform when needed (e.g. `--platform linux/amd64`).
- Mount the repo into the container; map UID/GID to avoid root-owned artifacts.
- Capture logs to files and print a small error digest on failure.

This makes `make build` reproducible across machines.

### 6) Backwards-compatible target aliases

- Preserve stable entrypoints even when you rename things.
- If you shipped a typo or legacy target name, keep an alias target pointing to the canonical one and label it clearly.

### 7) Trust-no-LLM for structured outputs

For any target that writes structured outputs (JSON, fixed headings, contract text, release notes):

- Add a deterministic validator function that checks shape and required fields.
- Retry generation at least once on validation failure (with clear stderr logging).
- On repeated failure, fail loudly or write the output explicitly marked as invalid.

Apply this especially to `contract-check`, `release`, and any AI-assisted workflows that emit machine-consumed artifacts.
