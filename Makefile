# --- L9_META ---
# l9_schema: 1
# origin: l9-deployment-platform
# layer:
# - repository
# tags:
# - L9_META
# - deployment-platform
# owner: platform
# status: active
# --- /L9_META ---
.PHONY: sync format lint typecheck test coverage contracts workflows metadata contract-scan alignment shell-syntax compile validate release-clean release-artifacts release-pack-check release-prepare release-archive package clean

sync:
	uv sync --all-extras --frozen

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

typecheck:
	uv run mypy src/l9_deploy

test:
	uv run pytest -q --cov=l9_deploy --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=75

coverage:
	uv run pytest -q --cov=l9_deploy --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=75

contracts:
	uv run python scripts/validate-contracts.py

workflows:
	uv run python scripts/validate-workflows.py

metadata:
	uv run python scripts/verify-l9-meta.py

contract-scan:
	uv run python scripts/fast-contract-scan.py

alignment:
	uv run python scripts/validate-alignment.py

shell-syntax:
	bash -n scripts/*.sh

compile:
	uv run python -m compileall -q src scripts

validate: lint typecheck test contracts workflows metadata contract-scan alignment shell-syntax compile

release-clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov build dist .coverage coverage.xml
	rm -f artifacts/coverage.xml
	find src tests scripts -type d -name __pycache__ -prune -exec rm -rf {} +
	find src tests scripts -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

release-artifacts: release-clean
	PYTHONDONTWRITEBYTECODE=1 uv run python scripts/generate-release-artifacts.py

release-pack-check:
	PYTHONDONTWRITEBYTECODE=1 uv run python scripts/validate-release-pack.py

release-prepare: release-artifacts release-pack-check

ARCHIVE ?= ../l9-deployment-platform.zip
RECEIPT ?= $(ARCHIVE:.zip=.receipt.json)
DIST_DIR ?= ../l9-deployment-platform-dist
release-archive: release-prepare
	PYTHONDONTWRITEBYTECODE=1 uv run python scripts/build-release-archive.py --output "$(ARCHIVE)" --receipt "$(RECEIPT)"
	PYTHONDONTWRITEBYTECODE=1 uv run python scripts/validate-release-pack.py --archive "$(ARCHIVE)" --receipt "$(RECEIPT)"

package:
	uv build --out-dir "$(DIST_DIR)"

clean:
	rm -rf .venv dist build .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	rm -f artifacts/coverage.xml
	find src tests scripts -type d -name __pycache__ -prune -exec rm -rf {} +
