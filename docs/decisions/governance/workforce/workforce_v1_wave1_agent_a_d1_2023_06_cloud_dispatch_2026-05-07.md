# Workforce v1 wave 1 — Agent A — D1 2023-06 cloud dispatch

Date: 2026-05-07
Branch target: `feature/cloud/deepdive/d1-2023-06-falsifier`
Mode: `RESEARCH`
Worker class: `deep-dive`
Activation state: `primary`
Status: `dispatch-ready / implementation-prepared / non-authoritative`

## Authority fence

Det här dokumentet är Agent A:s dispatch-kontrakt.
Det är inte ny governance, inte merge-auktoritet och inte shared-truth-auktoritet.

Worker outputs förblir bounded evidence only.
De får inte promotas till repo-sanning, readiness eller runtime-authority utan uttrycklig control / integration-granskning.

## Ownership tuple

- **Window:** `2023-06`
- **Question class:** `D1 external falsifier`
- **Output class:** `implementation-prepared deep-dive`
- **Activation state:** `primary`

## Dispatch pins

- **Base branch:** `feature/next-slice-2026-05-06`
- **Base SHA:** `cf852ad8a559dfd8313405c3c30806fd3ff00e08`
- **Question fingerprint:** `qfp_d1_2023_06_external_falsifier_v1`
- **Change class:** `helper-backed research-evidence slice`

## Exact question

Can one exact `2023-06` low-zone `insufficient_evidence` external surface support a bounded D1 external falsifier slice without reopening March, July `2024`, late-2024, or any annual-wide search?

## Source anchors

Primary current-branch anchors:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_bank_state_synthesis_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`
- `results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json`

Historical provenance anchor only:

- retained branch `feature/wt/deepdive/d1-2023-06-falsifier`
- commit `a1732698`
- path `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_precode_packet_2026-05-07.md`

Den branch-lokala packeten ovan är provenance only.
Det här dispatch-dokumentet är det kontrollerande kontraktet för cloud-körningen.

## Scope IN

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_precode_packet_2026-05-07.md`
- `scripts/analyze/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_20260507.py`
- `tests/backtest/test_ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier.py`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_2026-05-07.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_2026-05-07.md`

## Scope OUT

- all `2017-06` corroborative files
- all `2023-04` fallback files
- `GENESIS_WORKING_CONTRACT.md`
- `workforce_roadmap.md`
- `docs/governance/**`
- `src/**`
- `config/**`
- March subjects as primary loop
- July `2024` as primary subject
- late-2024 as reopened transport loop

## Allowed inputs

- all source anchors listed above
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json`
- `results/evaluation/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.json`

## Allowed outputs

- one refreshed or recreated precode packet on current branch
- one read-only analysis helper
- one targeted hermetic test
- one deterministic JSON artifact
- one human-readable analysis note
- one bounded branch-local PR

## Forbidden surfaces

- runtime/default/config-authority
- shared truth writes
- backlog / roadmap / decision promotion
- new threshold search
- new feature-family search
- widening beyond `2023-06`
- use of `clarity_score` in PASS/FAIL
- backfill or inferred rescue of `clarity_raw`

## Done criteria

- the exact `2023-06` target and anti-target/context surface is row-locked explicitly
- the D1 bank ceilings remain frozen from the admitted 2026-05-05 context-clean artifact
- helper, targeted test and analysis note exist only inside Scope IN
- deterministic rerun hash proof exists for the emitted JSON artifact
- output explicitly separates `observed`, `inferred`, and `unverified`
- the note states what the slice does **not** prove

## Stop conditions

- the exact `2023-06` surface cannot be row-locked honestly
- required inputs are missing or non-evaluable
- the work begins to overlap Agent B or Agent C ownership tuples
- the slice requires March, July `2024`, late-2024, or annual-wide search to remain meaningful
- the output would imply runtime/default/promotion authority

## Escalation conditions

- the slice needs a wider corroborative control before any honest verdict exists
- `clarity_raw` absence would force interpretation beyond the allowed fail-closed rule
- the worker believes `2017-06` or `2023-04` should replace the current primary lane
- any governance conflict or `base_sha` mismatch appears

## Required return format

- `status`
- `artifacts`
- `summary`
- `observed`
- `inferred`
- `unverified`
- `what_this_does_not_prove`
- `contradictions_found`
- `assumptions_rejected`
- `recommended_next_step`
- `recommended_integration_class`
- `provenance`
- `base_sha_confirmed`
- `scope_adherence_report`

## What this brief does not authorize

Det här dispatch-kontraktet gör Agent A implementation-prepared, men inte merge-självständig.
Det autoriserar inte shared-truth writes, runtime-förslag eller backlog-promotion.
