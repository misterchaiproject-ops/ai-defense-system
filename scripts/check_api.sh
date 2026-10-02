#!/usr/bin/env bash
# check_api.sh — Verify that ClassName.method() calls in a test file
# actually exist in the source file. Prevents AttributeError at test time.
# Uses Python AST (safe, does not execute code).
set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: $0 <test_file.py> <source_file.py>"
    exit 1
fi

TEST_FILE="$1"
SRC_FILE="$2"

if [ ! -f "$TEST_FILE" ]; then
    echo "Error: test file not found: $TEST_FILE"
    exit 1
fi

if [ ! -f "$SRC_FILE" ]; then
    echo "Error: source file not found: $SRC_FILE"
    exit 1
fi

python3 - "$TEST_FILE" "$SRC_FILE" << 'PYEOF'
import ast
import re
import sys

test_path, src_path = sys.argv[1], sys.argv[2]

with open(src_path, "r", encoding="utf-8") as f:
    src_tree = ast.parse(f.read(), filename=src_path)

# Build map: class_name -> set of method names
class_methods: dict[str, set[str]] = {}
for node in src_tree.body:
    if isinstance(node, ast.ClassDef):
        methods = set()
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.add(item.name)
        class_methods[node.name] = methods

if not class_methods:
    print("No classes found in source. Nothing to check.")
    sys.exit(0)

# Scan test file for ClassName.method_name patterns
with open(test_path, "r", encoding="utf-8") as f:
    test_content = f.read()

pattern = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\.([a-z_][A-Za-z0-9_]*)\s*\(")
errors = []

for match in pattern.finditer(test_content):
    cls, method = match.group(1), match.group(2)
    if cls in class_methods and method not in class_methods[cls]:
        line_no = test_content[: match.start()].count("\n") + 1
        errors.append(f"  ❌ line {line_no}: {cls}.{method}() — '{method}' not found in class '{cls}'")

print(f"Classes found in {src_path}:")
for cls, methods in class_methods.items():
    print(f"  - {cls}: {sorted(methods)}")
print()

if errors:
    print("API Check FAILED:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print("✅ All ClassName.method() calls are valid.")
PYEOF
