#!/usr/bin/env bash
# Self-Fix: Run safe automatic fixes.
# Never touches tests, never touches logic, never touches security.
set -euo pipefail

echo "▶ Layer 1: Self-Fix"
echo "===================="

echo "  1. Formatting code..."
uv run ruff format .

echo "  2. Auto-fixing lints (imports, style)..."
uv run ruff check --fix .

echo "  3. Verifying no safe fixes remain..."
uv run ruff check .

echo ""
echo "✅ Safe fixes applied. Now run scripts/check.sh for full diagnosis."
