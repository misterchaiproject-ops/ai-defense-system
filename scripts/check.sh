#!/usr/bin/env bash
# Self-Diagnose: Run all checks (no auto-fix).
# Reports every problem in one unified view.
set +e  # Do not exit on first failure — show everything

echo "▶ Layer 2: Self-Diagnose"
echo "========================"

FAILED=0

echo ""
echo "[1/4] ruff check (lint)..."
if ! uv run ruff check .; then
    echo "     ❌ Fix with: ./scripts/fix.sh"
    FAILED=1
else
    echo "     ✅ Clean"
fi

echo ""
echo "[2/4] mypy --strict (types)..."
if ! uv run mypy src/contracts src/guardrail src/channel src/orchestrator tests --strict; then
    echo "     ❌ Manual review required"
    FAILED=1
else
    echo "     ✅ Clean"
fi

echo ""
echo "[3/4] bandit (security)..."
if ! uv run bandit -r src/contracts src/guardrail src/channel src/orchestrator -q; then
    echo "     ❌ Security issues found"
    FAILED=1
else
    echo "     ✅ No issues"
fi

echo ""
echo "[4/4] pytest (tests)..."
if ! uv run pytest -q; then
    echo "     ❌ Tests failed"
    FAILED=1
else
    echo "     ✅ All passing"
fi

echo ""
echo "========================"
if [ $FAILED -eq 0 ]; then
    echo "🎉 All checks passed. Ready to push."
    exit 0
else
    echo "⚠️  Some checks failed. Review output above."
    exit 1
fi
