# Resource, Data & Execution Governance

**Status:** Design baseline — no runtime enforcement yet  
**Phase:** Architectural hardening before Self-Healing L3/L4  
**Date:** 2026-10-20  
**Scope:** Agents, workflows, tools, Doctor/Self-Healing, storage, telemetry, and execution resources

---

## 1. Purpose

This document defines the security and engineering boundary for controlling resource consumption, data lifecycle, execution scope, and cross-agent isolation.

It is a design contract, not an implementation authorization. Runtime controls MUST be implemented only after the relevant contracts and tests exist.

The objective is to prevent:

- unbounded CPU, memory, token, API, tool, retry, concurrency, network, storage, or log consumption;
- uncontrolled retention of operational or sensitive data;
- cross-agent or cross-tenant data access;
- runaway workflows and recursive tool/agent loops;
- Self-Healing actions from expanding their own authority;
- resource exhaustion becoming a denial-of-service or denial-of-wallet condition.

---

## 2. Governing Principles

1. **Least privilege:** every agent, workflow, tool, and Doctor capability receives only the minimum authority required.
2. **Explicit budgets:** resource consumption is bounded before execution, not only measured afterward.
3. **Fail-closed:** an unknown, missing, malformed, or exceeded security limit MUST NOT silently become unlimited.
4. **Isolation:** tenant, agent, workflow, credential, and data scopes MUST be independently enforceable.
5. **Data minimization:** collect and retain only what is required for security, operation, audit, or contractual obligations.
6. **Bounded execution:** retries, recursion, concurrency, runtime, tool calls, and external requests MUST have explicit ceilings.
7. **No arbitrary self-modification:** Doctor/Self-Healing MUST use an allowlisted action model and MUST NOT grant itself capabilities.
8. **Observe before heal:** detection and diagnosis are separate from authorization and execution.
9. **Verify after action:** a healing action is incomplete until its result has been independently checked.
10. **Audit security decisions:** security-relevant denials, throttling, isolation, healing, rollback, and budget exhaustion MUST produce structured audit evidence.

---

## 3. Security Boundary Model

```text
Tenant
  |
  +-- Agent Identity
       |
       +-- Agent Contract
            |
            +-- Workflow Scope
                 |
                 +-- Capability Policy
                      |
                      +-- Resource Budget
                           |
                           +-- Data Policy
                                |
                                +-- Execution Gate
                                     |
                                     +-- Runtime
                                     |
                                     +-- Audit / Telemetry
```

No component may bypass a higher-level boundary by writing directly to a lower-level resource.

A Prompt/LLM instruction is **not** a security boundary. Authorization, limits, isolation, and dangerous-action restrictions MUST be enforced in deterministic application/runtime controls.

---

## 4. Resource Budget Contract

Every executable agent/workflow context MUST eventually have a resolved resource policy. Until such a policy exists, unlimited execution is not permitted for security-sensitive operations.

Minimum budget dimensions:

| Resource | Required control | Example failure behavior |
|---|---|---|
| CPU/time | execution deadline | terminate/escalate |
| Memory | maximum working set where enforceable | isolate/terminate |
| LLM tokens | input/output/session budget | stop or require approval |
| Tool calls | per-run and per-window count | deny further calls |
| API requests | rate + quota | throttle/circuit-break |
| Retries | maximum attempts | escalate |
| Concurrency | per-agent/workflow limit | queue or deny |
| Recursion/depth | maximum depth | terminate loop |
| Network | request/rate/egress policy | deny/throttle |
| Persistent storage | quota | reject new writes |
| Logs/audit | bounded operational retention/volume | aggregate/throttle, never silently discard security evidence |

### 4.1 Budget semantics

- Missing limit: **deny or use an explicitly documented safe default**, never implicit infinity.
- Negative/NaN/infinite/overflowing values: reject configuration.
- Budget counters MUST use monotonic accounting where wall-clock changes could affect safety.
- Enforcement MUST occur before the operation when practical and MUST be checked again for cumulative budgets.
- A child workflow MUST NOT inherit more authority or budget than its parent contract permits.
- A retry MUST consume budget; retries are not free executions.

---

## 5. Data Governance

Data lifecycle:

```text
Create -> Classify -> Authorize -> Store -> Use -> Retain -> Archive/Delete
```

Required controls:

### 5.1 Classification

At minimum:

- PUBLIC
- INTERNAL
- CONFIDENTIAL
- SENSITIVE
- SECRET

Classification MUST affect storage, logging, access, retention, and export policy.

### 5.2 Collection minimization

Do not persist prompts, tool output, credentials, raw payloads, or diagnostic context merely because they are available.

Sensitive values MUST be redacted or replaced with references before operational logging where the raw value is not required.

### 5.3 Retention

Every persistent data class MUST have an explicit retention policy. No indefinite retention by default.

Security/audit evidence MUST not be deleted merely to satisfy a normal resource quota. When storage pressure threatens security evidence, the system MUST raise an operational/security event and apply an approved archive policy.

### 5.4 Isolation

Data access MUST be bound to the authenticated tenant/agent/workflow context. Object identifiers alone MUST NOT authorize access.

---

## 6. Execution Controls

The execution gate MUST evaluate, at minimum:

```text
Identity
+ Contract
+ Capability
+ Resource Budget
+ Data Policy
+ Target Scope
+ Risk Level
+ Current System State
```

Only then may an action execute.

High-risk actions MUST require stronger authorization. Examples include:

- changing security policy;
- changing cryptographic configuration;
- modifying trust boundaries;
- changing credentials/keys;
- deleting audit evidence;
- changing another tenant's state;
- arbitrary code execution;
- modifying production security controls.

These actions are **not** part of automatic Self-Healing by default.

---

## 7. Circuit Breaker States

A resource or execution context may transition only through explicit policy:

```text
NORMAL
  -> WARNING
  -> THROTTLED
  -> ISOLATED
  -> STOPPED
```

Recovery MUST NOT jump directly from STOPPED to unrestricted NORMAL. A controlled recovery and verification step is required.

The circuit breaker MUST itself be bounded and fail closed if its state cannot be reliably determined.

---

## 8. Doctor / Self-Healing Boundary

The Doctor is an observer/diagnostician first. It is not an unrestricted administrator.

Required flow:

```text
OBSERVE
  -> DETECT
  -> COLLECT EVIDENCE
  -> DIAGNOSE
  -> SCORE RISK
  -> CHECK CONTRACT/POLICY
  -> AUTHORIZE ALLOWLISTED ACTION
  -> EXECUTE WITH BUDGET
  -> VERIFY
  -> AUDIT
  -> CLOSE / ROLLBACK / ESCALATE
```

### 8.1 Forbidden Doctor capabilities

The Doctor MUST NOT be able to:

- grant itself permissions;
- bypass resource budgets;
- disable audit controls;
- delete security evidence to free storage;
- modify cryptographic policy automatically;
- cross tenant boundaries;
- execute arbitrary commands/code;
- modify its own policy or contract;
- suppress failed verification results.

### 8.2 Healing action contract

Every future healing action MUST define:

```text
Action ID
Target scope
Preconditions
Required capability
Maximum resource budget
Expected state transition
Verification procedure
Rollback procedure
Audit event
Failure behavior
```

No generic `heal()` operation is permitted.

---

## 9. Configuration and Contract Integrity

Resource policies and contracts are security-sensitive configuration.

Therefore:

- schema validation is mandatory;
- unknown fields MUST NOT silently change semantics;
- invalid limits MUST fail closed;
- configuration changes MUST be versioned and auditable;
- a policy cannot weaken a higher-level security invariant;
- child policies cannot exceed parent limits;
- policy changes affecting production enforcement require the project's established review gates.

---

## 10. Telemetry Requirements

At minimum, telemetry should support:

- resource usage by tenant/agent/workflow;
- budget consumption and remaining budget;
- throttling/circuit-breaker transitions;
- denied operations and reason codes;
- storage/retention pressure;
- tool/API call rates;
- healing attempts and outcomes;
- rollback/escalation events.

Telemetry MUST avoid becoming an uncontrolled data sink. Collection itself is subject to storage, retention, and privacy policies.

---

## 11. Threat Model

| Threat | Required mitigation |
|---|---|
| Runaway agent loop | recursion/depth + tool-call + time budgets |
| Denial of Service | concurrency/rate/resource limits + circuit breaker |
| Denial of Wallet | token/API quotas + cumulative budgets |
| Memory/storage exhaustion | quotas + pressure monitoring + safe rejection |
| Cross-agent data leakage | identity-bound authorization + isolation |
| Prompt injection | deterministic policy enforcement; prompt is not authorization |
| Malicious/self-amplifying Doctor | allowlisted actions + immutable capability boundary |
| Audit flooding | bounded operational telemetry + protected security evidence |
| Policy tampering | integrity/version/review controls |
| False-positive healing | evidence + risk gate + verification + rollback |
| Failed healing | fail closed + rollback/escalation |

---

## 12. Implementation Order

This specification intentionally precedes runtime implementation.

### Step R1 — Contract model
Define typed resource/data/execution policy contracts.

### Step R2 — Deterministic validation
Reject malformed, conflicting, unsafe, or inheritance-breaking policies.

### Step R3 — Enforcement points
Integrate enforcement at the execution boundary rather than trusting callers.

### Step R4 — Telemetry
Measure usage without creating an unbounded logging problem.

### Step R5 — Circuit breakers
Implement bounded state transitions and recovery verification.

### Step R6 — Doctor integration
Allow Doctor to diagnose resource/data incidents and propose only allowlisted actions.

### Step R7 — Self-Healing
Enable automatic healing only after R1-R6 have tests and security review.

---

## 13. Required Tests Before Runtime Enablement

At minimum:

- missing/invalid/negative/infinite limits;
- boundary values and overflow;
- parent/child budget inheritance;
- cross-tenant access attempts;
- cross-agent workflow access attempts;
- recursive tool/workflow loops;
- concurrent budget consumption;
- race conditions around quota enforcement;
- storage pressure;
- audit retention under pressure;
- circuit-breaker transitions and recovery;
- Doctor attempting forbidden capabilities;
- failed healing verification;
- rollback after failed healing;
- policy tampering/version mismatch;
- prompt injection attempting to bypass policy;
- deterministic behavior under repeated failures.

No Self-Healing production capability should be enabled until these categories have explicit coverage.

---

## 14. Current Decision

**Decision:** adopt this document as the architectural baseline for Resource, Data & Execution Governance.

**Not yet implemented:** runtime budgets, tenant isolation, circuit breakers, or automatic healing capabilities.

**Next engineering action:** inspect existing `src/contracts`, `src/orchestrator`, `src/guardrail`, `src/doctor`, and `src/audit` boundaries and design the smallest compatible typed contracts for R1 without changing existing runtime behavior.

**Safety rule:** no production behavior change is authorized by this document alone.
