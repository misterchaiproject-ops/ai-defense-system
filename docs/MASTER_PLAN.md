# AI Defense System — Master Plan

**Version:** 2.3
**Status:** Active
**Date:** 2026-10-01
**Timeline:** 12-18 months (realistic)
**Reference:** NIST SP 800-53, OWASP ACS, IETF PQC, EU AI Act, CRA

---

## Vision

Build the first open-source **Semantic Defense Layer** for AI agents,
running above execution layers (NVIDIA OpenShell), compliant with
NIST COSAiS, OWASP ACS, and IETF standards.

---

## Six Non-Negotiable Principles

1. No code without full understanding.
2. Tests precede code.
3. Security is architectural.
4. Documentation is part of code.
5. Assume breach.
6. Assume independent verification.

---

## Current Phase: Phase 3.5 (Self-Healing Foundation)

**Active work:**
- G5.2: Audit logging integration in `verify_message` (deferred from Phase 3)
- Self-Healing L3: Auto-Test Retry + Cache Rebuild
- Self-Healing L4: Runtime Circuit Breakers

**Recently completed (Phase 3 + 3.5):**
- G1 (Replay SQLite), G2 (Key Ring), G5 (Audit Log), G5.1 (Audit MVP)
- Self-Healing L1 (`make doctor`), L2 (`safe-commit.sh V2`)
- DevContainer for reproducible environments

### Progress

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| src/contracts/proposal.py | 31 | 100% | DONE |
| src/contracts/agent_identity.py | 0 | 0% | IN PROGRESS |
| src/contracts/validation_result.py | 0 | 0% | PENDING |
| src/contracts/reason_codes.py | 0 | 0% | PENDING |
| src/contracts/actions.py | 0 | 0% | PENDING |
| src/contracts/roles.py | 0 | 0% | PENDING |
| src/guardrail/core.py | 0 | 0% | PENDING |
| src/channel/core.py | 0 | 0% | PENDING |
| src/orchestrator/core.py | 0 | 0% | PENDING |
| tests/test_smoke.py | 13 | smoke | DONE |
| **Total** | **44** | **~50%** | **27% of target** |

**Target:** 160 tests, 90% coverage, CI enforced.

---

## Roadmap (14 Stages, 12-18 months)

| Stage | Focus | Timeline | Status |
|-------|-------|----------|--------|
| 1   | Foundation hardening     | Month 1     | DONE    |
| 2   | Expand tests             | Month 1-2   | DONE    |
| 2.5 | Standards & threat model | Month 2     | DONE    |
| 3   | Architectural fixes (G1,G2,G5,G5.1) | Month 2-3 | DONE |
| 4 | Comprehensive docs | Month 3 | PENDING |
| 5 | Performance benchmarks | Month 3 | PENDING |
| 6 | Red Team Agent | Month 4-5 | PENDING |
| 6.5 | NVIDIA OpenShell integration | Month 5 | PENDING |
| 7 | Advanced features (Audit, Keys, PQC) | Month 6-8 | PENDING |
| 8 | Standards & interop | Month 8-9 | PENDING |
| 8.5 | SPIFFE/SPIRE + OpenShell deep | Month 9 | PENDING |
| 9 | Academic output (White Paper) | Month 10-11 | PENDING |
| 9.5 | Independent evaluation (AMTSO) | Month 11 | PENDING |
| 10 | Commercial (Pitch, partnerships) | Month 11-12 | PENDING |
| 10.5 | EU Horizon Application | Month 12 | PENDING |
| 11 | Ethics & legal | Parallel | PENDING |
| 12 | Incident Response | Month 3 | PENDING |
| 13 | EU AI Act + CRA compliance | Month 7-8 | PENDING |
| 14 | Standardization (IETF/OWASP) | Month 12+ | PENDING |

---

## Deferred (explicit)

- Formal Verification (TLA+, Z3): Month 10+
- SPIFFE/SPIRE: Month 6+ (simple Cryptographic IDs now)
- Multi-process (Redis): Month 9+
- EU Horizon Application: Month 12
- Full IETF standardization: Year 2

---

## Target Standards (priority order)

1. OWASP ACS (Agentic Control Standard)
2. NIST COSAiS (overlays on SP 800-53)
3. AMTSO (independent testing)
4. IETF PQC (identity + timestamps)
5. EU AI Act + CRA

---

## Success Metrics

- **Technical:** ASR < 5%, 90% coverage, 0 issues
- **Academic:** White Paper + Open Dataset
- **Standard:** OWASP ACS alignment
- **Commercial:** Sustainable business model
- **Community:** Adoption by 3+ external projects

---

## Recent Milestones

- 2026-10-01: Migrated to src/ layout
- 2026-10-01: 31 tests for proposal.py (100% coverage)
- 2026-10-01: CI/CD operational
- 2026-10-01: Constitution v1.0 drafted

---

## References

- NIST SP 800-53 Rev.5
- NIST COSAiS (2026)
- OWASP ACS (2026)
- IETF PQC Drafts (2026)
- EU AI Act (2026)
- NVIDIA OpenShell (2026)
- AMTSO Standard (2026)
- OATS Framework (2026)

---

**End of Master Plan v2.3**
