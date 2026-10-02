#!/bin/bash
# Automated API Inspector
# Usage: ./scripts/show_api.sh <path/to/file.py>
# Shows: classes, methods, functions, and their signatures.

if [ -z "$1" ]; then
    echo "Usage: $0 <path/to/file.py>"
    exit 1
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
    echo "Error: File $FILE not found."
    exit 1
fi

echo "═══════════════════════════════════════════════"
echo "🔍 API Inspector: $FILE"
echo "═══════════════════════════════════════════════"
echo ""
echo "📦 Module-level functions:"
grep -n "^def " "$FILE" | sed 's/^/   /'
echo ""
echo "🏛️  Classes:"
grep -n "^class " "$FILE" | sed 's/^/   /'
echo ""
echo "🔧 All methods (with their class context):"
grep -n "    def " "$FILE" | sed 's/^/   /'
echo ""
echo "═══════════════════════════════════════════════"
echo "📊 Summary:"
echo "   - Module functions: $(grep -c '^def ' "$FILE")"
echo "   - Classes: $(grep -c '^class ' "$FILE")"
echo "   - Methods: $(grep -c '    def ' "$FILE")"
echo "═══════════════════════════════════════════════"
