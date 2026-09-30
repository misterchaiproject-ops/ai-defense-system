# Review 003 — Post-MVP Assessment

**Date:** 2026-09-30
**Reviewer:** Gemini (independent AI review)
**Scope:** MVP v0.1 (contracts, guardrail, channel, orchestrator)
**Status:** Accepted — Action items defined

---

## Summary

After successfully deploying MVP v0.1 to GitHub with 13 passing tests,
an independent review was conducted. The verdict:

> Core code is sound. Security for MVP is sufficient. But gaps exist
> that must be closed before expanding to additional layers.

---

## Strengths Confirmed

1. **Core logic is architecturally sound.** The `_ACTION_ROLES` matrix
   and RBAC rules in `DeterministicGuardrail` are watertight.

2. **Input hardening works.** `Envelope.__post_init__` and
   `DeterministicGuardrail` effectively block NaN, Inf, and log injection.

3. **Mandatory validation enforced.** `SecureOrchestrator` correctly
   requires validation on both outbound and inbound flows.

4. **Fast execution.** 13 tests pass in 0.06 seconds — efficient design.

---

## Critical Findings

### Finding 1: In-Memory ReplayCache (Critical)

**Location:** `channel/core.py` → `_ReplayCache`

**Issue:** The replay cache is in-memory only. On restart, all recorded
nonces are lost, enabling replay attacks after any process restart.

**Impact:** Production-blocking.

**Mitigation (future):** Redis or persistent store. Not required for MVP.

### Finding 2: Minimal pyproject.toml (High)

**Location:** `pyproject.toml`

**Issue:** Missing mypy, ruff, bandit, pytest-cov configurations.
No static type checking, no lint, no automated security scan.

**Impact:** Technical debt accumulates without automated checks.

**Mitigation (this sprint):** Add tool configs and enable strict mode.

### Finding 3: Few Tests (High)

**Location:** `tests/`

**Issue:** 13 tests cover smoke-level scenarios only. No property-based,
no performance, no adversarial, no network tests.

**Impact:** Limited regression coverage.

**Mitigation (future sprints):** Add hypothesis, benchmarks, TCP tests.

---

## Decision: Priority = Harden Before Expand

After review, the decision is:

> **Option B wins.** Harden the current MVP before adding new layers
> (Audit, Keys, PQC). Depth matters more than breadth.

### Rationale

- A weak foundation makes every future layer unsafe.
- Static analysis catches errors that tests miss.
- Strict typing prevents entire classes of bugs.
- Automated checks scale better than manual review.

---

## 30-Day Plan

### Sprint 1: Tooling (Week 1)
- [ ] Update `pyproject.toml` with mypy, ruff, bandit, pytest-cov.
- [ ] Run `mypy --strict` and fix all errors.
- [ ] Run `ruff check` and fix warnings.
- [ ] Run `bandit -r src` and address findings.
- [ ] Target: 0 errors, 0 warnings.

### Sprint 2: Tests Expansion (Week 2)
- [ ] Add property-based tests with `hypothesis`.
- [ ] Add boundary tests (NaN, Inf, bool, None).
- [ ] Add orchestrator TOCTOU tests.
- [ ] Target: 40+ tests, 95%+ coverage.

### Sprint 3: Documentation (Week 3)
- [ ] `docs/ARCHITECTURE.md`
- [ ] `docs/THREAT_MODEL.md`
- [ ] `docs/ANTI_PATTERNS.md` (36 patterns)
- [ ] `docs/adr/` (35 ADRs)

### Sprint 4: CI/CD (Week 4)
- [ ] GitHub Actions workflow.
- [ ] Run mypy, ruff, bandit, pytest on every push.
- [ ] Coverage report.
- [ ] Branch protection.

---

## Non-Goals (deferred)

- ❌ Audit layer
- ❌ Keys layer
- ❌ PQC (ML-DSA-65)
- ❌ Multi-process / Redis
- ❌ Docker
- ❌ Production deployment

These come **after** the foundation is hardened.

---

## References

- `docs/REVIEW-001.md` — first review (pre-MVP)
- `docs/REVIEW-002.md` — second review (post-Layer-4)
- This document — third review (post-MVP)

---

## Principles Applied

1. **Understand every line.**
2. **Tests precede code.**
3. **Security is architectural.**
4. **Documentation is part of code.**
5. **Assume breach.**

---

**End of Review 003.**
