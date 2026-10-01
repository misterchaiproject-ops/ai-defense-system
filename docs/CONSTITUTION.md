# The Technical Constitution

**Version:** 1.0
**Date:** 2026-10-01
**Status:** Mandatory — applies to every project
**Source:** Derived from AI Defense System experience

---

## Purpose

This document defines the non-negotiable principles, protocols, and
standards that govern every technical project. It is a living
document — updated with every new lesson learned.

**It complements, not replaces:**
- `docs/MASTER_PLAN.md` — project roadmap
- `docs/LESSONS_LEARNED.md` — hard-won lessons
- `docs/VERIFICATION_PROTOCOL.md` — verification rules

---

## The Six Non-Negotiable Principles

### Principle 1: No Code Without Full Understanding
Every line must be explainable. No copy-paste from unexplained
sources. No AI-generated code without line-by-line review.

### Principle 2: Tests Precede Code
Every new function has at least one test. TDD is not a luxury —
it is a requirement. No `git push` without passing tests.

### Principle 3: Security is Architectural
Security is not a feature added later. Fail-Closed by default.
Zero Trust in every layer. Immutability for sensitive data.

### Principle 4: Documentation is Part of Code
Every important decision has a document. Every function has a
docstring. Every lesson is recorded in `LESSONS_LEARNED.md`.

### Principle 5: Assume Breach
Design the system assuming every layer may be compromised.
Defense in Depth (≥ 3 layers). Continuous internal Red Team.
Blast Radius Limitation. Incident Response Plan.

### Principle 6: Independent Verification is Mandatory
Every security claim must be verifiable by a third party.
No single-source trust. At least 3 independent sources
before accepting any important decision.

---

## The Golden Rule

> **Do not trust a single source. Do not trust yourself.**
> **Verify from at least 3 independent sources,**
> **then make your system verify itself.**

---

## Pre-Push Checklist (Mandatory)

Before every `git push`, run these commands in order:

```bash
# 1. Format
uv run ruff format .

# 2. Lint
uv run ruff check .

# 3. Type check (strict)
uv run mypy --strict <packages>

# 4. Security scan
uv run bandit -r <packages> -q

# 5. Tests
uv run pytest -v

# 6. Coverage
uv run pytest --cov=<packages> --cov-report=term-missing


**Required outcomes:**
- `All checks passed` for ruff
- `Success: no issues found` for mypy
- `No issues identified` for bandit
- `X passed` for pytest
- Coverage ≥ 80% (target: 90%)

**Rule:** If any fails → do NOT push. Fix first.

---

## File Creation Protocol

### For files < 30 lines

```bash
cat > path/to/file.py << 'EOF'
# content
EOF
cat >> docs/CONSTITUTION.md << 'ENDOFFILE'

---

## References to Other Documents

This Constitution is the parent document. For details, see:

- **`docs/MASTER_PLAN.md`** — project roadmap and phases
- **`docs/LESSONS_LEARNED.md`** — hard-won lessons and protocols
- **`docs/VERIFICATION_PROTOCOL.md`** — detailed verification rules
- **`docs/ANTI_PATTERNS.md`** (planned) — rejected patterns registry
- **`docs/ARCHITECTURE.md`** (planned) — system architecture
- **`docs/THREAT_MODEL.md`** (planned) — threat modeling

---

## The Seven Preventive Protocols (Summary)

For full details, see `LESSONS_LEARNED.md`:

1. **Verify-After-Modify** — check after every change
2. **Chunked-Paste** — never paste > 80 lines
3. **Local-First Verification** — run all checks before push
4. **Read-Before-Write** — read files before editing
5. **Cross-Verify with AI** — get a second opinion
6. **Rollback-Ready** — backup before major changes
7. **Document-Learned-Lessons** — record every failure

---

## Rejected Patterns (Summary)

For full registry, see `LESSONS_LEARNED.md` and upcoming `ANTI_PATTERNS.md`:

- AP-001 to AP-015: Core patterns (see `LESSONS_LEARNED.md`)
- AP-016: Iterate before size-check on collections
- AP-017: Reveal regex patterns in error messages
- AP-018: Echo raw user input in exceptions
- AP-019: `in` operator on StrEnum without isinstance

---

## Commitment

Every contributor commits to:

1. Read this Constitution before starting any project.
2. Apply the Pre-Push Checklist on every push.
3. Use the File Creation Protocol.
4. Document new lessons in `LESSONS_LEARNED.md`.
5. Request AI cross-verification after every module.
6. Never bypass any of the Six Principles.
7. Report any vulnerability or error immediately.
8. Keep the repository clean and documented.

---

## Closing

**This Constitution is a living document.**

- Updated with every new lesson.
- Extended with every new technology.
- Hardened with every repeated error.
- Simplified when complexity grows.

**Supreme purpose:**
Build clean, secure, maintainable, and long-lived projects.

---

**End of Constitution v1.0**
