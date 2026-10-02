#!/bin/bash
# Automated style fixer for tests
echo "🔧 Fixing import order..."
ruff check --fix tests/unit/channel/test_core.py

echo "✅ Checking types..."
mypy --strict tests/unit/channel/test_core.py

echo "🎉 Done. Review changes with: git diff"
