PYTHON = python3
BUILD_DIR = build
CACHE_DIR = $(BUILD_DIR)/cache
WHEEL_DIR = $(BUILD_DIR)/wheel
WHL_FILE = mazegenerator-00001-py3-none-any.whl
DEPENDENCIES = mypy flake8 pygame
MAIN = pac-man.py
CONFIG = config.json
MKDIR = mkdir -p
RM = rm -rf

$(BUILD_DIR):

	$(MKDIR) $(BUILD_DIR)

dirs: $(BUILD_DIR)

	$(MKDIR) $(CACHE_DIR)
	$(MKDIR) $(WHEEL_DIR)

install: dirs
	$(PYTHON) -m pip install $(DEPENDENCIES)
## $(PYTHON) -m pip install $(WHL_FILE)
	unzip $(WHL_FILE) -d $(WHEEL_DIR)
	
run:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb

clean:
	find . -depth -type d -name "__pycache__" -exec $(RM) {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -depth -type d -name "*.egg-info" -exec $(RM) {} + 2>/dev/null || true
	$(RM) .mypy_cache
	$(RM) .pytest_cache
	$(RM) venv
	$(RM) .venv
	$(RM) data/output
	$(RM) $(BUILD_DIR)

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --cache-dir $(CACHE_DIR)/mypy \
		--warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --cache-dir $(CACHE_DIR)/mypy --strict

.PHONY: install run debug test clean lint lint-strict