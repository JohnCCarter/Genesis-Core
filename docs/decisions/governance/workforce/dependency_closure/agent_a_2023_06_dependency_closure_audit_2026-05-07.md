# Agent A 2023-06 dependency closure audit

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `manual-draft / non-authoritative / dispatch-blocked`

This packet is a manual dependency-closure draft stored under `docs/` for research-evidence traceability only. It is non-authoritative, is not consumed by runtime or dispatch tooling, and does not authorize cloud relaunch; `dispatch_allowed` remains `false` until every required input is tracked on the target branch or captured through an approved artifact mechanism.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW` — docs-only dependency audit for one already-observed cloud failure
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — cheapest admissible lane because this slice documents one real dependency failure without implementing compiler, store, or bundle logic
- **Objective:** make Agent A wave-1 `2023-06` cloud dependency closure explicit and fail-closed
- **Candidate:** `qfp_d1_2023_06_external_falsifier_v1`
- **Base SHA:** `cf852ad8a559dfd8313405c3c30806fd3ff00e08`

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/governance/workforce/workforce_v1_wave1_cloud_batch_dispatch_2026-05-07.md`
  - `docs/decisions/governance/workforce/workforce_v1_wave1_agent_a_d1_2023_06_cloud_dispatch_2026-05-07.md`
  - `docs/governance/worker_governance_envelope.md`
  - tracked analysis notes listed below
  - tracked context-clean artifact `results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json`
- **Candidate / comparison surface:** local-only annual diff artifact `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json`
- **Vad ska förbättras:** explicit declaration of repo-visible vs local-only required inputs for one real cloud worker slice
- **Vad får inte brytas / drifta:** no runtime/config/governance SSOT changes; no compiler/store implementation claims; no silent relaunch authorization
- **Reproducerbar evidens som måste finnas:** pinned hashes for tracked repo inputs and an explicit missing-dependency record for the annual diff artifact

## Scope

- **Scope IN:**
  - `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_dependency_closure_audit_2026-05-07.md`
  - `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_dependency_manifest_2026-05-07.yaml`
  - `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_repo_snapshot_manifest_2026-05-07.yaml`
  - `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_missing_dependency_report_2026-05-07.yaml`
- **Scope OUT:**
  - `.gitignore`
  - `docs/contracts/**`
  - `docs/governance/worker_governance_envelope.md`
  - `workforce_roadmap.md`
  - all `src/**`, `tests/**`, `scripts/**`, `config/**`, `results/**`, and `data/**` content changes
  - any cloud PR state changes
- **Expected changed files:** `4`
- **Max files touched:** `4`

## Skill usage

- No suitable repository skill was found for this bounded docs/governance dependency-closure slice.
- A dedicated dependency-closure skill is **föreslagen**, not **införd**.

## Closure subject

- `task_id`: `workforce_v1_agent_a_2023_06_dependency_closure`
- `dispatch_id`: `workforce_v1_agent_a_2023_06_dependency_closure_2026-05-07`
- `worker_class`: `deep-dive`
- `lane`: `research-evidence`
- `resolved_mode`: `RESEARCH`
- `question`: Can Agent A's `2023-06` external falsifier lane be dispatched honestly to cloud using only repo-visible or explicitly captured dependencies?
- `dispatch_verdict_for_current_state`: `blocked`

## Observed dependency inventory

### Satisfied repo-visible dependencies

| Path | Role | SHA256 | Notes |
| --- | --- | --- | --- |
| `docs/decisions/governance/workforce/workforce_v1_wave1_cloud_batch_dispatch_2026-05-07.md` | batch dispatch brief | `608a7226cbdb172b1668fa24f671be6396f9d5b0db57eadad4049eb67c670cf9` | tracked + remote-visible |
| `docs/decisions/governance/workforce/workforce_v1_wave1_agent_a_d1_2023_06_cloud_dispatch_2026-05-07.md` | worker dispatch brief | `34d70e8deda007d14f3fc63115c4b4899db0998902f7e3f50a1bcd87cf06f8e5` | tracked + remote-visible |
| `docs/governance/worker_governance_envelope.md` | worker envelope authority narrow spec | `89978bb58884e8e2c7f3dbb51294b0a98f5dcf836b31942ed88af0ab81a545f2` | tracked + remote-visible |
| `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.md` | context-clean analysis anchor | `0745d08dca788162fd290e390067b73fc99b497d07bd6bf8deb40b96c6769c8d` | tracked + remote-visible |
| `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_bank_state_synthesis_2026-05-06.md` | D1 bank synthesis anchor | `991c238ca67b4566fd8f55ba15da335fdc4d122ca00e263ad4df793d437110c6` | tracked + remote-visible |
| `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md` | mixed-year pocket anchor | `644273f0964431e471ee109be2669afecf9bca897eb12b7c57c59da39bb35f11` | tracked + remote-visible |
| `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md` | annual-shape comparison anchor | `dd9c6d8ca9cc8bfaef1c3cd0b70424f98b7bf39acc176cbe3e595768fa9c3f92` | tracked + remote-visible |
| `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md` | annual evidence anchor | `ad254afaff162c1258249c9e27f0437b6b0c19e74d4103a97fec5686259aef4d` | tracked + remote-visible |
| `results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json` | tracked machine-readable context-clean artifact | `194e4e6f188999277ecefa6ad72c399f30a1bfbec219cc072fdfea7aa2d9be04` | tracked + remote-visible |

### Missing from cloud closure

| Path | Exists locally | Tracked | Remote-visible | SHA256 | Size bytes | Effect |
| --- | --- | --- | --- | --- | ---: | --- |
| `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json` | `true` | `false` | `false` | `8b8ca2434056cf046202f064d33736d24bb9b8e41fdafc71d84d202e9c085940` | `1249971` | blocks honest cloud dispatch |

### Operational state

Observed from the dispatch brief and worker envelope:

- no required local session-state file is explicitly named for this slice
- no `~/.claude/state/genesis-core/*` file is required by the current dispatch contract
- this slice can be compiled from dispatch docs plus explicit artifacts; uncaptured session state remains inadmissible

## Closure verdict

- `dispatch_allowed`: `false`
- `dispatch_block_reason`: `missing_required_artifact`
- `blocking_dependency`: local-only, non-tracked annual diff artifact under `results/backtests/**`
- `worker_behavior_if_unfixed`: `blocked` at preflight or deterministic `fail-closed` if the worker contract explicitly allows a missing-source outcome
- `recommended_storage_class`: artifact-store-managed or explicitly bundled MVP capture
- `forbidden_remediation`: ad hoc local search, inference from partial context, or silent substitution with another artifact

## Produced manual drafts

- `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_dependency_manifest_2026-05-07.yaml`
- `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_repo_snapshot_manifest_2026-05-07.yaml`
- `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_missing_dependency_report_2026-05-07.yaml`

## Observed

- Agent A requires one annual diff input that exists locally but is not tracked in git.
- All dispatch/governance/analysis anchors needed to describe the slice are tracked and hashable.
- The tracked context-clean JSON artifact is repo-visible and can be pinned in a manifest.
- No required session-state file is currently declared for this slice.

## Inferred

- The annual diff artifact should be treated as an immutable external artifact or an explicitly bundled MVP input rather than an assumed local file.
- This slice can be safely compiled into a future dependency-closure workflow because the missing input boundary is narrow and explicit.
- Agent A's prior `source_data_unavailable` outcome is governance-compatible for cloud, but it is not a substitute for a complete closure.

## Unverified

- Whether the local annual diff artifact is fully reproducible from currently committed instructions alone.
- Whether the local annual diff artifact contains any hidden secondary dependencies beyond the file itself.
- Whether a future artifact-store capture for this file should carry a canonical artifact ID or dataset ID.
- Whether later Agent A variants will require any session-state snapshot beyond the current dispatch docs.

## Recommended next step

Capture the annual diff artifact through an approved immutable reference path (artifact store or explicit MVP bundle), then regenerate this same dependency manifest with `dispatch_allowed: true` only after the captured object is hash-pinned and authorized for the task.
