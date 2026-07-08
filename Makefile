PYTHON = python3
WHL_FILE = mazegenerator-00001-py3-none-any.whl
MAIN = pac-man.py
CONFIG = config.json
RM = rm -rf
SYNC = uv sync
RUN= uv run


install:
	@$(SYNC)
	@if [ ! -d mazegenerator ]; then \
		unzip -o $(WHL_FILE); \
	fi

run: install
	@PYTHONDONTWRITEBYTECODE=1 $(RUN) $(PYTHON) $(MAIN) $(CONFIG)

debug: install
	@PYTHONDONTWRITEBYTECODE=1 $(RUN) $(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean: install
	@find . -depth -type d -name "__pycache__" -exec $(RM) {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -depth -type d -name "*.egg-info" -exec $(RM) {} + 2>/dev/null || true
	@$(RM) .mypy_cache
	@$(RM) .pytest_cache
	@$(RM) venv
	@$(RM) .venv
	@$(RM) data/output
	@$(RM) scores.json
# 	@$(RM) mazegenerator
# 	@$(RM) mazegenerator-2.0.1.dist-info
# automatically generated files while creating .zip
	@$(RM) dist/
	@$(RM) build/
	@$(RM) PacMan.spec

lint: install
	@$(RUN) $(PYTHON) -m flake8 .
	@$(RUN) $(PYTHON) -m mypy . \
		--warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict: install
	@$(RUN) $(PYTHON) -m flake8 .
	@$(RUN) $(PYTHON) -m mypy . --strict

.PHONY: install run debug test clean lint lint-strict unzip
