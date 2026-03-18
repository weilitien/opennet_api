
.PHONY: install test test-login test-products \
        lint ruff-check mypy format ruff-format \
        check report clean help

PYTHON     := python
PYTEST     := $(PYTHON) -m pytest
RUFF       := $(PYTHON) -m ruff
MYPY       := $(PYTHON) -m mypy

SRC_DIRS   := clients config utils tests
REPORT_DIR := reports

# ------------------------------------------------------------------------------
# Install
# ------------------------------------------------------------------------------

install:
	pip install -r requirements.txt

# ------------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------------

test:
	$(PYTEST)

test-login:
	$(PYTEST) tests/test_login.py -v

test-products:
	$(PYTEST) tests/test_products.py -v

report:
	@mkdir -p $(REPORT_DIR)
	$(PYTEST) --html=$(REPORT_DIR)/report.html --self-contained-html
	@echo "Report generated: $(REPORT_DIR)/report.html"

# ------------------------------------------------------------------------------
# Quality checks
# ------------------------------------------------------------------------------

ruff-check:
	@echo ">>> Running ruff (lint)..."
	$(RUFF) check $(SRC_DIRS)

mypy:
	@echo ">>> Running mypy (type checking)..."
	$(MYPY) $(SRC_DIRS) \
		--ignore-missing-imports \
		--exclude __pycache__

# ------------------------------------------------------------------------------
# Auto-format
# ------------------------------------------------------------------------------

ruff-format:
	@echo ">>> Formatting with ruff..."
	$(RUFF) format $(SRC_DIRS)
	$(RUFF) check $(SRC_DIRS) --fix

format: ruff-format
	@echo ">>> Code formatted!"

# ------------------------------------------------------------------------------
# Combined (CI-ready)
# ------------------------------------------------------------------------------

check: format lint test
	@echo ">>> All checks passed!"

# ------------------------------------------------------------------------------
# Clean
# ------------------------------------------------------------------------------

clean:
	@echo ">>> Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache  -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf $(REPORT_DIR)
	@echo ">>> Clean done!"

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install all dependencies"
	@echo "  make test           Run all tests"
	@echo "  make test-login     Run only test_login.py"
	@echo "  make test-products  Run only test_products.py"
	@echo "  make report         Run tests + generate HTML report in reports/"
	@echo "  make ruff-check     Lint with ruff"
	@echo "  make mypy           Type checking"
	@echo "  make lint           ruff-check + mypy"
	@echo "  make format         Auto-format with ruff"
	@echo "  make check          format + lint + test (run before committing)"
	@echo "  make clean          Remove __pycache__, .mypy_cache, .ruff_cache, reports/"
	@echo ""
