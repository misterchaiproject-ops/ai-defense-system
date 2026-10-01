# Verification Protocol

**Version:** 1.0
**Date:** 2026-10-01
**Status:** Mandatory — enforced on every contribution

---

## The Golden Rule

> **Do not trust a single source. Do not trust yourself.**
> **Verify from at least 3 independent sources,**
> **then make your system verify itself.**

---

## Part 1: Rules for Code Authors

### Rule 1.1: No code without tests
Every new function is accompanied by at least one test.

### Rule 1.2: No code without full understanding
- Every line must be explainable.
- No copy-paste from unexplained sources.
- No AI-generated code without line-by-line review.

### Rule 1.3: No code without automated checks
Before submitting, code must pass:
- `mypy --strict` (0 errors)
- `ruff check` (0 warnings)
- `ruff format --check` (0 diffs)
- `bandit -r` (0 issues)
- `pytest` (all passing)

### Rule 1.4: No code without explicit types
- Every function has complete type hints.
- Every `dict`/`list` has a specified type.
- No `Any` without documented justification.

### Rule 1.5: No code without comments on non-obvious decisions
- If a line is unclear, comment it.
- If a decision is intentional, comment it.
- If a check is defensive, comment it.

---

## Part 2: Rules for Reviewers

### Rule 2.1: Ruthless critique, no praise
Reviewers look for problems, not to confirm correctness.

### Rule 2.2: Five verification methods

#### Method 1: Automated tools (strongest)
- `pytest` — does it work?
- `mypy --strict` — are types correct?
- `ruff check` — is style correct?
- `bandit` — any vulnerabilities?

**If any tool fails → reject the code.**

#### Method 2: Cross-verification with another AI
- Send the code to an independent AI (Gemini, Claude, GPT).
- Request explicit critique, not affirmation.
- Compare results.

#### Method 3: Comparison with official docs
- docs.python.org
- docs.astral.sh/uv
- nist.gov (for security)
- peps.python.org (for standards)

#### Method 4: "External auditor" — explicit critique request
When sending code to AI, the request must be:

#### Method 5: Adversarial scenario testing
- "What if a `NaN` value is sent?"
- "What if the same message is resent 1000 times?"
- "What if `sender_id` is changed to `admin`?"

---

## Part 3: The Mandatory Checklist

After every new code:

- [ ] **`pytest` passes?**
- [ ] **`mypy --strict` passes?**
- [ ] **`ruff check` passes?**
- [ ] **`ruff format --check` passes?**
- [ ] **`bandit -r` passes?**
- [ ] **External AI reviewer confirms correctness?**
- [ ] **Author understands every line?**
- [ ] **Every function has type hints?**
- [ ] **Every function has at least one test?**

**If all "yes" → 95% confidence.**
**If any "no" → do not proceed until fixed.**

---

## Part 4: Red Flags (Stop and Ask)

**If any of these appear, stop and ask:**

| Red Flag | Meaning |
|----------|---------|
| "Trust me" | No professional says this |
| "This is complex, you don't need to understand it" | Hides a problem |
| "It works only on my machine" | Not real |
| "No time to test this" | Recipe for disaster |
| "Don't worry about the warnings" | Warnings matter |
| "I know what I'm doing" | Claim without proof |
| Ignoring questions | Danger sign |

**On any Red Flag:**
1. Stop.
2. Request clear explanation.
3. Verify from an independent source.
4. Do not proceed until resolved.

---

## Part 5: Project Health Indicators

### Objective Indicators

| Indicator | Healthy Value | How to check |
|-----------|---------------|--------------|
| Number of tests | Increasing | `pytest` |
| Test coverage | ≥ 80% | `pytest --cov` |
| mypy errors | 0 | `mypy --strict` |
| ruff warnings | 0 | `ruff check` |
| bandit issues | 0 | `bandit -r` |
| Number of commits | Growing logically | `git log` |
| Number of files | Growing logically | Compare to plan |

### Signs of Healthy Progress

- Every session adds something new.
- Every session fixes new problems (not the same ones).
- Tests increase.
- Code gets simpler, not more complex.

### Signs of Stall

- We fix the same errors every session.
- We add code without tests.
- We hide problems instead of solving them.
- We ignore tool warnings.

---

## Part 6: Commitments

Every code author (human or AI) commits to:

1. **Honesty** — never hide mistakes.
2. **Acknowledging ignorance** — if I don't know, I say so.
3. **Requesting cross-verification** — will ask another AI for review.
4. **Relying on tools** — will never ignore them.
5. **Working step by step** — will not rush.
6. **Requesting stop** — if code needs review before continuing.

### What I cannot guarantee:

1. **Perfection** — I will make mistakes.
2. **Optimal solution always** — may miss improvements.
3. **Absolute security** — no system is 100% secure.
4. **Compatibility with every environment** — every device differs.

---

## Part 7: Session Protocol

### Before the session:
- [ ] All automated checks pass.
- [ ] No pending changes.
- [ ] `git status` is clean.

### During the session:
- [ ] Every step is tested immediately.
- [ ] Every code is reviewed by another AI (Gemini).
- [ ] No rushing.

### After the session:
- [ ] All automated checks pass.
- [ ] Changes pushed to GitHub.
- [ ] Session documented in `docs/SESSION-XXX.md`.

---

**End of Verification Protocol v1.0**
