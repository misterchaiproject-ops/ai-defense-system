#!/usr/bin/env bash
# safe-commit.sh — atomic commit pipeline: fix -> check -> commit -> push.
# Usage: ./scripts/safe-commit.sh "subject" ["body"]
#        ./scripts/safe-commit.sh --dry-run "subject" ["body"]
#        ./scripts/safe-commit.sh -h | --help

set -euo pipefail

DRY_RUN=0

show_help() {
    cat <<'HELP'
Usage: safe-commit.sh [--dry-run] "subject" ["body"]

Atomic pipeline:
  1/5 Pre-flight  (no .bak files, changes present)
  2/5 Auto-fix    (ruff --fix + format)
  3/5 Verify      (make check, 6 steps)
  4/5 Commit      (git add -A + commit)
  5/5 Push        (git push)

Options:
  --dry-run    Run steps 1-3 only; skip commit and push.
  -h, --help   Show this help.
HELP
}

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) show_help; exit 0 ;;
        *) break ;;
    esac
done

if [ $# -eq 0 ]; then
    echo "ERROR: commit subject required."
    show_help
    exit 1
fi

SUBJECT="$1"
BODY="${2:-}"

# --- Step 1/5: Pre-flight ---
echo ">> Step 1/5: Pre-flight"

BAK_FILES=$(find . -name '*.bak' -not -path './.git/*' 2>/dev/null || true)

# Blocklist: refuse accidental files
BLOCKED_FILES=""
for pattern in '^=$' '\.swp$' '~$' '\.DS_Store$' '\.orig$' '\.tmp$'; do
    matches=$(git status --porcelain | awk '{print $2}' | grep -E "$pattern" || true)
    if [ -n "$matches" ]; then
        BLOCKED_FILES="${BLOCKED_FILES}${matches}"$'\n'
    fi
done
if [ -n "$BLOCKED_FILES" ]; then
    echo "ERROR: found accidental file(s) that must not be committed:"
    echo "$BLOCKED_FILES"
    exit 1
fi

if [ -z "$(git status --porcelain)" ]; then
    echo "ERROR: no changes to commit (working tree clean)."
    exit 1
fi
if [ -n "$BAK_FILES" ]; then
    echo " OK: detected .bak files (will auto-clean after verify)"
else
    echo " OK: no .bak files, changes detected"
fi

# --- Step 2/5: Auto-fix ---
echo ""
echo ">> Step 2/5: Auto-fix"
if ! ./scripts/fix.sh; then
    echo "ERROR: fix.sh failed"
    exit 1
fi

# --- Step 3/5: Verify ---
echo ""
echo ">> Step 3/5: Verify"
if ! ./scripts/check.sh; then
    echo "ERROR: check.sh failed (.bak files kept for rollback)"
    exit 1
fi

# Auto-cleanup .bak files (only on success, only if not dry-run)
if [ -n "$BAK_FILES" ] && [ "$DRY_RUN" -eq 0 ]; then
    echo ""
    echo ">> Auto-cleanup: removing .bak files"
    while IFS= read -r f; do
        if [ -n "$f" ]; then
            rm -f "$f" && echo "   removed: $f"
        fi
    done <<< "$BAK_FILES"
fi

if [ "$DRY_RUN" -eq 1 ]; then
    echo ""
    echo "DRY-RUN OK: pre-flight + fix + check passed. Commit/push skipped."
    exit 0
fi

# --- Step 4/5: Commit ---
echo ""
echo ">> Step 4/5: Commit"
git add -A
if [ -n "$BODY" ]; then
    git commit -m "$SUBJECT" -m "$BODY"
else
    git commit -m "$SUBJECT"
fi

# --- Step 5/5: Push ---
echo ""
echo ">> Step 5/5: Push"
git push

echo ""
echo "SUCCESS: committed and pushed."
