.PHONY: install test test-login test-auth test-refresh test-products \
        lint flake8 mypy isort-check format black isort \
        check report clean help

PYTHON     := python
PYTEST     := pytest
SRC_DIRS   := clients config utils tests
REPORT_DIR := reports

# ------------------------------------------------------------------------------
# Install
# ------------------------------------------------------------------------------

install:
	pip install -r requirements.txt
	pip install black flake8 mypy isort

# ------------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------------

test:
	$(PYTEST)

test-login:
	$(PYTEST) tests/test_login.py -v

test-auth:
	$(PYTEST) tests/test_auth_me.py -v

test-refresh:
	$(PYTEST) tests/test_token_refresh.py -v

test-products:
	$(PYTEST) tests/test_products.py -v

report:
	@mkdir -p $(REPORT_DIR)
	$(PYTEST) --html=$(REPORT_DIR)/report.html --self-contained-html
	@echo "Report generated: $(REPORT_DIR)/report.html"

# ------------------------------------------------------------------------------
# Quality checks
# ------------------------------------------------------------------------------

mypy:
	@echo ">>> Running mypy (type checking)..."
	mypy $(SRC_DIRS) \
		--ignore-missing-imports \
		--exclude __pycache__


# ------------------------------------------------------------------------------
# Auto-format
# ------------------------------------------------------------------------------

ruff-format:
	@echo ">>> Formatting with ruff..."
	$(PYTHON) -m ruff format $(SRC_DIRS)

ruff-check:
	@echo ">>> Linting with ruff..."
	$(PYTHON) -m ruff check $(SRC_DIRS) --fix

format: ruff-format ruff-check
	@echo ">>> Code formatted!"

