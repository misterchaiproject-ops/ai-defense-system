# AI Defense System — Master Plan v2.2

**Status:** Approved after Gemini review
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
6. **Assume independent verification** (new).

---

## Immediate Focus (Month 1)

### Stage 2: Expand Tests
- 13 → 85 tests
- Coverage: 40% → 90%
- Add hypothesis (property-based)
- Target: 0 regressions

### Stage 2.5: Standards & Threat Model
- Add **Indirect Prompt Injection** to threat model
- Add **Agent Memory Poisoning** to threat model
- Add **Supply Chain Attacks on Tools**
- Review OWASP ACS, map controls
- Cryptographic IDs (PQC-signed) as SPIFFE placeholder

---

## Roadmap (14 Stages, 12-18 months)

| Stage | Focus | Timeline |
|-------|-------|----------|
| 1 | Foundation hardening | ✅ Done |
| 2 | Expand tests | Month 1 |
| 2.5 | Standards & threat model | Month 1 |
| 3 | Architectural fixes | Month 2 |
| 4 | Comprehensive docs | Month 2 |
| 5 | Performance benchmarks | Month 2 |
| 6 | Red Team Agent | Month 3-4 |
| 6.5 | NVIDIA OpenShell integration | Month 4 |
| 7 | Advanced features (Audit, Keys, PQC) | Month 5-7 |
| 8 | Standards & interop | Month 7-8 |
| 8.5 | SPIFFE/SPIRE + OpenShell deep | Month 8 |
| 9 | Academic output (White Paper) | Month 9-10 |
| 9.5 | Independent evaluation (AMTSO) | Month 10 |
| 10 | Commercial (Pitch, partnerships) | Month 10-11 |
| 10.5 | EU Horizon Application | Month 12 |
| 11 | Ethics & legal | Parallel |
| 12 | Incident Response | Month 3 |
| 13 | EU AI Act + CRA compliance | Month 6-7 |
| 14 | Standardization (IETF/OWASP) | Month 12+ |

---

## Deferred (explicit)

- Formal Verification (TLA+, Z3): Month 10+
- SPIFFE/SPIRE: Month 6+ (use simple Cryptographic IDs now)
- Multi-process (Redis): Month 9+
- EU Horizon Application: Month 12
- Full IETF standardization: Year 2

---

## Target Standards (in priority)

1. **OWASP ACS** (Agentic Control Standard) — closest fit
2. **NIST COSAiS** — overlays on SP 800-53
3. **AMTSO** — independent testing
4. **IETF PQC** — identity + timestamps
5. **EU AI Act + CRA** — European compliance

---

## Success Metrics

- **Technical:** ASR < 5%, 90% coverage, 0 issues.
- **Academic:** White Paper + Open Dataset.
- **Standard:** OWASP ACS alignment.
- **Commercial:** Sustainable business model.
- **Community:** Adoption by 3+ external projects.

---

## Key ADRs (20 total)

(see docs/adr/ for details)

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

**End of Master Plan v2.2**
