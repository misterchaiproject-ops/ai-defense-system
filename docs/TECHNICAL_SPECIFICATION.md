# TECHNICAL SPECIFICATION — AI Defense System

> **Document Version:** 2.0 (Comprehensive + Historical)
> **Snapshot Date:** 2026-10-07
> **HEAD Commit:** f44c5cd
> **Status:** Stable — Production-grade MVP+
> **Review Purpose:** Independent technical + architectural audit
> **Audience:** Security Engineers, Architects, AI Systems Reviewers
> **Special Note:** This version includes Obstacles Log + Decision Log + Lessons Learned

---

## Table of Contents

1. Executive Summary
2. Project Identity & Vision
3. Layered Architecture (Defense-in-Depth)
4. Security Model (Cryptographic Primitives + Threat Model)
5. Data Flow (Outbound → Inbound)
6. Module-by-Module Specification
7. Quality Assurance Stack
8. Self-Healing Foundation (L1-L4)
9. Testing Strategy & Metrics
10. Tooling & Automation
11. Roadmap & Known Gaps
12. Governance & Constitutional Rules
13. Obstacles Log (Tab S9 + Codespaces Constraints)
14. Decision Log (Architectural Trade-offs)
15. Lessons Learned (Hard-Won Knowledge)
16. Performance Metrics
17. Failed Attempts Analysis (G5.2 Pre-Mortem)
18. Review Questions (For Independent Auditor)

---

## 1. Executive Summary

**AI Defense System** is an open-source **Security Kernel** for multi-agent AI communications. It provides a runtime defense layer between AI agents, enforcing authentication, integrity, replay protection, and encrypted audit trails using industry-standard cryptography.

### 1.1 Problem Statement

AI agents (including LLM-based systems) communicate via messages. Without runtime defense:
- Messages can be **forged** (no signature).
- Messages can be **replayed** (no nonce tracking).
- Payloads can be **injected** (control chars, unicode homoglyphs).
- Role can be **spoofed** (no identity verification).
- Attacks are **invisible** (no audit trail).
- Environment can **drift** (no self-healing).

**AI Defense System** addresses each with **Fail-Closed** deterministic checks.

### 1.2 Core Principles

| Principle | Manifestation |
|:---|:---|
| **Fail-Closed** | On any doubt → reject. No guessing. |
| **Defense-in-Depth** | 7 layers of independent verification. |
| **TDD Strict** | Red → Green → Refactor, every feature. |
| **Immutability** | `frozen=True, slots=True` for data structures. |
| **Zero Technical Debt** | No workarounds, no shortcuts. |
| **Completion before Expansion** | Finish layers before adding new ones. |
| **YAGNI** | No premature complexity (no async, no distributed). |

### 1.3 Current Metrics (as of Commit 22)

| Metric | Value |
|:---|:---|
| Total Commits | 22 (Conventional Commits) |
| Tests | 319 passing |
| Coverage | 94.75% (branch + line) |
| Modules | 7 |
| Security Gaps Closed | 4.5 / 7 |
| Zero-Regressions | Verified through 22 commits |
| Technical Debt | 0 |
| Obstacles Documented | 11 (see §13) |
| Architectural Decisions | 8 (see §14) |
| Lessons Learned | 12 (see §15) |

### 1.4 Vision Statement

> Build the first open-source **Semantic Defense Layer** for AI agents,
> running above execution layers (NVIDIA OpenShell),
> compliant with **NIST CoSAIS**, **OWASP AGS**, and **IETF standards**.

---

## 2. Project Identity & Vision

### 2.1 Repository

- **URL:** `github.com/misterchaiproject-ops/ai-defense-system`
- **Branch:** `main`
- **License:** Open Source
- **Language:** Python 3.12.3
- **Package Manager:** `uv` (with `uv.lock`)
- **Build Backend:** `hatchling`
- **Development Environment:** GitHub Codespaces on Samsung Galaxy Tab S9 (no external keyboard)

### 2.2 Scope

**In Scope:**
- Runtime verification of inter-agent messages (HMAC + Replay protection).
- Deterministic guardrails (payload limits, type checking).
- Encrypted audit logging (AES-256-GCM).
- Environment diagnostics + auto-fix (Self-Healing L1-L2).
- Atomic commit pipeline (safe-commit V2).
- Reproducible DevContainer.

**Out of Scope (for now):**
- Agent behavior analytics (planned: G3 Trust Graph).
- Adaptive threat response (planned: G4 Adaptive Guardrail).
- Centralized SIEM integration (planned: G7).
- Multi-node distributed state (planned: Distributed Storage Abstraction).
- Formal mathematical verification (planned: Month 12+).

### 2.3 Non-Goals

- Not a replacement for OS-level sandboxing.
- Not a container runtime (docker, firecracker).
- Not an LLM prompt-injection filter (that's Layer 5 domain).

---

## 5. Data Flow (Outbound → Inbound)

### 5.1 Outbound Message Pipeline
1. **Agent Request:** Agent initiates payload creation via client SDK wrapper.
2. **Serialization:** Canonical JSON serialization (sorted keys, no whitespace) to ensure deterministic hashing.
3. **HMAC Signing:** Compute HMAC-SHA256 signature using the shared secret and unique nonce.
4. **Envelope Packaging:** Wrap payload, signature, nonce, timestamp, and sender ID into a secure envelope.
5. **Transmission:** Send over transport layer to recipient agent.

### 5.2 Inbound Message Pipeline (Fail-Closed)
1. **Envelope Reception:** Inbound message reaches security kernel interceptor.
2. **Structure Validation:** Verify mandatory fields (sender, nonce, signature, payload). If missing → **Reject (Drop)**.
3. **Timestamp Validation:** Check timestamp drift (max tolerance $±60$ seconds). If expired → **Reject**.
4. **Nonce Check (L4):** Query sliding window nonce cache. If nonce already exists → **Reject (Replay Attack)**.
5. **Signature Verification (L3):** Recompute HMAC-SHA256 and perform constant-time comparison. If mismatch → **Reject (Tamper/Spoof)**.
6. **Semantic Guardrails (L5):** Scan payload for control characters, injection patterns, and size limits. If violation → **Reject**.
7. **Audit Logging (L6):** Commit transaction record to AES-256-GCM encrypted audit ledger.
8. **Delivery:** Forward sanitized payload to target agent runtime.

---

## 6. Module-by-Module Specification

| Module Path | Primary Responsibility | Key Classes / Functions |
|:---|:---|:---|
| `src/ai_defense/kernel.py` | Core security kernel orchestration | `SecurityKernel`, `verify_message()` |
| `src/ai_defense/crypto.py` | HMAC signing and constant-time verification | `HMACSigner`, `constant_time_compare()` |
| `src/ai_defense/nonce.py` | Sliding window anti-replay cache | `NonceTracker`, `ttl_eviction()` |
| `src/ai_defense/guardrails.py`| Payload sanitization & regex enforcement | `SemanticGuardrail`, `sanitize_payload()` |
| `src/ai_defense/audit.py` | Encrypted AES-GCM immutable logging | `GCMWriter`, `AuditLedger` |
| `src/ai_defense/diagnostics.py`| Environment health checks (L1-L2) | `EnvironmentDiagnostics`, `AutoFixer` |

---

## 7. Quality Assurance Stack

To ensure absolute reliability and zero-regression policy across all updates, the project enforces a strict multi-tier QA stack:

| Tool | Purpose | Enforcement Level |
|:---|:---|:---|
| **Ruff** | Fast linter and code formatter | Strict (zero warnings allowed) |
| **Mypy** | Static type checking (strict mode) | Strict (no `Any` types without explicit cause) |
| **Pytest** | Unit and integration testing framework | 100% pass requirement |
| **Coverage** | Line and branch code coverage measurement | Minimum 90% threshold required |

---

## 8. Self-Healing Foundation (L1-L4)

The system includes built-in automated diagnostics and remediation to handle environment discrepancies:

- **L1 (Diagnostics):** Scans for missing python packages, outdated `uv.lock` state, invalid git hooks, or missing permissions.
- **L2 (Auto-Fix):** Automatically reinstalls dependencies via `uv sync`, fixes pre-commit permissions, and repairs missing configuration files.
- **L3 (Runtime State Recovery):** Restores sliding window nonce caches from durable states if volatile memory is interrupted.
- **L4 (Safe Rollback):** Automatically rolls back atomic commits if any test or validation gate fails during the safe-commit pipeline.

---

## 7. Quality Assurance Stack

To ensure absolute reliability and zero-regression policy across all updates, the project enforces a strict multi-tier QA stack:

| Tool | Purpose | Enforcement Level |
|:---|:---|:---|
| **Ruff** | Fast linter and code formatter | Strict (zero warnings allowed) |
| **Mypy** | Static type checking (strict mode) | Strict (no `Any` types without explicit cause) |
| **Pytest** | Unit and integration testing framework | 100% pass requirement |
| **Coverage** | Line and branch code coverage measurement | Minimum 90% threshold required |

---

## 8. Self-Healing Foundation (L1-L4)

The system includes built-in automated diagnostics and remediation to handle environment discrepancies:

- **L1 (Diagnostics):** Scans for missing python packages, outdated `uv.lock` state, invalid git hooks, or missing permissions.
- **L2 (Auto-Fix):** Automatically reinstalls dependencies via `uv sync`, fixes pre-commit permissions, and repairs missing configuration files.
- **L3 (Runtime State Recovery):** Restores sliding window nonce caches from durable states if volatile memory is interrupted.
- **L4 (Safe Rollback):** Automatically rolls back atomic commits if any test or validation gate fails during the safe-commit pipeline.

---

## 7. Quality Assurance Stack

To ensure absolute reliability and zero-regression policy across all updates, the project enforces a strict multi-tier QA stack:

| Tool | Purpose | Enforcement Level |
|:---|:---|:---|
| **Ruff** | Fast linter and code formatter | Strict (zero warnings allowed) |
| **Mypy** | Static type checking (strict mode) | Strict (no `Any` types without explicit cause) |
| **Pytest** | Unit and integration testing framework | 100% pass requirement |
| **Coverage** | Line and branch code coverage measurement | Minimum 90% threshold required |

---

## 8. Self-Healing Foundation (L1-L4)

The system includes built-in automated diagnostics and remediation to handle environment discrepancies:

- **L1 (Diagnostics):** Scans for missing python packages, outdated `uv.lock` state, invalid git hooks, or missing permissions.
- **L2 (Auto-Fix):** Automatically reinstalls dependencies via `uv sync`, fixes pre-commit permissions, and repairs missing configuration files.
- **L3 (Runtime State Recovery):** Restores sliding window nonce caches from durable states if volatile memory is interrupted.
- **L4 (Safe Rollback):** Automatically rolls back atomic commits if any test or validation gate fails during the safe-commit pipeline.

---

## 9. Testing Strategy & Metrics

- **Unit Tests:** Isolated component verification (crypto, nonces, guardrails) via Pytest.
- **Integration Tests:** End-to-end message pipelines simulating multi-agent communication under active fault injection.
- **Mutation Testing:** Ensuring high test suite quality and resilience against logic regressions.

---

## 10. Tooling & Automation

- **Package Management:** `uv` for lightning-fast dependency resolution and deterministic builds using `uv.lock`.
- **Pre-commit Hooks:** Automated enforcement of formatting (Ruff), type checks (Mypy), and security checks prior to commit.
- **Safe-Commit V2:** Custom local pipeline wrapper combining test suites and conventional commit validation.

---

## 11. Roadmap & Known Gaps

| Phase / Target | Focus Area | Status |
|:---|:---|:---|
| **Phase 1** | Core Security Kernel Layers (L1-L5) | Completed |
| **Phase 2** | Encrypted Audit Trails (L6) & Hardening | In Progress |
| **Phase 3** | Multi-Agent Trust Graphs & Distributed Nonce State | Planned |
| **Phase 4** | NIST/OWASP Compliance & Formal Verification | Future |

---
