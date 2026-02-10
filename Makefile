.PHONY: help all sync validate request drift mission-dry-run graph slice branching-factor \
	dream-scan driver-demo agents-suggest test metrics ratchet-check ratchet-baseline clean

PY ?= python3

MVF_SRC = product/src
MVF_DOC = product/docs/architecture.md
CHANGED ?= Makefile

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
	 && echo "  make test             run local unit tests (stdlib unittest)" \
	 && echo "  make ratchet-check     (Ch11) compare current metrics to baselines" \
	 && echo "  make ratchet-baseline  (Ch11) update baselines from current metrics" \
	 && echo "  make clean            remove build artifacts"

all: sync validate

sync: ## Propose/apply Map updates from Terrain
	$(PY) factory/tools/sync_public_interfaces.py --src $(MVF_SRC) --doc $(MVF_DOC) --apply

validate: ## Enforce Map/Terrain alignment (Physics)
	$(PY) factory/tools/validate_map_alignment.py --src $(MVF_SRC) --doc $(MVF_DOC)

request:
	@mkdir -p build
	$(PY) factory/tools/build_doc_sync_context.py --src $(MVF_SRC) --doc $(MVF_DOC) --out build/doc_sync_context.json
	$(PY) factory/tools/render_doc_sync_request.py --context build/doc_sync_context.json --template factory/templates/doc_sync_diff_request.txt

drift:
	$(PY) factory/tools/measure_drift.py --src $(MVF_SRC) --doc $(MVF_DOC) --runs 10

mission-dry-run:
	$(PY) factory/tools/mission_dry_run.py --mission missions/update_public_interfaces.json

graph:
	@mkdir -p build
	$(PY) factory/tools/build_context_graph.py --root examples/tax_service --out build/context_graph.json

slice: graph
	$(PY) factory/tools/slice_context_graph.py \
		--graph build/context_graph.json \
		--anchor examples/tax_service/tests/test_tax_service.py:test_calculate_income_tax_high_earner_scenario \
		--out build/slice_packet.md
	@echo "Wrote build/slice_packet.md"

branching-factor:
	$(PY) factory/tools/lint_branching_factor.py --root examples/tax_service

driver-demo:
	$(PY) factory/tools/resolve_driver.py --action run_tests --target product/src

agents-suggest:
	$(PY) factory/tools/update_agents.py --path $(CHANGED)

dream-scan:
	$(PY) factory/tools/dream_scan.py --root .

test:
	$(PY) -m unittest discover -s tests -v

metrics:
	@mkdir -p .metrics/current
	$(PY) factory/tools/collect_metrics.py --root . --out-dir .metrics/current

ratchet-check: metrics
	$(PY) factory/tools/ratchet_check.py --config governance/ratchets.json

ratchet-baseline: metrics
	$(PY) factory/tools/ratchet_update_baseline.py --config governance/ratchets.json --yes

clean:
	rm -rf build
