# AI Defense System — Change Archive

This file is the canonical human-readable archive of repository changes.

## Archive policy

- Git history is the authoritative immutable record of every commit.
- This file provides a searchable engineering/security summary of the commit history.
- The GitHub Actions workflow regenerates it automatically after pushes to `main`.
- Archive-update commits are excluded to prevent recursive entries.
- Unmerged work remains represented by its branch and pull request until it reaches `main`.

## Change history

### 2026-09-29 — `9fa2305ff913` — Initial commit
- Author: misterchaiproject-ops
- Files changed:
  - `A	README.md`

### 2026-09-30 — `23fc3d51dbc0` — Add .gitignore for Python project
- Author: misterchaiproject-ops
- Files changed:
  - `A	.gitignore`

### 2026-09-30 — `dc500e7aa808` — Add contracts/actions.py with Action enum
- Author: misterchaiproject-ops
- Files changed:
  - `A	contracts/actions.py`

### 2026-09-30 — `fec9f14028a8` — Add contracts/roles.py with Role enum
- Author: misterchaiproject-ops
- Files changed:
  - `A	contracts/contracts/roles.py`

### 2026-09-30 — `229040cc869f` — Delete contracts/contracts/roles.py
- Author: misterchaiproject-ops
- Files changed:
  - `D	contracts/contracts/roles.py`

### 2026-09-30 — `60f073549695` — Add contracts/reason_codes.py with ReasonCode enum
- Author: misterchaiproject-ops
- Files changed:
  - `A	contracts/reason_codes.py`

### 2026-09-30 — `d71155c96657` — Add contracts/roles.py with Role enum
- Author: misterchaiproject-ops
- Files changed:
  - `A	contracts/roles.py`

### 2026-09-30 — `9744b1d33bdd` — Add contracts/validation_result.py
- Author: misterchaiproject-ops
- Files changed:
  - `A	contracts/validation_result.py`

### 2026-09-30 — `ae922604c619` — Add contracts/proposal.py with immutable Proposal
- Author: misterchaiproject-ops
- Files changed:
  - `A	contracts/proposal.py`

### 2026-09-30 — `13bcf814499c` — Add contracts/agent_identity.py with immutable AgentIdentity
- Author: misterchaiproject-ops
- Files changed:
  - `A	contracts/agent_identity.py`

### 2026-09-30 — `87523bbe5584` — Add contracts/__init__.py with public API
- Author: misterchaiproject-ops
- Files changed:
  - `A	contracts/__init__.py`

### 2026-09-30 — `e8560fb84c16` — Add guardrail/core.py with DeterministicGuardrail
- Author: misterchaiproject-ops
- Files changed:
  - `A	guardrail/core.py`

### 2026-09-30 — `a0f4fffdc7ed` — Add guardrail/__init__.py with public API
- Author: misterchaiproject-ops
- Files changed:
  - `A	guardrail/__init__.py`

### 2026-09-30 — `7fa8eccdcbff` — Add channel/core.py with SecureAgentChannel
- Author: misterchaiproject-ops
- Files changed:
  - `A	channel/core.py`

### 2026-09-30 — `9b60e28e4589` — Add channel/__init__.py with public API
- Author: misterchaiproject-ops
- Files changed:
  - `A	channel/__init__.py`

### 2026-09-30 — `371cb8573de0` — Add orchestrator/core.py with SecureOrchestrator
- Author: misterchaiproject-ops
- Files changed:
  - `A	orchestrator/core.py`

### 2026-09-30 — `fa66ccabfe0f` — Add orchestrator/__init__.py with public API
- Author: misterchaiproject-ops
- Files changed:
  - `A	orchestrator/__init__.py`

### 2026-09-30 — `6bfee0dccd7a` — Add pyproject.toml for project configuration
- Author: misterchaiproject-ops
- Files changed:
  - `A	pyproject.toml`

### 2026-09-30 — `9447318d7a80` — Add tests/test_smoke.py with basic end-to-end tests
- Author: misterchaiproject-ops
- Files changed:
  - `A	tests/test_smoke.py`

### 2026-09-30 — `b7e1cf9a71ea` — Add docs/REVIEW-003.md with post-MVP assessment
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/REVIEW-003.md`

### 2026-09-30 — `be418a927380` — Add tooling config: mypy, ruff, bandit, coverage
- Author: misterchaiproject-ops
- Files changed:
  - `M	pyproject.toml`

### 2026-09-30 — `95317d886286` — Fix: pass mypy --strict, add tooling configs
- Author: misterchaiproject-ops
- Files changed:
  - `A	aux | grep nano`
  - `M	contracts/proposal.py`
  - `M	guardrail/core.py`
  - `A	mypy_errors.txt`
  - `A	mypy_out.txt`
  - `A	poetry.lock`
  - `M	pyproject.toml`

### 2026-09-30 — `2c3c64b24629` — Refactor: modernize enums to StrEnum, pass ruff+bandit+mypy
- Author: misterchaiproject-ops
- Files changed:
  - `M	channel/core.py`
  - `M	contracts/actions.py`
  - `M	contracts/agent_identity.py`
  - `M	contracts/proposal.py`
  - `M	contracts/reason_codes.py`
  - `M	contracts/roles.py`
  - `M	contracts/validation_result.py`
  - `M	guardrail/core.py`
  - `M	orchestrator/core.py`
  - `A	ruff_out.txt`

### 2026-10-01 — `594cba19d07a` — Harden: fix default=str, validate Role types, add tests/__init__.py, sort imports
- Author: misterchaiproject-ops
- Files changed:
  - `M	channel/core.py`
  - `M	contracts/agent_identity.py`
  - `A	tests/__init__.py`
  - `M	tests/test_smoke.py`
  - `A	verify_out.txt`

### 2026-10-01 — `dc1ffadcfa7d` — Add CI workflow, lock file, pip-audit; unignore uv.lock
- Author: misterchaiproject-ops
- Files changed:
  - `A	.github/workflows/ci.yml`
  - `M	.gitignore`
  - `M	pyproject.toml`
  - `A	uv.lock`

### 2026-10-01 — `0c022435e34c` — Apply ruff format to all files
- Author: misterchaiproject-ops
- Files changed:
  - `M	channel/core.py`
  - `M	contracts/actions.py`
  - `M	contracts/agent_identity.py`
  - `M	contracts/proposal.py`
  - `M	contracts/roles.py`
  - `M	contracts/validation_result.py`
  - `M	guardrail/core.py`
  - `A	main`
  - `M	orchestrator/core.py`
  - `M	tests/test_smoke.py`
  - `M	uv.lock`
  - `M	verify_out.txt`

### 2026-10-01 — `cd3340174d18` — Add SESSION-003 report
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/SESSION-003.md`

### 2026-10-01 — `ac0a8915dcd0` — Add Master Plan v2.2 (Gemini-approved)
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/MASTER_PLAN.md`

### 2026-10-01 — `51b05e9b8545` — Phase 2: Add 31 tests for contracts/proposal.py (100% coverage)
- Author: misterchaiproject-ops
- Files changed:
  - `M	contracts/proposal.py`
  - `A	tests/unit/__init__.py`
  - `A	tests/unit/contracts/__init__.py`
  - `A	tests/unit/contracts/test_proposal.py`

### 2026-10-01 — `705a3b269908` — Fix: apply ruff format to proposal.py
- Author: misterchaiproject-ops
- Files changed:
  - `M	contracts/proposal.py`

### 2026-10-01 — `24b51f6eee6d` — refactor: migrate to src/ layout for package isolation
- Author: misterchaiproject-ops
- Files changed:
  - `M	.github/workflows/ci.yml`
  - `M	pyproject.toml`
  - `R100	channel/__init__.py	src/channel/__init__.py`
  - `R100	channel/core.py	src/channel/core.py`
  - `R100	contracts/__init__.py	src/contracts/__init__.py`
  - `R100	contracts/actions.py	src/contracts/actions.py`
  - `R100	contracts/agent_identity.py	src/contracts/agent_identity.py`
  - `R100	contracts/proposal.py	src/contracts/proposal.py`
  - `R100	contracts/reason_codes.py	src/contracts/reason_codes.py`
  - `R100	contracts/roles.py	src/contracts/roles.py`
  - `R100	contracts/validation_result.py	src/contracts/validation_result.py`
  - `R100	guardrail/__init__.py	src/guardrail/__init__.py`
  - `R100	guardrail/core.py	src/guardrail/core.py`
  - `R100	orchestrator/__init__.py	src/orchestrator/__init__.py`
  - `R100	orchestrator/core.py	src/orchestrator/core.py`

### 2026-10-01 — `5f0d2be3e03c` — docs: add Constitution, Lessons, Verification Protocol, Master Plan v2.3
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/CONSTITUTION.md`
  - `A	docs/LESSONS_LEARNED.md`
  - `M	docs/MASTER_PLAN.md`
  - `A	docs/VERIFICATION_PROTOCOL.md`

### 2026-10-01 — `782fa12027cf` — Phase 2: Harden agent_identity (DoS + info-disclosure fixes) + 37 tests (100% coverage)
- Author: misterchaiproject-ops
- Files changed:
  - `M	src/contracts/agent_identity.py`
  - `A	tests/unit/contracts/test_agent_identity.py`

### 2026-10-02 — `5971a1856bb3` — chore: add pre-commit hook + VS Code auto-fix settings
- Author: misterchaiproject-ops
- Files changed:
  - `A	.pre-commit-config.yaml`
  - `M	docs/LESSONS_LEARNED.md`
  - `M	pyproject.toml`
  - `M	src/contracts/validation_result.py`
  - `A	tests/unit/contracts/test_reason_codes.py`
  - `A	tests/unit/contracts/test_validation_result.py`
  - `M	uv.lock`

### 2026-10-02 — `626a3032df4a` — feat: add self-healing system + tests for roles and actions
- Author: misterchaiproject-ops
- Files changed:
  - `M	.pre-commit-config.yaml`
  - `A	Makefile`
  - `M	pyproject.toml`
  - `A	scripts/check.sh`
  - `A	scripts/fix.sh`
  - `A	scripts/verify.sh`
  - `A	tests/unit/contracts/test_actions.py`
  - `A	tests/unit/contracts/test_roles.py`

### 2026-10-02 — `91541ecd2c53` — Phase 2: Add 29 tests for guardrail/core.py
- Author: misterchaiproject-ops
- Files changed:
  - `A	tests/unit/guardrail/__init__.py`
  - `A	tests/unit/guardrail/test_core.py`

### 2026-10-02 — `4f5d2eb039d5` — Fix ruff F841 unused variable
- Author: misterchaiproject-ops
- Files changed:
  - `A	tests/unit/channel/__init__.py`
  - `A	tests/unit/channel/test_core.py`

### 2026-10-02 — `ff3eba377810` — docs: add PROMPT_TEMPLATE.md + enhance fix.sh with pre-commit hooks
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/PROMPT_TEMPLATE.md`
  - `M	scripts/fix.sh`
  - `M	tests/unit/channel/test_core.py`

### 2026-10-02 — `8f088245d9a4` — Phase 2: channel/core.py at 100% coverage (49 tests) + enhanced fix.sh
- Author: misterchaiproject-ops
- Files changed:
  - `M	.gitignore`
  - `A	scripts/fix_style.sh`
  - `M	tests/unit/channel/test_core.py`

### 2026-10-02 — `0f0d1aa02445` — Phase 2: Add orchestrator tests (100% coverage) + API tools + style fixes
- Author: misterchaiproject-ops
- Files changed:
  - `M	.gitignore`
  - `M	docs/PROMPT_TEMPLATE.md`
  - `A	scripts/check_api.sh`
  - `A	scripts/show_api.sh`
  - `M	src/channel/core.py`
  - `M	src/contracts/proposal.py`
  - `M	src/guardrail/core.py`
  - `A	tests/unit/orchestrator/__init__.py`
  - `A	tests/unit/orchestrator/test_core.py`
  - `D	verify_out.txt`

### 2026-10-02 — `60f9b2f8afa1` — Add pip-audit to make check (5th step)
- Author: misterchaiproject-ops
- Files changed:
  - `M	scripts/check.sh`

### 2026-10-02 — `ff2b6d9aff3b` — feat: add Hypothesis property-based tests + Dependabot + pre-commit hypothesis support
- Author: misterchaiproject-ops
- Files changed:
  - `A	.github/dependabot.yml`
  - `M	.pre-commit-config.yaml`
  - `M	tests/unit/contracts/test_proposal.py`

### 2026-10-02 — `315bbd1683d1` — docs: add THREAT_MODEL.md (Phase 2.5 - 9 sections, 201 lines)
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/THREAT_MODEL.md`

### 2026-10-03 — `65239e791450` — feat(channel): persist _ReplayCache via SQLite (Phase 3 - G1)
- Author: misterchaiproject-ops
- Files changed:
  - `M	src/channel/core.py`
  - `M	tests/unit/channel/test_core.py`

### 2026-10-03 — `81335fa0bc85` — feat(channel): add key ring rotation with legacy compatibility (Phase 3 - G2)
- Author: misterchaiproject-ops
- Files changed:
  - `M	src/channel/core.py`
  - `M	tests/unit/channel/test_core.py`

### 2026-10-03 — `65316b1ec077` — chore(scripts): add ruff format --check to make check pipeline
- Author: misterchaiproject-ops
- Files changed:
  - `M	scripts/check.sh`

### 2026-10-03 — `436d57e1d8d4` — feat(scripts): add safe-commit.sh atomic pipeline
- Author: misterchaiproject-ops
- Files changed:
  - `A	scripts/safe-commit.sh`

### 2026-10-03 — `8c54ca53306d` — feat(channel): wire db_path to SecureAgentChannel (G1-Wiring)
- Author: misterchaiproject-ops
- Files changed:
  - `M	src/channel/core.py`
  - `M	tests/unit/channel/test_core.py`

### 2026-10-03 — `265db8ed6a96` — chore(scripts): add coverage step [7/7] to make check
- Author: misterchaiproject-ops
- Files changed:
  - `M	Makefile`
  - `M	scripts/check.sh`

### 2026-10-03 — `d554b58e9c03` — chore(deps): add cryptography>=43.0 for audit encryption (G5)
- Author: misterchaiproject-ops
- Files changed:
  - `M	pyproject.toml`
  - `M	uv.lock`

### 2026-10-03 — `5504cb42c758` — chore(tooling): enable --unsafe-fixes and fix mypy pre-commit hook
- Author: misterchaiproject-ops
- Files changed:
  - `M	.pre-commit-config.yaml`
  - `M	scripts/fix.sh`

### 2026-10-03 — `0e0d6cab7e0f` — feat(audit): add SecureAuditLog with AES-256-GCM (G5 MVP)
- Author: misterchaiproject-ops
- Files changed:
  - `M	Makefile`
  - `M	pyproject.toml`
  - `M	scripts/check.sh`
  - `A	src/audit/core.py`
  - `A	tests/unit/audit/__init__.py`
  - `A	tests/unit/audit/test_core.py`

### 2026-10-03 — `3f3981ce4fb8` — feat(audit): add package init and hardening tests (G5)
- Author: misterchaiproject-ops
- Files changed:
  - `A	src/audit/__init__.py`
  - `M	tests/unit/audit/test_core.py`

### 2026-10-03 — `770977643561` — docs(self-healing): add Self-Healing Foundation design document
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/SELF_HEALING.md`

### 2026-10-03 — `e184d64c67fe` — feat(doctor): add make doctor environment diagnostics (Self-Healing L1)
- Author: misterchaiproject-ops
- Files changed:
  - `M	Makefile`
  - `M	pyproject.toml`
  - `M	scripts/check.sh`
  - `A	src/doctor/__init__.py`
  - `A	src/doctor/__main__.py`
  - `A	src/doctor/core.py`
  - `A	tests/unit/doctor/__init__.py`
  - `A	tests/unit/doctor/test_core.py`

### 2026-10-03 — `68bc207d85bf` — feat(doctor): add CLI tests for doctor.__main__ (Self-Healing L1)
- Author: misterchaiproject-ops
- Files changed:
  - `M	tests/unit/doctor/test_core.py`

### 2026-10-03 — `c2ea654ad417` — fix(doctor): correct 2 test assertions and imports
- Author: misterchaiproject-ops
- Files changed:
  - `A	=`
  - `M	tests/unit/doctor/test_core.py`

### 2026-10-03 — `5bc2deb77e99` — chore: remove accidental '=' file from repo root
- Author: misterchaiproject-ops
- Files changed:
  - `D	=`

### 2026-10-03 — `e9c555162866` — chore(scripts): harden safe-commit with blocklist and auto-cleanup (V2)
- Author: misterchaiproject-ops
- Files changed:
  - `M	scripts/safe-commit.sh`

### 2026-10-03 — `2d2ea99cdc9b` — fix(doctor): replace mtime check with 'uv lock --check' subprocess
- Author: misterchaiproject-ops
- Files changed:
  - `M	src/doctor/core.py`
  - `M	tests/unit/doctor/test_core.py`

### 2026-10-06 — `98b87de2a83b` — feat(channel): add audit_log parameter to SecureAgentChannel (G5.1 MVP)
- Author: misterchaiproject-ops
- Files changed:
  - `A	.devcontainer/setup.sh`
  - `M	src/channel/core.py`

### 2026-10-06 — `ef2a0ed7b827` — chore(devcontainer): add self-configuring container
- Author: misterchaiproject-ops
- Files changed:
  - `A	.devcontainer/devcontainer.json`
  - `M	.devcontainer/setup.sh`

### 2026-10-06 — `a67faa581e75` — docs: update MASTER_PLAN with current phase 3.5
- Author: misterchaiproject-ops
- Files changed:
  - `M	docs/MASTER_PLAN.md`

### 2026-10-06 — `f44c5cd26212` — docs: add PROJECT_STATE + ROADMAP_FULL + ARCHITECTURE_MAP
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/ARCHITECTURE_MAP.md`
  - `A	docs/PROJECT_STATE.md`
  - `A	docs/ROADMAP_FULL.md`

### 2026-10-13 — `a5fedbc03249` — docs: add STRATEGIC_ROADMAP + TECHNICAL_SPECIFICATION
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/STRATEGIC_ROADMAP.md`
  - `A	docs/TECHNICAL_SPECIFICATION.md`

### 2026-10-14 — `af35ae5847c2` — feat(channel): add audit logging to verify_message (G5.2)
- Author: misterchaiproject-ops
- Files changed:
  - `D	ruff_out.txt`
  - `M	src/channel/core.py`
  - `M	tests/unit/channel/test_core.py`

### 2026-10-19 — `4200b7ea1264` — docs: add canonical change archive
- Author: misterchaiproject-ops
- Files changed:
  - `A	docs/CHANGELOG.md`

### 2026-10-19 — `bf1bd2c414fe` — chore: add automated change archive generator
- Author: misterchaiproject-ops
- Files changed:
  - `A	scripts/update_change_archive.py`

### 2026-10-19 — `469280a96ff0` — ci: automate change archive on main
- Author: misterchaiproject-ops
- Files changed:
  - `A	.github/workflows/change-archive.yml`
