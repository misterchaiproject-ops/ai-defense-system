# AI Defense System — Codex Engineering Rules

## Mission

This repository is a security-critical Python project for protecting AI-agent systems, workflows, and supporting infrastructure.

Codex is an implementation assistant. It is **not** the project architect, security authority, or final approver.

## Authority Model

- Architecture and security decisions require explicit human approval.
- Codex must implement approved specifications; it must not silently expand scope.
- GitHub CI is a verification gate, not permission to weaken tests or security controls.
- The final merge decision belongs to the project owner/reviewer.

## Mandatory Change Discipline

1. Work on an isolated non-main branch unless explicitly instructed otherwise.
2. Read the relevant architecture, contracts, tests, and documentation before editing.
3. Identify the exact files allowed to change before implementation.
4. Keep the diff minimal and directly related to the task.
5. Do not rename, move, delete, or create unrelated files.
6. Do not change public APIs, contracts, protocol formats, dependency direction, or security boundaries without explicit approval.
7. Never perform broad automatic rewrites or repository-wide `--fix` operations.
8. Never modify generated/archive records manually unless the task explicitly requires it and the repository's archival mechanism is respected.
9. Never commit secrets, credentials, tokens, private keys, or sensitive environment data.
10. Preserve backward compatibility unless the task explicitly authorizes a breaking change.

## Security Rules

1. Fail closed for security-sensitive validation and authorization paths.
2. Do not weaken authentication, authorization, replay protection, audit integrity, input validation, or cryptographic controls to make tests pass.
3. Do not suppress a security/lint finding without documenting the precise reason and scope.
4. Do not introduce dynamic code execution, shell execution, unsafe deserialization, or unrestricted filesystem/network access without explicit security review.
5. Treat logs, audit records, error messages, and traces as potentially sensitive.
6. Preserve constant-time comparison where cryptographic verification requires it.
7. Do not introduce uncontrolled retries, recursion, concurrency, storage growth, or resource consumption.

## Tests-First and Verification

Before implementation:

- State the expected behavior.
- Identify relevant existing tests.
- Identify failure modes and boundary conditions.
- Define the minimum verification required.

After implementation:

1. Run the narrowest relevant test first.
2. Run the affected test suite.
3. Run formatting/lint checks.
4. Run type checking.
5. Run security checks.
6. Run the full project Quality Gate when practical.
7. Inspect the final diff for unrelated changes.

Never make a test weaker merely to obtain a green CI result.

## Architecture Boundaries

Respect the repository's established dependency direction and layer boundaries.

- Contracts define stable interfaces and shared domain types.
- Guardrails enforce policy and validation boundaries.
- Orchestration coordinates approved operations.
- Secure channels enforce secure message transport/protocol behavior.
- Audit components preserve security-relevant evidence.
- Doctor is currently a bounded diagnostic/environment component; do not turn it into unrestricted self-healing behavior without an approved design.

Do not create duplicate policy engines or bypass existing security boundaries.

## Self-Healing Restrictions

Self-healing is a future controlled capability, not an implicit permission.

Until a dedicated approved design exists, Codex must **not** implement autonomous remediation that can:

- modify arbitrary source code;
- alter security policy;
- change authentication/authorization rules;
- modify deployment configuration;
- delete security evidence;
- access arbitrary credentials/secrets;
- execute unrestricted shell commands;
- create unbounded retry or remediation loops.

Any future self-healing implementation must have explicit detection, authorization, bounded remediation, verification, rollback/escalation, and audit requirements.

## Resource and Data Governance

Do not introduce ResourcePolicy, DataPolicy, ExecutionPolicy, quota systems, retention rules, or tenant-isolation mechanisms by assumption.

These require an approved specification covering:

- scope;
- trust boundaries;
- limits;
- failure behavior;
- observability;
- persistence;
- compatibility;
- security properties;
- tests.

## Path and Dependency Safety

Before changing imports, modules, or file locations:

- inspect existing import relationships;
- check for circular dependencies;
- preserve package boundaries;
- verify all references and tests;
- avoid duplicate modules with overlapping responsibilities.

Do not guess paths. Confirm them from the repository.

## Documentation and Evidence

Distinguish clearly between:

- VERIFIED — directly demonstrated by current repository/CI evidence;
- PARTIALLY VERIFIED — only part of the claim is demonstrated;
- CONTEXT/REPORTED — historical or externally reported information;
- PENDING — not yet verified;
- PROPOSED — design proposal, not implementation;
- ROADMAP — future intent.

Do not convert historical documentation into current facts without evidence.

## Change Completion Requirements

A task is not complete merely because code was generated.

The completion report must include:

- files changed;
- reason for each change;
- tests executed;
- verification results;
- known limitations;
- any remaining risks;
- whether the Quality Gate passed.

If verification cannot be performed, state that explicitly. Do not claim success without evidence.

## Stop Conditions

STOP and request review if:

- the requested change conflicts with architecture;
- a public/security-sensitive contract must change unexpectedly;
- the correct behavior is ambiguous;
- a security control must be weakened;
- a test appears to encode a security requirement that conflicts with the requested change;
- an unrelated failure is discovered;
- the change would require broad restructuring;
- multiple plausible fixes have materially different security consequences.

## Definition of Done

A change is ready for review only when:

- scope is satisfied;
- no unrelated files changed;
- relevant tests pass;
- required static/security checks pass;
- the diff has been inspected;
- no known path/dependency conflict was introduced;
- security-sensitive behavior has been explicitly considered;
- the result is accurately reported as verified, pending, or blocked.
