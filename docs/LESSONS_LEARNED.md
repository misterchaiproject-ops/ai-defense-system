# Lessons Learned — AI Defense System

**Version:** 1.0
**Date:** 2026-10-01
**Status:** Living Document

Every lesson below emerged from a real failure during development.
Each one is now a mandatory rule.

---

## Lesson 1: `ruff check` ≠ `ruff format`

**What happened:** Assumed `ruff check` was enough. CI failed at
`ruff format --check`.

**Why:** `ruff` has two independent operations:
- `ruff check` — logic/style errors.
- `ruff format` — physical code layout.

**Prevention:** Run BOTH before every push.

---

## Lesson 2: Never paste > 80 lines into Terminal

**What happened:** Pasted 200+ lines. Terminal duplicated content.

**Why:** Terminal is for commands, not bulk content. Touchscreen
paste gestures may duplicate.

**Prevention:**
- Use `cat > file.py << 'EOF'` for new files.
- Paste in chunks of 30-80 lines.
- Verify each chunk visually before the next.
- Close with `EOF` on its own line.

---

## Lesson 3: Always work from repository root

**What happened:** Inside `contracts/`, typed `contracts/roles.py`.
Result: `contracts/contracts/roles.py` (nested).

**Prevention:** Run `pwd` before every file creation. `cd` to root first.

---

## Lesson 4: `# type: ignore` requires justification

**What happened:** Added `# type: ignore[arg-type]` to `value=True`.
mypy complained: "Unused type: ignore comment".

**Why:** `bool` is a subclass of `int`, and `int` is compatible
with `float`. The ignore was unnecessary.

**Prevention:** Only add `# type: ignore[code]` when:
1. mypy actually reports an error.
2. The error is a known false positive.
3. A comment explains why.

---

## Lesson 5: CI catches what local checks miss

**What happened:** CI failed twice for preventable reasons.

**Prevention:** Run the full Pre-Push Checklist BEFORE every push.
Never rely on CI to catch local mistakes.

---

## Lesson 6: Verify-after-modify

**What happened:** Assumed `sed` modified a file. It hadn't.

**Prevention:** After every file modification, run:
```bash
grep "expected_text" path/to/file.py
head -10 path/to/file.py
tail -10 path/to/file.py
git diff path/to/file.py


---

## The Master Pre-Push Checklist

```bash
uv run ruff format .        # 1. Format
uv run ruff check .          # 2. Lint
uv run mypy --strict ...     # 3. Types
uv run bandit -r ... -q      # 4. Security
uv run pytest -v             # 5. Tests


**Rule:** If any step fails, fix it before moving on.

---

## Commitment

Every contributor (human or AI) commits to:
1. Running the pre-push checklist before every push.
2. Using heredoc pattern for files > 50 lines.
3. Documenting new lessons in this file.
4. Reviewing this file at the start of each session.

---

**End of Lessons Learned v1.0**
