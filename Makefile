PYTHON ?= python3

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[dev]
	$(PYTHON) -m pip install black ruff mypy mkdocs mkdocs-material

format:
	$(PYTHON) -m black src

format-check:
	$(PYTHON) -m black --check src

lint:
	$(PYTHON) -m ruff check src

lint-fix:
	$(PYTHON) -m ruff check src --fix

type:
	$(PYTHON) -m mypy src

# format-docs: # does weird line splits, can't make it dumb to just wrap at 88 chars or ignore what I've already formatted
# 	docformatter -i -r --wrap-summaries 88 --wrap-descriptions 88 src

report-default:
	$(PYTHON) -m flights report --config examples/test.json

report-json:
ifndef CONFIG_JSON
	$(error CONFIG_JSON is required)
endif
	$(PYTHON) -m flights report --config-json "$$CONFIG_JSON"

build-site:
	$(PYTHON) -m mkdocs build

serve-site:
	$(PYTHON) -m mkdocs serve

check: format-check lint type
ci: install check report-default build-site
local-run: report-default build-site serve-site
