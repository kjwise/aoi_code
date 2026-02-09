.PHONY: all sync validate

SRC = product/src
DOC = product/docs/architecture.md

SYNC_CMD = python3 factory/tools/sync_public_interfaces.py \
  --src $(SRC) \
  --doc $(DOC) \
  --apply

VALIDATE_CMD = python3 factory/tools/validate_map_alignment.py \
  --src $(SRC) \
  --doc $(DOC)

all: sync validate

sync: ## Propose/apply Map updates from Terrain
	$(SYNC_CMD)

validate: ## Enforce Map/Terrain alignment (Physics)
	$(VALIDATE_CMD)
