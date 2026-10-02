#!/usr/bin/env bash
# Self-Diagnose: Run all checks (no auto-fix).
# Reports every problem in one unified view.
set +e  # Do not exit on first failure - show everything

echo ">> Layer 2: Self-Diagnose"
echo "=========================="

FAILED=0

echo ""
echo "[1/5] ruff check (lint)..."
if ! uv run ruff check .; then
    echo "  FAIL: Fix with ./scripts/fix.sh"
    FAILED=1
else
    echo "  OK: Clean"
fi

echo ""
echo "[2/5] mypy --strict (types)..."
if ! uv run mypy src/contracts src/guardrail src/channel src/orchestrator tests --strict; then
    echo "  FAIL: Manual review required"
    FAILED=1
else
    echo "  OK: Clean"
fi

echo ""
echo "[3/5] bandit (security)..."
if ! uv run bandit -r src/contracts src/guardrail src/channel src/orchestrator -q; then
    echo "  FAIL: Security issues found"
    FAILED=1
else
    echo "  OK: No issues"
fi

echo ""
echo "[4/5] pip-audit (dependencies)..."
if ! uv run pip-audit; then
    echo "  FAIL: Vulnerable dependencies found"
    FAILED=1
else
    echo "  OK: No vulnerabilities"
fi

echo ""
echo "[5/5] pytest (tests)..."
if ! uv run pytest -q; then
    echo "  FAIL: Tests failed"
    FAILED=1
else
    echo "  OK: All passing"
fi

echo ""
echo "=========================="
if [ $FAILED -eq 0 ]; then
    echo "SUCCESS: All checks passed. Ready to push."
    exit 0
else
    echo "WARNING: Some checks failed. Review output above."
    exit 1
fi
