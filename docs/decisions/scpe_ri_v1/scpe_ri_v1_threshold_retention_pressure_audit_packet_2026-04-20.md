# SCPE RI V1 threshold retention pressure audit packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Required Path: `Full`
Category: `obs`
Constraint: `NO BEHAVIOR CHANGE`
Objective: explain whether raw defensive candidates retained in continuation via `confidence_below_threshold` form a near-miss defensive population or a materially weaker subpopulation on the frozen baseline replay surface.
Candidate: `RI threshold retention pressure audit`
Base SHA: `06a4e642`
Skills used: `python_engineering`

## Commit contract

### Scope IN

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_threshold_retention_pressure_audit_packet_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_threshold_retention_pressure_audit_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_threshold_retention_pressure_audit.py`
- `results/evaluation/scpe_ri_v1_threshold_retention_pressure_audit_2026-04-20.json`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `tmp/**`
- `results/research/**`
- `docs/scpe_ri_v1_architecture.md`
- runtime integration
- canonical replay regeneration
- edits to `scripts/analyze/scpe_ri_v1_router_replay.py`
- edits to `scripts/analyze/scpe_ri_v1_defensive_scarcity_audit.py`
- edits to prior audit/revision script logic
- any new threshold rule, defensive rule, or dwell rule
- any change to baseline or revision recommendation semantics

### Expected changed files

- packet
- report
- one new threshold-pressure audit script
- one new commit-safe JSON artifact

### Max files touched

- 4

## Audit question

The bounded question for this slice is:

- Among raw defensive candidates retained in continuation via `confidence_below_threshold`, are we seeing a near-miss defensive population close to switch acceptance, or a materially weaker subpopulation that stays well below observed defensive selection quality?

This audit is observational-only and bounded to the frozen baseline replay artifacts plus the unchanged replay script as an analysis reference. It does not introduce a new threshold rule, does not modify the current `NEEDS_REVISION` recommendation, and only classifies the observed decision-time profile of threshold-retained defensive candidates.

This audit is observational only. It reconstructs threshold-retained defensive-candidate profiles from frozen research artifacts using a research-side analytical mirror of the existing replay behavior; it does not modify or supersede canonical replay logic and does not propose a new threshold rule.

The audit script may execute helper definitions from `scripts/analyze/scpe_ri_v1_router_replay.py` via `runpy.run_path` only to reconstruct row-local raw target policy and decision-time state from frozen inputs. It does not regenerate canonical replay artifacts, and the run must fail if the frozen `results/research/scpe_v1_ri/**` replay-root surface changes.

Its purpose is limited to describing how threshold-retained raw defensive candidates compare against the wider raw defensive candidate population and against narrow comparator buckets already observed in the frozen baseline trace.

The audit emits descriptive metrics, deterministic example rows, and bounded comparator tables only. Any `near-miss`, `materially weaker`, or `mixed` phrasing belongs only in the implementation report as a non-authoritative analyst summary over frozen metrics; it must not be emitted by the script as a new threshold rule, recommendation rule, or replay-quality reinterpretation.

Any follow-up paths are `föreslagen` hypotheses only and are out of scope for this slice.

## Planned audit logic

- load frozen baseline routing trace + replay metrics + manifest
- load frozen Phase C entry rows
- reconstruct raw router targets and decision-time state with the unchanged research-only replay logic
- fail closed unless the frozen replay-root identity matches the expected replay manifest / replay metrics / routing trace hashes recorded by the prior scarcity slice
- derive all comparator buckets from the same reconstructed frozen candidate table using these exact selectors:
  - raw defensive candidates: `raw target policy = RI_defensive_transition_policy`
  - threshold-retained comparator: `selected_policy = RI_continuation_policy` and `switch_reason = confidence_below_threshold`
  - min-dwell-retained comparator: `selected_policy = RI_no_trade_policy` and `switch_reason = switch_blocked_by_min_dwell`
  - observed selected-defensive comparator: `selected_policy = RI_defensive_transition_policy`
- compute deterministic summary metrics for the threshold-retained subset, including:
  - count
  - avg/min/max for `ri_clarity_score`, `conf_overall`, `action_edge`, `bars_since_regime_change`
  - `zone` counts
  - `transition_bucket` counts
  - veto-reason counts
  - raw-switch-reason counts
- compute bounded comparator summaries for:
  - all raw defensive candidates
  - min-dwell-retained raw defensive candidates
  - observed selected-defensive raw defensive candidates
- emit stable example rows from the threshold-retained subset sorted deterministically by:
  - highest `action_edge`
  - then highest `conf_overall`
  - then highest `ri_clarity_score`
  - then lowest `row_index`
- leave any `near-miss`, `materially weaker`, or `mixed` interpretation to the report only, based on the emitted descriptive metrics

## Boundaries

This slice must:

- remain summary-only, observational-only, and non-authoritative
- treat `results/research/scpe_v1_ri/**` as frozen input only
- use the unchanged replay script only as an analysis reference for row-local reconstruction
- define comparator buckets only as descriptive reference cohorts from the same frozen reconstruction surface; they must not define an alternative acceptance policy, counterfactual recommendation rule, or threshold-retuning proposal
- emit one deterministic JSON summary under `results/evaluation/`
- emit one deterministic implementation report without volatile fields
- enforce deterministic outputs: sorted JSON keys, stable bucket ordering, no timestamps, no host/user metadata, and no random inputs

This slice must not:

- modify runtime or canonical replay logic
- alter prior revision or scarcity artifacts
- claim policy approval, release approval, or deployment readiness
- reinterpret the replay-quality rule itself
- turn the threshold-retained population into a recommendation for a new threshold

## Expected evidence

- exact threshold-retained raw defensive candidate count
- exact comparator counts for all raw defensive candidates, min-dwell-retained candidates, and observed selected-defensive candidates
- deterministic metric summaries for each bounded comparator bucket
- explicit statement in the report only of whether threshold-retained candidates look descriptively near-miss, materially weaker, or mixed relative to observed selected-defensive rows
- explicit statement that the slice describes observed decision-time profiles only and does not recommend a new threshold rule
- frozen input hashes and `read_only_inputs_confirmed = true`

## Gates required

- `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_threshold_retention_pressure_audit_packet_2026-04-20.md docs/analysis/scpe_ri_v1/scpe_ri_v1_threshold_retention_pressure_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_threshold_retention_pressure_audit.py results/evaluation/scpe_ri_v1_threshold_retention_pressure_audit_2026-04-20.json`
- explicit smoke run of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_threshold_retention_pressure_audit.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` (unchanged-surface guardrails only; not direct validation of the new audit logic)
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_threshold_retention_pressure_audit.py` with stable output-hash proof for both the JSON artifact and the report
- explicit proof that `results/research/scpe_v1_ri/**` remains unchanged before vs after both runs
- explicit proof that `scripts/analyze/scpe_ri_v1_threshold_retention_pressure_audit.py` does not import from `src/core/**`

## Stop conditions

- scope drift beyond the four scoped files
- any write to `results/research/scpe_v1_ri/**`
- any attempt to introduce a new threshold, defensive, or dwell rule
- any wording that turns the audit into runtime advice or promotion evidence

## Done criteria

- the threshold retention pressure audit is implemented and documented
- all listed gates pass
- Opus post-audit confirms the slice is still observational-only and governance-safe
