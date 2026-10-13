# STRATEGIC ROADMAP — AI Defense System

> **Document Version:** 1.0
> **Snapshot Date:** 2026-10-09
> **HEAD Commit:** f44c5cd
> **Purpose:** Strategic development roadmap for evolving from Secure Messaging Kernel to Global AI Agent Security Platform
> **Foundation:** Constitution (30 rules) + ChatGPT strategic recommendations
> **Status:** Strategic Planning (Post-Phase 3.5)

---

## TABLE OF CONTENTS

1. Analysis of ChatGPT Recommendations
2. Target Architecture (11 Layers)
3. Classified Roadmap (V1 -> V3+)
4. Strategic Gaps (Agent Identity, Authorization, Tool, Memory)
5. Success Metrics per Phase
6. Constitutional Alignment
7. Final Verdict

---

## §1. ANALYSIS OF CHATGPT RECOMMENDATIONS

### 1.1 Recommendation Classification

| # | Recommendation | ChatGPT Priority | Constitutional Alignment | Our Verdict | Timing |
|:---:|:---|:---|:---|:---|:---|
| 1 | G5.2 Audit Logging in verify_message | Deferred | P-03 (Architectural Security) | EXECUTE NOW | Session 1 |
| 2 | Branch Protection Rules | Recommended | P-06 (Independent Verification) | EXECUTE NOW | Session 1 |
| 3 | Self-Healing L3 (Auto-Test Retry) | Recommended | P-05 (Defense-in-Depth) | EXECUTE SOON | Session 2 |
| 4 | Mutation Testing (mutmut) | Recommended | P-06 (Verification) | EXECUTE SOON | Session 2 |
| 5 | Coverage Booster (guardrail, audit) | Recommended | P-03 (Quality) | EXECUTE SOON | Session 2 |
| 6 | G3 Multi-Agent Trust Graph | Recommended | P-05 (Defense-in-Depth) | EXECUTE AFTER G5.2 | Session 4 |
| 7 | G4 Adaptive Guardrail | Recommended | P-05 | EXECUTE AFTER G3 | Session 5 |
| 8 | OpenTelemetry Integration | Recommended | YAGNI (before G3) | DEFER | After G3 |
| 9 | Distributed Storage (Redis) | Recommended | YAGNI (premature) | DEFER | V2 |
| 10 | Async/Await Optimization | Recommended | YAGNI (no benchmarks) | DEFER | V3 |
| 11 | Formal Verification (TLA+) | Month 10+ | Correct timing | DEFER | Month 10+ |
| 12 | SLSA L3-4 + SBOM | Recommended | After SLSA L1-2 | DEFER | Month 3+ |

### 1.2 Analysis of Each Recommendation

#### R-01: G5.2 — Audit Logging in verify_message
- **Verdict:** ✅ EXECUTE NOW (Session 1) — Highest priority to close the loop on G5.1 MVP using strict TDD.

#### R-02: Branch Protection Rules
- **Verdict:** ✅ EXECUTE NOW (Session 1) — Configure GitHub UI to protect main branch and require CI checks.

#### R-03: Self-Healing L3 — Auto-Test Retry
- **Verdict:** ✅ EXECUTE SOON (Session 2) — Bounded retries and circuit breakers for transient test failures.

#### R-04: Mutation Testing (mutmut)
- **Verdict:** ✅ EXECUTE SOON (Session 2) — Introduce artificial bugs to verify test suite robustness (>90% score).

#### R-05: Coverage Booster
- **Verdict:** ✅ EXECUTE SOON (Session 2) — Raise guardrail and audit coverage to target ~97%.

#### R-06 & R-07: G3 Trust Graph & G4 Adaptive Guardrail
- **Verdict:** Execute sequentially after G5.2 completion.

#### R-08 to R-11: Observability, Distributed Storage, Async, Formal Verification
- **Verdict:** ⏸️ DEFER per YAGNI and architectural maturity principles.

---

## §2. TARGET ARCHITECTURE (11 LAYERS)

### 2.1 Current State (7 Layers)
- Layer 0: Contracts
- Layer 1: Guardrail
- Layer 2: Channel
- Layer 3: Audit
- Layer 5: Orchestrator
- Layer N: Doctor

### 2.2 Target Architecture (11 Layers)
- **Layer 10:** Enterprise Control Plane
- **Layer 9:** Risk & Trust Engine
- **Layer 8:** Runtime Security
- **Layer 7:** Memory & Context Security
- **Layer 6:** Tool & Action Security
- **Layer 5:** Orchestrator (Current)
- **Layer 4:** Authorization & Policy Engine
- **Layer 3:** Audit (Current)
- **Layer 2:** Channel (Current)
- **Layer 1:** Guardrail (Current)
- **Layer 0:** Contracts (Current)

---


## §3. CLASSIFIED ROADMAP (V1 -> V3+)

### 3.1 Overview

The roadmap is organized into 8 phases, spanning from immediate hardening to global platform vision.

\
### 3.2 Phase 0 — Assessment (DONE)

**Status:** Completed on 2026-10-09.

**Deliverables:**
- 22 commits, 319 tests, 94.75% coverage.
- Complete documentation set (14 .md files).
- Project Comprehensive Specification.
- Strategic Roadmap (this document).

**Exit Criteria:**
- [x] Architecture review complete.
- [x] Claim audit performed.
- [x] Gaps identified.

---

### 3.3 Phase 1 — Security Kernel Hardening (CURRENT)

**Objective:** Complete the current kernel before expansion.

**Sessions 1-3 (Approx 4 hours):**

| # | Task | Duration | Priority |
|:---:|:---|:---|:---:|
| 1 | Rebuild Container (DevContainer activation) | 5 min | HIGH |
| 2 | G5.2 — Audit Logging (strict TDD) | 45-60 min | HIGH |
| 3 | Branch Protection Rules (GitHub UI) | 10 min | HIGH |
| 4 | Self-Healing L3 (Auto-Test Retry) | 60 min | MEDIUM |
| 5 | Mutation Testing (mutmut) | 45 min | MEDIUM |
| 6 | Coverage Booster (guardrail, audit) | 30 min | MEDIUM |
| 7 | SBOM + SLSA Level 1 | 45 min | MEDIUM |

**Deliverables:**
- G5.2 complete: \ logs all 7 security events.
- Branch protection enforced on \.
- Self-Healing L1 + L2 + L3 complete.
- Mutation score > 90%.
- Coverage > 97%.
- SBOM auto-generated per release.

**Exit Criteria:**
- [ ] G5.2 merged (Commit 23+).
- [ ] Branch protection active.
- [ ] No regressions in 319+ tests.
- [ ] Coverage maintained at 97%+.
- [ ] SBOM attached to every release.

---

### 3.4 Phase 2 — Identity + Authorization + Policy

**Objective:** Add formal identity and authorization layers.

**Sessions 4-6 (Approx 6 hours):**

| # | Task | Duration |
|:---:|:---|:---|
| 8 | AgentIdentity Model (extend existing) | 60 min |
| 9 | Authentication Protocol (per-agent credentials) | 90 min |
| 10 | Authorization Engine (RBAC/ABAC) | 90 min |
| 11 | Policy Engine (Default Deny, REQUIRE_HUMAN_APPROVAL) | 60 min |
| 12 | Policy Versioning + Audit | 30 min |

**Deliverables:**
- Layer 4 added: \.
- \ dataclass: ALLOW / DENY / REQUIRE_HUMAN_APPROVAL.
- Agent registration + credential rotation.
- Delegation model (Agent A -> Agent B with scope reduction).

**Exit Criteria:**
- [ ] Every agent has a registered identity.
- [ ] Every message passes through authorization.
- [ ] Policy versioning works.
- [ ] Delegation cannot exceed delegator's scope.

---

### 3.5 Phase 3 — Tool Security + Runtime Security

**Objective:** Protect agents' interactions with external tools.

**Sessions 7-9 (Approx 8 hours):**

| # | Task | Duration |
|:---:|:---|:---|
| 13 | Tool Registry (tool_id, capabilities, risk) | 90 min |
| 14 | Tool Authorization (per-tool, per-agent) | 90 min |
| 15 | Input/Output Validation for tools | 60 min |
| 16 | Rate Limiting per tool | 60 min |
| 17 | Runtime Decision Enforcement | 90 min |
| 18 | MCP Security primitives | 90 min |

**Deliverables:**
- Layer 6 added: \.
- Layer 8 added: \.
- Tool Registry with capabilities + risk levels.
- Human approval for HIGH-risk tools (e.g., payments).

**Exit Criteria:**
- [ ] Every tool has a registered identity.
- [ ] Every tool call passes authorization.
- [ ] HIGH-risk actions require approval.
- [ ] MCP tools use the same security primitives.

---

### 3.6 Phase 4 — Agent-to-Agent + Context + Memory

**Objective:** Protect agent communication at scale + memory/context safety.

**Sessions 10-12 (Approx 8 hours):**

| # | Task | Duration |
|:---:|:---|:---|
| 19 | Agent-to-Agent Authentication Flow | 90 min |
| 20 | Trust Boundaries between agents | 60 min |
| 21 | Context Source Classification | 90 min |
| 22 | Memory Integrity Layer | 90 min |
| 23 | RAG Safety Layer | 60 min |

**Deliverables:**
- Layer 7 added: \.
- Context sources classified: Trusted Instruction / Untrusted Content / Data.
- Memory poisoning detection.
- RAG safety boundaries.

**Exit Criteria:**
- [ ] Every context source has a classification.
- [ ] Memory writes are integrity-checked.
- [ ] RAG reads are validated.
- [ ] External content cannot become Trusted Instruction.

---

### 3.7 Phase 5 — Risk + Trust

**Objective:** Add trust scoring and adaptive risk assessment.

**Sessions 13-14 (Approx 6 hours):**

| # | Task | Duration |
|:---:|:---|:---|
| 24 | G3 — Multi-Agent Trust Graph | 90 min |
| 25 | G4 — Adaptive Guardrail | 90 min |
| 26 | Risk Engine (deterministic) | 90 min |
| 27 | Anomaly Indicators | 60 min |

**Deliverables:**
- Layer 9 added: \.
- TrustScore (0.0-1.0) per agent.
- Threat Levels: LOW, ELEVATED, CRITICAL.
- Risk classification: LOW, MEDIUM, HIGH, CRITICAL.

**Exit Criteria:**
- [ ] Trust scores update dynamically.
- [ ] Threat levels affect guardrails.
- [ ] Risk engine is deterministic and testable.
- [ ] Audit logs capture risk decisions.

---

### 3.8 Phase 6 — Enterprise Control Plane

**Objective:** Enable enterprise deployment.

**Sessions 15-17 (Approx 8 hours):**

| # | Task | Duration |
|:---:|:---|:---|
| 28 | Multi-Tenancy Model | 90 min |
| 29 | KMS/HSM Integration (stub) | 60 min |
| 30 | OpenTelemetry Integration | 90 min |
| 31 | SIEM Integration (JSON/CEF output) | 90 min |
| 32 | SOC Integration API | 60 min |

**Deliverables:**
- Layer 10 added: \.
- Multi-tenant isolation.
- Distributed tracing (Trace Spans).
- SIEM-ready audit output.

**Exit Criteria:**
- [ ] Tenants are isolated.
- [ ] Traces visible in Jaeger/Datadog.
- [ ] SIEM ingests audit events.
- [ ] SOC APIs work.

---

### 3.9 Phase 7 — Global Platform

**Objective:** Scale to global, multi-region platform.

**Sessions 18+ (Ongoing):**

| # | Task | Duration |
|:---:|:---|:---|
| 33 | Distributed Storage Abstraction | 2 sessions |
| 34 | Async/Await (if benchmarks require) | 2 sessions |
| 35 | Multi-Region Replication | 3 sessions |
| 36 | SLSA Level 3-4 | 2 sessions |
| 37 | Formal Verification (TLA+, Z3) | Month 10+ |

**Deliverables:**
- Distributed state abstraction.
- Multi-region replication.
- Signed releases + provenance.
- Formal verification of core protocol.

**Exit Criteria:**
- [ ] Storage backend is swappable.
- [ ] Multi-region failover works.
- [ ] SLSA L3+ certified.
- [ ] Formal proofs of security properties.

---

## §4. STRATEGIC GAPS

### 4.1 Gap Analysis Summary

| Gap | Category | Priority | Phase |
|:---|:---|:---:|:---:|
| Agent Identity Model | Identity | HIGH | Phase 2 |
| Authorization Engine | Authorization | HIGH | Phase 2 |
| Policy Engine | Policy | HIGH | Phase 2 |
| Tool Security | Tools | HIGH | Phase 3 |
| Runtime Enforcement | Runtime | MEDIUM | Phase 3 |
| Agent-to-Agent Auth | Communication | HIGH | Phase 4 |
| Context Classification | Context | MEDIUM | Phase 4 |
| Memory Integrity | Memory | MEDIUM | Phase 4 |
| Trust Graph (G3) | Trust | MEDIUM | Phase 5 |
| Adaptive Guardrail (G4) | Risk | MEDIUM | Phase 5 |
| Multi-Tenancy | Enterprise | LOW | Phase 6 |
| SIEM Integration (G7) | Observability | LOW | Phase 6 |

### 4.2 Critical Strategic Gaps (Not Yet Addressed)

**Gap 1: Agent Identity is Minimal**

Current: \ + frozenset of roles.
Missing:
- Owner / Organization / Tenant.
- Environment / Workload.
- Model / Model Version.
- Trust Domain.
- Credential rotation + revocation.

**Gap 2: No Authorization Layer**

Current: Role allowlist check only.
Missing:
- RBAC (Role-Based Access Control).
- ABAC (Attribute-Based Access Control).
- Policy evaluation engine.
- Default Deny enforcement.
- Least Privilege principle.

**Gap 3: No Tool Security**

Current: Nothing.
Missing:
- Tool identity registration.
- Tool authorization per agent.
- Input validation for tool calls.
- Output validation from tools.
- Rate limiting per tool.
- Human approval for HIGH-risk tools.

**Gap 4: No Memory/Context Security**

Current: Nothing.
Missing:
- Context source classification.
- Memory integrity checks.
- RAG safety.
- Instruction vs Data separation.

### 4.3 Strategic Value of Filling These Gaps

Filling these gaps would transform the project from:
- **Secure Messaging Library** (current)

Into:
- **AI Agent Security Platform** (target)

**Competitive Advantages:**
- First open-source AI Agent Security Platform.
- Compliant with NIST CoSAIS + OWASP AGS + IETF.
- Deterministic + Auditable + Fail-Closed.
- Modular architecture (Kernel + Layers).

---

## §5. SUCCESS METRICS PER PHASE

### 5.1 Phase 1 Metrics

| Metric | Current | Target |
|:---|:---:|:---:|
| Tests | 319 | 340+ |
| Coverage | 94.75% | 97%+ |
| Mutation Score | N/A | 90%+ |
| Commits | 22 | 27+ |
| SBOM | None | Auto-generated |
| Branch Protection | None | Active |

### 5.2 Phase 2 Metrics

| Metric | Target |
|:---|:---:|
| Authorization Decision Tests | 50+ |
| Policy Versioning Tests | 20+ |
| Agent Identity Fields | 10+ |
| Delegation Tests | 15+ |

### 5.3 Phase 3 Metrics

| Metric | Target |
|:---|:---:|
| Registered Tools | 10+ |
| Tool Authorization Tests | 40+ |
| Rate Limit Tests | 15+ |
| Human Approval Workflows | 5+ |

### 5.4 Phase 4 Metrics

| Metric | Target |
|:---|:---:|
| Context Classifications | 6+ |
| Memory Integrity Tests | 20+ |
| RAG Safety Tests | 15+ |

### 5.5 Phase 5 Metrics

| Metric | Target |
|:---|:---:|
| Trust Score Tests | 30+ |
| Adaptive Guardrail Tests | 25+ |
| Risk Engine Tests | 40+ |

### 5.6 Phase 6 Metrics

| Metric | Target |
|:---|:---:|
| Tenant Isolation Tests | 20+ |
| OpenTelemetry Traces | 50+ span types |
| SIEM Format Tests | 10+ |

---

## §6. CONSTITUTIONAL ALIGNMENT

### 6.1 Mapping to Constitutional Principles

| Phase | Primary Principle | Secondary Principle |
|:---:|:---|:---|
| Phase 1 | P-03 (Architectural Security) | P-06 (Verification) |
| Phase 2 | P-03 (Architectural Security) | P-01 (Understanding) |
| Phase 3 | P-05 (Defense-in-Depth) | P-03 |
| Phase 4 | P-05 (Defense-in-Depth) | P-03 |
| Phase 5 | P-05 (Defense-in-Depth) | P-06 |
| Phase 6 | P-06 (Independent Verification) | P-04 |
| Phase 7 | P-04 (Documentation) | P-06 |

### 6.2 Compliance Checklist

For every phase, the following must hold:

- [ ] TDD strict (Red -> Green -> Refactor).
- [ ] Atomic commits (Conventional Commits).
- [ ] Zero regressions.
- [ ] >> Layer 2: Self-Diagnose
==========================

[1/7] ruff check (lint)...
All checks passed!
  OK: Clean

[2/7] mypy --strict (types)...
Success: no issues found in 33 source files
  OK: Clean

[3/7] bandit (security)...
  OK: No issues

[4/7] pip-audit (dependencies)...
Name              Skip Reason
----------------- --------------------------------------------------------------------------------
ai-defense-system Dependency not found on PyPI and could not be audited: ai-defense-system (0.1.0)
  OK: No vulnerabilities

[5/7] ruff format --check (formatting)...
33 files already formatted
 OK: Clean

[6/7] pytest (tests)...
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspaces/ai-defense-system
configfile: pyproject.toml
testpaths: tests
plugins: platformdirs-4.12.2, hypothesis-6.168.3, cov-7.1.0
collected 319 items

tests/test_smoke.py .............                                        [  4%]
tests/unit/audit/test_core.py ........................                   [ 11%]
tests/unit/channel/test_core.py ........................................ [ 24%]
.....................                                                    [ 30%]
tests/unit/contracts/test_actions.py ..............                      [ 35%]
tests/unit/contracts/test_agent_identity.py ............................ [ 43%]
.........                                                                [ 46%]
tests/unit/contracts/test_proposal.py .................................. [ 57%]
..                                                                       [ 57%]
tests/unit/contracts/test_reason_codes.py .................              [ 63%]
tests/unit/contracts/test_roles.py ..............                        [ 67%]
tests/unit/contracts/test_validation_result.py ......................... [ 75%]
.....                                                                    [ 77%]
tests/unit/doctor/test_core.py ............................              [ 85%]
tests/unit/guardrail/test_core.py .............................          [ 94%]
tests/unit/orchestrator/test_core.py ................                    [100%]

============================= 319 passed in 1.58s ==============================
  OK: All passing

[7/7] coverage (branch, fail-under=80)...
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspaces/ai-defense-system
configfile: pyproject.toml
testpaths: tests
plugins: platformdirs-4.12.2, hypothesis-6.168.3, cov-7.1.0
collected 319 items

tests/test_smoke.py .............                                        [  4%]
tests/unit/audit/test_core.py ........................                   [ 11%]
tests/unit/channel/test_core.py ........................................ [ 24%]
.....................                                                    [ 30%]
tests/unit/contracts/test_actions.py ..............                      [ 35%]
tests/unit/contracts/test_agent_identity.py ............................ [ 43%]
.........                                                                [ 46%]
tests/unit/contracts/test_proposal.py .................................. [ 57%]
..                                                                       [ 57%]
tests/unit/contracts/test_reason_codes.py .................              [ 63%]
tests/unit/contracts/test_roles.py ..............                        [ 67%]
tests/unit/contracts/test_validation_result.py ......................... [ 75%]
.....                                                                    [ 77%]
tests/unit/doctor/test_core.py ............................              [ 85%]
tests/unit/guardrail/test_core.py .............................          [ 94%]
tests/unit/orchestrator/test_core.py ................                    [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________

Name                                 Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------
src/audit/__init__.py                    2      0      0      0   100%
src/audit/core.py                      105      7     34      6    91%   55, 68, 87, 92->95, 132, 139, 151-152
src/channel/__init__.py                  2      0      0      0   100%
src/channel/core.py                    183      8     80      8    94%   172, 174, 176, 180, 182, 184, 190, 267
src/contracts/__init__.py                7      0      0      0   100%
src/contracts/actions.py                 8      0      0      0   100%
src/contracts/agent_identity.py         42      0     14      0   100%
src/contracts/proposal.py               43      0     20      0   100%
src/contracts/reason_codes.py           20      0      0      0   100%
src/contracts/roles.py                   8      0      0      0   100%
src/contracts/validation_result.py      45      0     14      0   100%
src/doctor/__init__.py                   2      0      0      0   100%
src/doctor/__main__.py                  21      1      4      1    92%   44
src/doctor/core.py                      83      2     24      1    97%   35-36
src/guardrail/__init__.py                2      0      0      0   100%
src/guardrail/core.py                   63      9     40      6    85%   108, 120, 122, 124, 126, 168, 194-197
src/orchestrator/__init__.py             2      0      0      0   100%
src/orchestrator/core.py                52      0     14      0   100%
--------------------------------------------------------------------------------
TOTAL                                  690     27    244     22    95%
Required test coverage of 80% reached. Total coverage: 94.75%
============================= 319 passed in 2.76s ==============================
 OK: Coverage >= 80%

==========================
SUCCESS: All checks passed. Ready to push. 7/7.
- [ ] Coverage maintained or improved.
- [ ] Documentation updated.
- [ ] No new technical debt.
- [ ] Fail-Closed philosophy preserved.

---

## §7. FINAL VERDICT

### 7.1 Answers to Key Questions

**1. Does the current project deserve further development?**
YES. The kernel is architecturally sound, has zero technical debt, and provides a solid foundation.

**2. Should it be rebuilt from scratch or evolved incrementally?**
EVOLVED INCREMENTALLY. The current 7-layer architecture is well-structured. Rebuilding would waste 22 commits of careful engineering.

**3. What are the 5 most important technical changes?**
1. G5.2 (audit logging in verify_message).
2. Authorization layer (RBAC/ABAC).
3. Policy Engine (Default Deny).
4. Tool Security (per-tool authorization).
5. Agent Identity expansion (owner, tenant, trust domain).

**4. What are the 5 most critical security gaps?**
1. No authorization layer.
2. No tool security.
3. No memory/context security.
4. Minimal agent identity.
5. No runtime enforcement.

**5. What are the 5 most important features to become Agent Security Platform?**
1. Agent Identity + Authentication.
2. Authorization + Policy Engine.
3. Tool Security.
4. Memory + Context Security.
5. Risk + Trust Engine.

**6. What should be deferred?**
- Async/Await (no benchmarks yet).
- Distributed Storage (no need yet).
- OpenTelemetry (before G3 it's premature).
- Formal Verification (needs frozen spec).
- Multi-region replication.

**7. What could become a competitive advantage?**
- First open-source AI Agent Security Platform.
- NIST CoSAIS + OWASP AGS + IETF compliance.
- Deterministic + Auditable + Fail-Closed.
- Modular Kernel + Layers architecture.

**8. What is the true V1?**
**V1 = Phase 1 + Phase 2** (Kernel Hardening + Identity + Authorization + Policy).

**V1 Exit Criteria:**
- G5.2 complete.
- Agent Identity expanded.
- Authorization engine working.
- Policy Engine (Default Deny).
- Coverage 97%+.
- Mutation score 90%+.
- Branch Protection active.

**9. What is V2?**
**V2 = Phase 3 + Phase 4 + Phase 5** (Tool Security + Agent-to-Agent + Memory + Risk + Trust).

**10. How can the project become an Enterprise AI Agent Security Platform?**
Path: V1 -> V2 -> Phase 6 (Enterprise) -> Phase 7 (Global).

Requirements:
- Multi-tenancy.
- KMS/HSM integration.
- OpenTelemetry.
- SIEM integration.
- SOC APIs.
- SLSA L3+.
- Formal verification (month 10+).

### 7.2 Recommended Priority Order (Final)

\
---

**End of STRATEGIC_ROADMAP.md**

**Document Version:** 1.0
**Last Updated:** 2026-10-09
**Status:** Ready for execution
**Next Action:** Execute Session 1 (G5.2 + Branch Protection)


## §3. CLASSIFIED ROADMAP (V1 -> V3+)

### 3.1 Phase V1 (Current -> Session 1-3) — Core Hardening & Quality
- **Focus:** Complete G5.2 audit logging, branch protection, self-healing L3, mutation testing, coverage booster, SBOM.
- **Milestones:** Zero technical debt, 100% core test passing, 95%+ coverage.

### 3.2 Phase V2 (Session 4-6) — Intelligence & Adaptation
- **Focus:** G3 Multi-Agent Trust Graph, G4 Adaptive Guardrail.
- **Milestones:** Dynamic threat tracking, automated mitigation policies based on agent behavioral scores.

### 3.3 Phase V3+ (Long-Term) — Scale & Enterprise Compliance
- **Focus:** Enterprise Control Plane integration, SLSA Level 3-4 builds, Formal Verification.
- **Milestones:** Compliance with NIST CoSAIS and OWASP AGS, production multi-node scaling readiness.

---

## §4. STRATEGIC GAPS & MITIGATIONS

1. **Agent Identity & Cryptographic Binding:**
   - *Gap:* Static sender IDs can be spoofed if keys are compromised.
   - *Mitigation:* Implement key rotation (G2) and certificate-based decentralized identities in V2.
2. **Authorization & Access Control:**
   - *Gap:* Lack of fine-grained policy evaluation per agent role.
   - *Mitigation:* Introduce Layer 4 Policy Engine in Phase V2.
3. **Tool & Action Validation:**
   - *Gap:* Messages are sanitized, but tool execution payloads lack dedicated runtime checks.
   - *Mitigation:* Implement Layer 6 Tool Security in V3.
4. **Memory & Context Isolation:**
   - *Gap:* Cross-agent memory injection or prompt poisoning via shared context.
   - *Mitigation:* Implement Layer 7 Memory & Context Security.

---
