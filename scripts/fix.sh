#!/usr/bin/env bash
# Self-Fix: Run ALL safe automatic fixes.
# Aligned with .pre-commit-config.yaml hooks.
set -euo pipefail

echo "▶ Layer 1: Self-Fix"
echo "===================="

echo "  1. Formatting code (ruff format)..."
uv run ruff format .

echo "  2. Auto-fixing lints (ruff check --fix)..."
uv run ruff check --fix .

echo "  3. Verifying no safe fixes remain (ruff check)..."
uv run ruff check .

echo ""
echo "  4. Running pre-commit hooks on all files..."
echo "     (this catches trailing-whitespace, end-of-file-fixer, etc.)"
uv run pre-commit run --all-files || {
    echo ""
    echo "  ⚠️  Some hooks modified files. Re-running to confirm..."
    uv run pre-commit run --all-files
}

echo ""
echo "✅ All safe fixes applied."
echo "   Now run scripts/check.sh for full diagnosis."
