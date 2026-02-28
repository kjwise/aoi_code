.PHONY: help all sync validate request drift mission-dry-run graph slice branching-factor \
	dream-scan driver-demo agents-suggest validate-missions salvage kill-switch-engage kill-switch-release \
	test metrics ratchet-check ratchet-baseline clean

PY ?= python3

MVF_SRC = product/src
MVF_DOC = product/docs/architecture.md
CHANGED ?= Makefile
MOCK ?= 0
EFFECTOR ?= tools/sync_public_interfaces.py
EFFECTOR_SEED ?=
REMOTE ?= origin
KILL_SWITCH_BRANCH ?= disable-auto-merge

help:
	@echo "Targets:" \
	 && echo "  make all             (Ch1) sync + validate" \
	 && echo "  make sync            (Ch1) propose/apply Map updates from Terrain" \
	 && echo "  make validate         (Ch1) enforce Map/Terrain alignment" \
	 && echo "  make request          (Ch2) render a diff-only request from template + context" \
	 && echo "  make drift            (Ch4) measure diff variance from a stochastic effector" \
	 && echo "  make mission-dry-run   (Ch5) print slice + validators + budgets" \
	 && echo "  make graph            (Ch6) build a tiny context graph snapshot" \
	 && echo "  make slice            (Ch6) emit a slice packet from an anchor" \
	 && echo "  make branching-factor  (Ch6) lint fan-out heuristics" \
	 && echo "  make driver-demo      (Ch7) resolve a driver from deterministic identity" \
	 && echo "  make agents-suggest   (Ch8) propose updates to AGENTS.md (Map-Updater demo)" \
	 && echo "  make dream-scan        (Ch9) read-only entropy scan (Depth 0)" \
	 && echo "  make validate-missions  (Ch7) Mission Object hygiene (schema checks)" \
	 && echo "  make salvage           list quarantined near-misses" \
	 && echo "  make kill-switch-engage  push disable-auto-merge branch (CI kill switch)" \
	 && echo "  make kill-switch-release delete disable-auto-merge branch (CI kill switch)" \
	 && echo "  make test             run local unit tests (stdlib unittest)" \
	 && echo "  make ratchet-check     (Ch11) compare current metrics to baselines" \
	 && echo "  make ratchet-baseline  (Ch11) update baselines from current metrics" \
	 && echo "  make clean            remove build artifacts"

all: ## Run MVF v0 loop (with Salvage Protocol on failure)
	$(PY) -m aoi all --src $(MVF_SRC) --doc $(MVF_DOC) --effector $(EFFECTOR) $(if $(EFFECTOR_SEED),--seed $(EFFECTOR_SEED),)

sync: ## Propose/apply Map updates from Terrain
	$(PY) -m aoi sync --src $(MVF_SRC) --doc $(MVF_DOC)

validate: ## Enforce Map/Terrain alignment (Physics)
	$(PY) -m aoi validate --src $(MVF_SRC) --doc $(MVF_DOC)

validate-missions:
	$(PY) -m aoi validate-missions

request:
	$(PY) -m aoi request --src $(MVF_SRC) --doc $(MVF_DOC)

drift:
	@if [ "$(MOCK)" = "1" ]; then \
		echo "[drift] MOCK=1 (offline variants + validation)"; \
		$(PY) -m aoi drift --src $(MVF_SRC) --doc $(MVF_DOC) --runs 10 --mock --validate; \
	else \
		$(PY) -m aoi drift --src $(MVF_SRC) --doc $(MVF_DOC) --runs 10; \
	fi

mission-dry-run:
	$(PY) -m aoi mission-dry-run --mission missions/update_public_interfaces.json

graph:
	$(PY) -m aoi graph --root examples/tax_service --out build/context_graph.json

slice: graph
	$(PY) -m aoi slice \
		--graph build/context_graph.json \
		--anchor examples/tax_service/tests/test_tax_service.py:test_calculate_income_tax_high_earner_scenario \
		--out build/slice_packet.md
	@echo "Wrote build/slice_packet.md"

branching-factor:
	$(PY) -m aoi branching-factor --root examples/tax_service

driver-demo:
	$(PY) -m aoi driver-demo --action run_tests --target product/src

agents-suggest:
	$(PY) -m aoi agents-suggest --path $(CHANGED)

salvage:
	$(PY) -m aoi salvage

dream-scan:
	$(PY) -m aoi dream-scan --root .

kill-switch-engage:
	git push $(REMOTE) HEAD:refs/heads/$(KILL_SWITCH_BRANCH)

kill-switch-release:
	git push $(REMOTE) :$(KILL_SWITCH_BRANCH)

test:
	$(PY) -m aoi test

metrics:
	$(PY) -m aoi metrics --root . --out-dir .metrics/current

ratchet-check:
	$(PY) -m aoi ratchet-check --config governance/ratchets.json

ratchet-baseline:
	$(PY) -m aoi ratchet-baseline --config governance/ratchets.json --yes

clean:
	rm -rf build
