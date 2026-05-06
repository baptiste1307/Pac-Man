PYTHON = python3
DEPENDENCIES = mypy flake8
MAIN = pac-man.py
CONFIG = config.json

install:
	$(PYTHON) -m pip install $(DEPENDENCIES)

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} \;
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .venv
	rm -rf data/output
	find . -type d -name "*.egg-info" -exec rm -rf {} \;

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

.PHONY: install run debug test clean lint lint-strict