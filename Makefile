.PHONY: fix check verify test cov clean

fix:
	@./scripts/fix.sh

check:
	@./scripts/check.sh

verify:
	@./scripts/verify.sh

test:
	@uv run pytest -v

cov:
	@uv run pytest --cov=contracts --cov=guardrail --cov=channel --cov=orchestrator --cov-report=term-missing --cov-fail-under=80

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."
