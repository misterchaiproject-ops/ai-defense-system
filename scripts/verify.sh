#!/usr/bin/env bash
# Self-Verify: Full verification before push.
# Combines fix + check.
set -euo pipefail

echo "▶ Layer 3: Self-Verify"
echo "======================"

echo ""
echo "Step 1: Apply safe fixes..."
./scripts/fix.sh

echo ""
echo "Step 2: Full diagnosis..."
./scripts/check.sh

echo ""
echo "🎉 Verification complete. Safe to push."
