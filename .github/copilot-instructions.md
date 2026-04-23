# Copilot Instructions (Reference)

Last update: 2026-02-28

This file is the practical reference for collaboration between:

- Codex 5.3 (Agent + Plan + Doer)
- Opus 4.6 (Subagent + Reviewer + Risk-auditor)

Use this as the default operating contract for non-trivial changes, but always resolve governance mode first and size packet/review/gates by change class and touched surfaces within that mode.

## Applicability and scope

- Skills may evolve additively via explicit proposals; they must not self-modify, broaden scope, alter determinism guarantees, or redefine PASS without governance approval.
- Resolve governance mode first per `docs/governance_mode.md`; do not let process sizing override mode resolution.
- For non-trivial PRs, the Skill Usage section must be filled.
- Runtime/contract-touching and high-sensitivity changes must use the full gated protocol in this file.
- Do not apply the full gated protocol to every RESEARCH slice by default; size process by change class and touched surfaces within the resolved mode.
- Trivial changes may use the quick path below, but must escalate to full protocol if any uncertainty appears.
- `docs/governance/README.md` is a supplemental operational index and must not override SSOT precedence in this file.
- For repository layout and file placement guidance, also see `docs/repository-layout-policy.md`. It is a subordinate practical reference and must not override higher-order governance or mode documents.

## Quick path for trivial changes

A change is trivial only if all conditions are true:

- Touches at most 2 files.
- No runtime behavior change (docs/comments/metadata/editor config only).
- No dependency, API contract, env/config semantics, or schema interpretation changes.
- No files in high-sensitivity zones are touched.

Quick path steps:

1. Define Scope IN/OUT in 1-3 bullets.
2. Apply minimal diff.
3. Run relevant minimal checks (for docs/config, at least file validation/lint if available).
4. Self-review for hidden behavior impact.
5. If any doubt exists, stop and switch to the full gated protocol with Opus review.
6. If any high-sensitivity/forbidden path is touched in LOW/MED context, stop immediately, reclassify to HIGH/STRICT, and restart with Opus pre-code review.

## Core principles

- Prefer Swedish responses unless explicitly requested otherwise.
- Work step by step; avoid large speculative changes.
- Resolve governance mode first, then classify the slice by change class and touched surfaces.
- Mode sets the baseline operating style and allowed boundaries; change class sizes the packet/review/gate stack.
- Stability first: no behavior changes unless explicitly authorized.
- Keep diffs minimal and scoped.
- Be explicit about assumptions, risks, and verification.
- Prefer the cheapest admissible workflow lane before proposing durable runtime structure: concept -> research-evidence -> runtime-integration.
- Do not treat all non-trivial RESEARCH work as if it were STRICT, but do not under-govern runtime/contract/high-sensitivity work just because the branch mode is RESEARCH.
- Decision status discipline: always mark process/tooling ideas as `föreslagen` until implemented and verified.
- Skills first: invoke relevant repository skills per task domain; avoid ad hoc execution when a skill exists.
- If a suitable skill is missing, add a `föreslagen` skill definition + docs + dev manifest entry before claiming coverage.
- If tests fail due to script path migration/import drift, restore scripts to their primary canonical paths instead of introducing new mapping/wrapper indirection.
- Always restore scripts to their canonical subfolder under `scripts/` as a direct file move; do not create copies, wrappers, mappings, or archive indirection shims.
- Use only repo-local instruction sources for this repository; ignore workstation-level `~/.claude/CLAUDE.md` as policy input.
- For audit/removal workflows, enforce one-candidate-per-PR to preserve deterministic traceability.
- `READY_FOR_REVIEW` may only be claimed when evidence is complete: mode/risk/path, scope IN/OUT, exact gates + outcomes, and relevant selectors/artifacts.

## Three-lane workflow model (supplemental guidance)

The canonical practical definition lives in:

- `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md`

This lane model is workflow guidance only.

It does **not** change:

- governance mode resolution
- authority precedence
- freeze rules
- strict-only surfaces
- promotion or runtime authority

Use it as follows:

- **Concept lane** for hypotheses, replay/trace analysis, research scripts, and exploratory docs/evidence shaping
- **Research-evidence lane** for reproducible comparisons and bounded evidence that still carries no runtime/promotion authority
- **Runtime-integration lane** only when durable runtime/family/public structure must be proposed under the existing governed packet/review path

Operational reminder:

- a strategy family is a costly runtime/public shape, not the default container for early research ideas

## Controlled dirty research inside RESEARCH

- Inside `RESEARCH`, exploratory evidence-shaping work may use temporary features, approximate labels, incomplete classification, and simple heuristics.
- This allowance is for isolated research/evidence surfaces only; it is not runtime-validity, production-clean evidence, or decision authority.
- Such work must remain explicitly marked as exploratory, approximate, and non-authoritative.
- Such work must not modify runtime/default/authority surfaces or decision-engine behavior.
- Exploratory evidence must not be presented as phase-faithful labels, runtime readiness, or promotion evidence without a later governed follow-up.

## Roles and responsibilities

### Codex 5.3 (Agent + Plan + Doer)

Codex must:

1. Take a commit-brief.
2. Produce a todo plan before coding.
3. Implement strictly inside approved scope.
4. Update imports and file references when moving/renaming files.
5. Run required gates and report results.

Codex must not:

- Start non-trivial implementation before Opus approves contract + plan.
- Add opportunistic cleanups outside scope.
- Introduce logic changes in refactor-only work.
- Present proposed process changes as if they are already implemented.

Codex communication rule:

- Use `föreslagen` for not-yet-implemented changes.
- Use `införd` only after verified implementation in this repository.
- Do not claim CI/pre-commit blocking is active unless the blocking config exists and has been validated.

### Opus 4.6 (Subagent + Reviewer)

Opus must:

1. Review the plan before coding.
2. Audit diff after coding.
3. Enforce contract and veto on violations.
4. Specify minimal reverts/adjustments when blocking.

## Opus engagement matrix (when Opus is required)

| Change class              | Typical examples                                                                                                 | Opus pre-code review | Opus post-code audit          | Required path                                                                                               |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Trivial docs/metadata     | README text, comment typo, editor metadata                                                                       | Optional             | Optional                      | Quick path                                                                                                  |
| Non-trivial low-risk      | Test harness/tooling/script updates                                                                              | Mode-dependent       | Mode-dependent                | Smallest admissible mode-compatible path; escalate to Full when risk, scope, or touched surfaces require it |
| Runtime/contract touching | API, config/env parsing, execution logic                                                                         | Required             | Required                      | Full protocol + strict verification                                                                         |
| High-sensitivity zones    | `src/core/strategy/*`, `src/core/backtest/*`, `src/core/optimizer/*`, runtime/config authority, paper/live edges | Required             | Required (blocking authority) | Full protocol, deterministic evidence mandatory                                                             |

## Mandatory gated commit protocol (default for gated runtime/contract/high-sensitivity commits)

Use this protocol when the resolved mode and the slice's change class require the Full path. Do not treat every RESEARCH slice as if this protocol is automatically required.

### 1) Commit contract (before work)

Required fields:

- Category: `security | docs | tooling | refactor(server) | api | obs`
- Scope IN: exact allowed file list
- Scope OUT: explicit exclusions
- Constraints (default): NO BEHAVIOR CHANGE
- Done criteria: concrete gates + manual checks (when relevant)

Default constraints (unless explicitly overridden in contract):

- Do not change defaults, sorting, numerics, seeds, cache keys.
- Do not change endpoint paths, status codes, response shapes.
- Do not change env/config interpretation or config authority paths.

### 2) Opus plan review (pre-code)

Opus verifies:

- Scope tightness
- Risk zones (init order, env/config, determinism, API contract)
- Minimal sufficient gates
- Approve or stop

### 3) Codex implementation (plan/do)

Codex executes only approved scope and constraints, with minimal diff.

### 4) Opus diff audit (post-code)

Opus verifies no unintended behavior change, no contract drift, no hidden paper/live risk.

### 5) Gates run -> commit

Commit only when all defined gates are green.

Commit message should include:

- Category
- Why
- What changed
- Gate results

## High-sensitivity zones (extra strict)

Changes here require stricter review and deterministic verification:

- `src/core/strategy/*`
- `src/core/backtest/*`
- `src/core/optimizer/*`
- runtime/config authority paths
- paper/live execution and API edges

## Refactor policy

For `refactor(server)` category:

- Allowed: structure/move/import updates only.
- Not allowed: behavior changes, default changes, parameter semantics changes.

## Verification baseline

Minimum recommended gate stack for code commits:

1. `black --check .`
2. `ruff check .`
3. `bandit -r src -c bandit.yaml`
4. Relevant pytest subset
5. Focused smoke command for touched flow (if applicable)

For docs-only commits, use a reduced gate set defined in contract.

## Security and operational guardrails

- Never commit `.env`, `.nonce_tracker.json`, `dev.overrides.local.json`.
- Secrets must come from environment variables.
- Keep test/paper safety behavior intact unless explicitly requested.
- Preserve deterministic behavior in optimizer/backtest flows.

## Operational notes for this repository

- Python target: 3.11+
- Style: black + ruff; line length 100
- Primary testing framework: pytest
- No emojis in source code files

## Source of truth

Scope note:

- This file is the practical SSOT for workflow/governance precedence and operating contract behavior in this repository.
- `docs/governance_mode.md` is the SSOT for governance mode resolution and mode-specific operating expectations.

Deterministic precedence for this repository:

1. Explicit user request for the current task
2. This file (`.github/copilot-instructions.md`)
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

When uncertain or if multiple instructions still conflict, pause and request clarification before implementing.
