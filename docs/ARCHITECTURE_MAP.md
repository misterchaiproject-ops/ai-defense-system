# ARCHITECTURE MAP — AI Defense System

> **Snapshot:** 2026-10-07
> **HEAD:** a67faa5
> **Purpose:** Visual + structural reference

---

## 1. Layered Architecture (Defense-in-Depth)

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Defense System                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 5 — Orchestrator                              │   │
│  │  src/orchestrator/core.py                            │   │
│  │  SecureOrchestrator.process_outbound / process_inbound│   │
│  │  Coverage: 100%                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 2 — Channel                                   │   │
│  │  src/channel/core.py                                 │   │
│  │  SecureAgentChannel (HMAC + SQLite Replay + Key Ring)│   │
│  │  Coverage: 94%                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 1 — Guardrail                                 │   │
│  │  src/guardrail/core.py                               │   │
│  │  DeterministicGuardrail (limits, min_values)         │   │
│  │  Coverage: 85%                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 0 — Contracts                                 │   │
│  │  src/contracts/                                      │   │
│  │  Frozen Dataclasses (Envelope, Proposal, AgentIdentity)│ │
│  │  Coverage: 100%                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Layer 3 — Audit (Cross-cutting)                            │
│  src/audit/core.py                                          │
│  SecureAuditLog (AES-256-GCM + AAD)                         │
│  Coverage: 91%                                              │
├─────────────────────────────────────────────────────────────┤
│  Layer ∞ — Doctor (Self-Healing)                            │
│  src/doctor/core.py                                         │
│  make doctor (5 environment checks)                         │
│  Coverage: 95%                                              │
└─────────────────────────────────────────────────────────────┘
```

---
## 2. Message Flow (Outbound → Inbound)

```
[Agent A: sender]
    │
    │  create_message(sender_id, payload)
    ▼
[SecureOrchestrator.process_outbound]
    │
    │  1. Guardrail.validate(payload)
    │  2. Channel.create_message(...)
    ▼
[SecureAgentChannel.create_message]
    │
    │  1. canonical = _canonicalize(payload)
    │  2. timestamp = time.time()
    │  3. nonce = secrets.token_hex(16)
    │  4. signature = _sign(key_id, sender_id, timestamp, nonce, canonical)
    ▼
[Envelope] (frozen dataclass)
    │
    │  version, key_id, sender_id, timestamp, nonce, payload, signature
    ▼
═══════════════════════════════════════════════════════════════
                        NETWORK
═══════════════════════════════════════════════════════════════
    ▼
[Agent B: receiver]
    │
    ▼
[SecureOrchestrator.process_inbound]
    │
    │  1. Channel.verify_message(envelope)
    │  2. Guardrail.validate(reconstructed_proposal)
    ▼
[SecureAgentChannel.verify_message]
    │
    ├─ 1. isinstance(envelope, Envelope)     → INVALID_ENVELOPE
    ├─ 2. envelope.version == PROTOCOL_VERSION → UNSUPPORTED_VERSION
    ├─ 3. envelope.key_id in self._key_ring  → UNKNOWN_KEY_ID
    ├─ 4. envelope.sender_id in self._allowed → ROLE_NOT_PERMITTED
    ├─ 5. timestamp freshness                 → TIMESTAMP_TOO_OLD
    │                                          TIMESTAMP_FROM_FUTURE
    ├─ 6. canonicalize payload + calculate expected HMAC
    ├─ 7. hmac.compare_digest(sig, expected)  → INVALID_SIGNATURE
    ├─ 8. atomic _replay.check_and_add(nonce)  → REPLAY_DETECTED
    │      retains nonce until message expiry; no active FIFO eviction
    │      capacity exhaustion fails closed (INTERNAL_ERROR)
    │
    └─ OK → ValidationResult.ok()
```

---

## 3. Security Layers

### 3.1 Confidentiality

| Data | Protection |
|:---|:---|
| Message payloads | HMAC-SHA256 (integrity) |
| Audit logs | AES-256-GCM (confidentiality + integrity) |
| Shared secrets | In-memory only (Key Ring) |
| SQLite Replay Cache | Nonces only (non-sensitive) |

### 3.2 Integrity

- **HMAC-SHA256** with  (constant-time)
- **AES-GCM tag** (16 bytes) for audit records
- **Canonical JSON** (sorted keys, ASCII-only) for deterministic signing

### 3.3 Availability

- Replay Cache is bounded and expiry-aware; unexpired nonces are never evicted to make room
- SQLite `BEGIN IMMEDIATE` serializes nonce reservation across independent connections
- Capacity exhaustion fails closed rather than weakening replay protection
- SQLite persistence prevents state loss on restart
-  prevents environment drift

---
## 4. Directory Structure

```
ai-defense-system/
├── .devcontainer/          Reproducible environment
│   ├── setup.sh            git config + bracketed-paste off
│   └── devcontainer.json   Python 3.12 + postCreateCommand
│
├── .github/                CI/CD
│   ├── workflows/ci.yml
│   └── dependabot.yml
│
├── docs/                   Documentation
│   ├── ARCHITECTURE_MAP.md (this file)
│   ├── CONSTITUTION.md
│   ├── LESSONS_LEARNED.md
│   ├── MASTER_PLAN.md
│   ├── PROJECT_STATE.md
│   ├── PROMPT_TEMPLATE.md
│   ├── REVIEW-003.md
│   ├── ROADMAP_FULL.md
│   ├── SELF_HEALING.md
│   ├── THREAT_MODEL.md
│   └── VERIFICATION_PROTOCOL.md
│
├── scripts/                Tooling
│   ├── check.sh            7-step verification
│   ├── check_api.sh        ClassName.method() validator
│   ├── fix.sh              auto-fix
│   ├── safe-commit.sh V2   atomic pipeline
│   ├── show_api.sh         API inspector
│   └── verify.sh           fix + check
│
├── src/                    Source
│   ├── audit/              Layer 3
│   ├── channel/            Layer 2
│   ├── contracts/          Layer 0
│   ├── doctor/             Layer ∞
│   ├── guardrail/          Layer 1
│   └── orchestrator/       Layer 5
│
├── tests/                  Tests
│   └── unit/
│       ├── audit/
│       ├── channel/
│       ├── contracts/
│       ├── doctor/
│       ├── guardrail/
│       └── orchestrator/
│
├── Makefile                make check | fix | verify | test | cov | clean
├── pyproject.toml          Project config
├── uv.lock                 Lock file
└── README.md
```

---

## 5. Key Files Reference

| File | Purpose | Coverage |
|:---|:---|:---:|
| `src/contracts/envelope.py` | Envelope dataclass (7 fields) | 100% |
| `src/contracts/proposal.py` | Proposal (3 fields) | 100% |
| `src/contracts/agent_identity.py` | AgentIdentity + roles | 100% |
| `src/contracts/validation_result.py` | ValidationResult + ReasonCode | 100% |
| `src/guardrail/core.py` | DeterministicGuardrail | 85% |
| `src/channel/core.py` | SecureAgentChannel + _ReplayCache | 94% |
| `src/audit/core.py` | SecureAuditLog + AuditEvent | 91% |
| `src/orchestrator/core.py` | SecureOrchestrator | 100% |
| `src/doctor/core.py` | Environment diagnostics | 95% |

---

## 6. Cryptographic Primitives

| Primitive | Usage | Standard |
|:---|:---|:---|
| **HMAC-SHA256** | Message authentication | RFC 2104 |
| **AES-256-GCM** | Audit log encryption | NIST SP 800-38D |
| **AAD** (`baudit-v1`) | Context separation | NIST SP 800-38D |
| **12-byte Nonce** | Random per record | NIST SP 800-38A |
| **32-byte Key** | 256-bit AES | NIST SP 800-57 |
| **secrets.token_bytes** | CSPRNG | Python docs |

---

## 7. Testing Strategy

| Test Type | Count | Location |
|:---|:---:|:---|
| **Unit** | 319 | `tests/unit/` |
| **Property-based** | (subset) | Hypothesis |
| **Smoke** | 1 | `tests/test_smoke.py` |

**Quality Gates:**
1. ruff check (linting)
2. mypy --strict (types)
3. bandit (SAST)
4. pip-audit (dependencies)
5. ruff format --check
6. pytest (319 tests)
7. coverage --fail-under=80

**Coverage:** 94.75% (branch + line)

---

## 8. Self-Healing Layers

| Layer | Mechanism | Commit |
|:---:|:---|:---|
| **L1** | `make doctor` — 5 environment checks | e184d64 |
| **L2** | `fix.sh` + `safe-commit.sh V2` | e9c5551 |
| **L3** | Auto-Test Retry (pending) | — |
| **L4** | Runtime Circuit Breaker (pending) | — |

---

## 9. Key Principles

1. **Fail-Closed** — عند الشك، ارفض.
2. **Defense-in-Depth** — 7 طبقات.
3. **TDD Strict** — Red → Green → Refactor.
4. **Atomic Commits** — Conventional Commits.
5. **Immutability** — `frozen=True, slots=True`.
6. **Zero Technical Debt**.
7. **Completion before Expansion**.
8. **YAGNI** — no premature complexity.

---

**End of ARCHITECTURE_MAP.md**
