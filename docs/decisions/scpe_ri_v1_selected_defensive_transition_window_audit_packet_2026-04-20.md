# SCPE RI V1 selected-defensive transition window audit packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Required Path: `Full`
Category: `obs`
Constraint: `NO BEHAVIOR CHANGE`
Objective: explain whether the tiny observed selected-defensive comparator bucket is best understood as an observed fresh-transition recency pocket distinct from the larger threshold-retained and min-dwell-retained defensive-candidate buckets on the frozen baseline replay surface.
Candidate: `RI selected-defensive transition window audit`
Base SHA: `ffb9e4dc`
Skills used: `python_engineering`, `ri_off_parity_artifact_check`

## Commit contract

### Scope IN

- `docs/decisions/scpe_ri_v1_selected_defensive_transition_window_audit_packet_2026-04-20.md`
- `docs/analysis/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py`
- `results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json`

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
- edits to prior audit/revision script logic
- any new threshold rule, defensive rule, or dwell rule
- any change to baseline or revision recommendation semantics

### Expected changed files

- packet
- report
- one new selected-defensive transition-window audit script
- one new commit-safe JSON artifact

### Max files touched

- 4

## Audit question

The bounded question for this slice is:

- Do the observed selected-defensive rows occupy an observed fresh-transition recency pocket that is structurally separate from the threshold-retained and min-dwell-retained raw defensive-candidate buckets, or are they simply the strongest score-like tail of the same broad stable defensive-candidate population?

This audit is observational-only and bounded to the frozen baseline replay artifacts plus the unchanged replay script as an analysis reference. It does not introduce a new defensive rule, does not introduce a new threshold rule or dwell rule, and does not change the current `NEEDS_REVISION` recommendation.

This audit is observational only. It reconstructs selected-defensive and comparator-bucket profiles from frozen research artifacts using a research-side analytical mirror of the existing replay behavior; it does not modify or supersede canonical replay logic.

The audit script may execute helper definitions from `scripts/analyze/scpe_ri_v1_router_replay.py` via `runpy.run_path` only to reconstruct row-local raw target policy and decision-time state from frozen inputs. It does not regenerate canonical replay artifacts, and the run must fail if the frozen `results/research/scpe_v1_ri/**` replay-root surface changes.

Its purpose is limited to describing whether observed selected-defensive routing appears inside a distinct fresh-transition recency pocket, with explicit recency and transition-bucket separation from the threshold-retained and min-dwell-retained comparator buckets.

The audit emits descriptive metrics, deterministic example rows, and bounded comparator tables only. Any `observed fresh-transition recency pocket`, `mixed`, or `overlapping` phrasing belongs only in the implementation report as a non-authoritative analyst summary over frozen metrics; it must not be emitted by the script as a new rule, recommendation, or replay-quality reinterpretation.

Any follow-up paths are `föreslagen` hypotheses only and are out of scope for this slice.

## Planned audit logic

- load frozen baseline routing trace + replay metrics + manifest
- load frozen Phase C entry rows
- reconstruct raw router targets and decision-time state with the unchanged research-only replay logic
- fail closed unless the frozen replay-root identity matches the expected replay manifest / replay metrics / routing trace hashes already established by prior RI audits
- fail closed on any missing mandatory field, hash mismatch, or unexpected row-identity drift between the frozen entry-row surface and the replay trace surface
- derive all comparator buckets from the same reconstructed frozen candidate table using these exact selectors:
  - raw defensive candidates: `raw target policy = RI_defensive_transition_policy`
  - observed selected-defensive comparator: `selected_policy = RI_defensive_transition_policy`
  - threshold-retained comparator: `selected_policy = RI_continuation_policy` and `switch_reason = confidence_below_threshold`
  - min-dwell-retained comparator: `selected_policy = RI_no_trade_policy` and `switch_reason = switch_blocked_by_min_dwell`
- compute deterministic summary metrics for each bounded comparator bucket, including:
  - count
  - avg/min/max for `ri_clarity_score`, `conf_overall`, `action_edge`, `bars_since_regime_change`
  - `zone` counts
  - `transition_bucket` counts
  - switch-reason counts
  - veto-reason counts
- compute explicit recency-gap summaries, including:
  - selected-defensive max `bars_since_regime_change`
  - threshold-retained min `bars_since_regime_change`
  - min-dwell-retained min `bars_since_regime_change`
  - deterministic gap values between the selected-defensive ceiling and the nearest threshold/min-dwell comparator rows by recency
- emit stable example rows sorted deterministically by:
  - for selected-defensive rows: lowest `bars_since_regime_change`, then highest `action_edge`, then highest `conf_overall`, then lowest `row_index`
  - for comparator rows nearest in recency: lowest `bars_since_regime_change`, then highest `action_edge`, then highest `conf_overall`, then lowest `row_index`
- freeze summary ordering and tie-breakers exactly as emitted in the script; no ad hoc re-ordering is allowed in the report
- leave any `observed fresh-transition recency pocket`, `mixed`, or `overlapping` interpretation to the report only, based on the emitted descriptive metrics

## Boundaries

This slice must:

- remain summary-only, observational-only, and non-authoritative
- treat `results/research/scpe_v1_ri/**` as frozen input only
- use the unchanged replay script only as an analysis reference for row-local reconstruction
- define comparator buckets only as descriptive reference cohorts from the same frozen reconstruction surface; they must not define an alternative acceptance policy or counterfactual routing rule
- emit one deterministic JSON summary under `results/evaluation/`
- emit one deterministic implementation report without volatile fields
- keep any frozen SHA256 identity guards intact; if secret scanning flags those literals, inline allowlisting is acceptable because they are replay-root identity checks rather than credentials
- enforce deterministic outputs: sorted JSON keys, stable bucket ordering, no timestamps, no host/user metadata, and no random inputs

This slice must not:

- modify runtime or canonical replay logic
- alter prior scarcity, threshold-retention, or min-dwell-retention artifacts
- claim policy approval, release approval, or deployment readiness
- reinterpret the replay-quality rule itself
- turn the selected-defensive recency-pocket observation into a recommendation for a new rule

## Expected evidence

- exact comparator counts for raw defensive, selected-defensive, threshold-retained, and min-dwell-retained buckets
- deterministic transition-window summaries for each bounded comparator bucket
- explicit recency-gap evidence showing how near the closest threshold/min-dwell rows get to the selected-defensive recency range
- explicit statement in the report only of whether observed selected-defensive routing appears as an observed fresh-transition recency pocket or a broader overlapping bucket
- explicit statement that the slice describes observed decision-time profiles only and does not recommend a new rule
- frozen input hashes and `read_only_inputs_confirmed = true`

## Gates required

- `pre-commit run --files docs/decisions/scpe_ri_v1_selected_defensive_transition_window_audit_packet_2026-04-20.md docs/analysis/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json`
- explicit smoke run of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py`
- explicit frozen decision-parity / replay-root identity gate: verify SHA256 of the frozen replay manifest, replay metrics, and routing trace before the first run and after the second run; all values must match the expected frozen roots and remain unchanged across both runs
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` (unchanged-surface guardrails only; not direct validation of the new audit logic)
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py` with stable output-hash proof for both the JSON artifact and the report
- explicit proof that `results/research/scpe_v1_ri/**` remains unchanged before vs after both runs
- static import proof that `scripts/analyze/scpe_ri_v1_selected_defensive_transition_window_audit.py` imports no modules from `src/core/**` or `core.*`, reported as a deterministic check result in the implementation report

## Stop conditions

- scope drift beyond the four scoped files
- any write to `results/research/scpe_v1_ri/**`
- any attempt to introduce a new threshold, defensive, or dwell rule
- any wording that turns the audit into runtime advice or promotion evidence

## Done criteria

- the selected-defensive transition-window audit is implemented and documented
- all listed gates pass
- Opus post-audit confirms the slice is still observational-only and governance-safe
