# Optimizer refactor trace reopen-shape packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the smallest honest current-branch interpretation of the retained optimizer refactor audit folder. It grants no refactor approval, no runtime or optimizer-behavior authority, and no queue by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice clarifies the current reading of retained optimizer refactor artifacts and chooses one future reopen shape only; it changes no source, tests, runtime, or optimizer behavior
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice narrows interpretation of historical optimizer refactor artifacts only; it does not reopen implementation work
- **Skill usage:** `none required` — bounded docs-only optimizer traceability slice; no repo-local skill matched this change
- **Objective:** make `docs/audit/refactor/optimizer/README.md` read truthfully on `feature/risk-hardening-wave2` and choose one exact future optimizer refactor subtopic without implying that the March artifacts are branch-current approval or completion
- **Base SHA:** `481269a7cdff4bb8352879b51704bcc4c6856b66`
- **Related artifacts:** `docs/audit/refactor/optimizer/README.md`, `docs/audit/refactor/optimizer/context_map_runner_split2_optuna_orchestration_validation_promotion_2026-03-13.md`, `docs/audit/refactor/optimizer/context_map_runner_split3_config_metadata_parameter_space_2026-03-13.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

### Scope

- **Scope IN:** this packet; one later-status note in `docs/audit/refactor/optimizer/README.md` that says the folder is historical traceability only on the current branch, records current observed optimizer file blast radius, and names one first admissible future subtopic
- **Scope OUT:** any edit to the March command packets or context maps themselves; any edit under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; any refactor plan that implies approval or immediate implementation; the already-dirty local governance docs `docs/decisions/governance/backtest_error_policy_reopen_shape_packet_2026-05-19.md` and `docs/decisions/governance/cache_schema_bump_selector_policy_carrier_decision_packet_2026-05-19.md`
- **Expected changed files:** `docs/decisions/governance/optimizer_refactor_trace_reopen_shape_packet_2026-05-19.md`, `docs/audit/refactor/optimizer/README.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and `docs/audit/refactor/optimizer/README.md`
- manual wording audit that the slice clarifies historical traceability only and does not imply current approval/completion
- manual wording audit that exactly one future reopen subtopic is named
- manual wording audit that no runtime/source/test/config behavior is changed

## Purpose

This packet answers one narrow question only:

- what is the smallest honest current-branch reading of the retained optimizer refactor folder, and what is the first admissible future optimizer refactor subtopic if a later reopen is needed?

## What changed in this slice

- `docs/audit/refactor/optimizer/README.md` now states more explicitly that the March optimizer split artifacts are historical traceability records on `feature/risk-hardening-wave2`
- the README now records current observed optimizer file sizes as branch-state context rather than leaving readers to infer current status from March packet names
- the README now names one first admissible future subtopic: the orchestration / validation / promotion boundary across current `runner.py` and `runner_optuna_orchestration.py`

## What did not change

- no optimizer refactor was approved or started
- no March packet or context map was rewritten as a live plan
- no `src/core/optimizer/**` behavior changed
- no tests, workflows, or gates changed

## Governing basis

### Observed

1. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` still lists `#16` as a current optimizer complexity risk and explicitly says there is no optimizer-specific tracked diagnostics note yet.
2. `docs/audit/refactor/optimizer/README.md` already says the folder is a navigation aid and that broader completion or approval must not be inferred from it.
3. The retained March context maps show two historical subtopics: orchestration / validation / promotion support and config / metadata / parameter-space extraction.
4. Current branch file sizes remain large: `src/core/optimizer/runner.py` = 1625 lines, `src/core/optimizer/runner_optuna_orchestration.py` = 1113 lines, `src/core/optimizer/runner_config.py` = 830 lines.

### Inferred

- The honest current-branch move is not to resurrect the March refactor folder as an active plan queue.
- The honest current-branch move is to clarify that the folder is historical traceability only and to choose one future reopen shape so a later worker does not infer that both March lines remain equally active by default.
- The first admissible future subtopic is the orchestration / validation / promotion boundary, because the current branch still shows the largest optimizer blast radius across `runner.py` and `runner_optuna_orchestration.py`, which aligns with the baseline `#16` risk statement more directly than the already-smaller config/metadata sidecar.

### Unverified in this packet

- whether a later implementation refactor should actually proceed
- whether the future reopen should stay docs-first or escalate directly to code planning
- whether a later branch should instead prioritize optimizer data-skip/promotion-gate questions ahead of structural refactor work

## Boundary decision

### Current standing conclusion

For `feature/risk-hardening-wave2`, the honest reading is:

- keep `docs/audit/refactor/optimizer/` as historical traceability only
- do not infer current approval, active queue status, or completion from the March file names
- if a later bounded reopen is needed, start with the orchestration / validation / promotion boundary across current `runner.py` and `runner_optuna_orchestration.py`

This packet therefore authorizes only a later-status note in the optimizer refactor README.

### Non-goals

This slice does **not**:

- approve optimizer refactor work
- select implementation sequencing beyond one future reopen shape
- rewrite the March packet set
- touch optimizer code, tests, or runtime behavior

## Hard stop and reopen rule

If a later slice needs any of the following, it must stop and reopen as a separate bounded packet:

- source changes under `src/core/optimizer/**`
- test rewrites or new optimizer behavior claims
- runtime/config/champion/promotion authority changes
- a different future subtopic than the one chosen here

## Bottom line

The smallest honest `#16` move is a **traceability-and-reopen-shape** slice: the retained optimizer refactor folder stays historical, but its README now says so explicitly for the current branch and points any future worker to one exact first reopen line instead of leaving the March artifacts to compete silently as implied active plans.
