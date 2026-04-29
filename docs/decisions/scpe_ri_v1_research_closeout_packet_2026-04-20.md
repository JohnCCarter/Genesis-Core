# SCPE RI V1 research closeout packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Required Path: `Full`
Category: `obs`
Constraint: baseline runtime + canonical replay remain unchanged; behavior change candidate is confined to a research-only counterfactual analysis script; closeout remains synthesis-only and non-authoritative
Objective: complete the current bounded SCPE RI V1 research roadmap by running one final tighter no-trade release-timing counterfactual over the frozen replay evidence surface and then writing a closeout report that explicitly states what the research lane resolved, what remains out of scope, and what conditions would gate any eventual runtime/integration roadmap.
Base SHA: `140911b0`
Skills used: `python_engineering`

This packet closes the current research lane; it does not authorize runtime integration, backtest execution integration, or any change to the canonical replay root `results/research/scpe_v1_ri/`.

This slice is still research-only. The counterfactual rule is row-local, non-propagating, and non-authoritative. The closeout document is a synthesis artifact only; it must not re-label the replay as runtime-ready or claim promotion approval.

## Commit contract

### Scope IN

- `docs/decisions/scpe_ri_v1_research_closeout_packet_2026-04-20.md`
- `docs/analysis/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md`
- `docs/decisions/scpe_ri_v1_research_closeout_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`
- `results/evaluation/scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `tmp/**`
- `results/research/**`
- `docs/scpe_ri_v1_architecture.md`
- `docs/analysis/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md`
- `docs/analysis/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
- runtime integration
- canonical replay regeneration
- edits to `scripts/analyze/scpe_ri_v1_router_replay.py`
- edits to prior audit/revision script logic
- edits to baseline replay recommendation semantics
- any threshold/config/runtime authority change outside the experimental script

### Expected changed files

- one packet
- one new experimental analysis script
- one new commit-safe JSON artifact
- one revision report
- one research closeout report

### Max files touched

- 5

## Revision hypothesis

The final bounded hypothesis is that the first no-trade release revision can be tightened enough to preserve a meaningful subset of continuation-shaped releases while staying inside the replay-quality churn ceiling.

The experimental early-release exception may only trigger when all of the following hold:

1. previous selected policy is `RI_no_trade_policy`
2. the raw target policy is `RI_continuation_policy`
3. the switch would otherwise be blocked only by `min_dwell`, proven by exact baseline blocker identity `switch_reason = switch_blocked_by_min_dwell` with `switch_blocked = true`
4. the row remains inside the frozen successful-release categorical support from `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
5. the row remains inside the frozen successful-release numeric support and clears the frozen median-floor for:
   - `ri_clarity_score`
   - `conf_overall`
   - `action_edge`
6. the row is `zone = mid`
7. the row is no longer at the freshest edge of the stable support and must satisfy `bars_since_regime_change >= 92.0`

Pre-packet read-only evidence over the frozen baseline showed that this stricter rule selects exactly `7` rows and yields:

- `actual_policy_change_count = 35`
- `actual_policy_change_rate = 0.241379`
- `blocked_switch_count_delta = -7`
- `no_trade_rate_delta = -0.047945`
- `continuation_trade_count_delta = +7`

This packet treats those values as scouting evidence only until the tracked script reproduces them deterministically.

## Boundaries

This slice is semantics-changing only inside a research-only counterfactual replay performed by a new analysis script. It must not:

- modify the canonical replay root under `results/research/scpe_v1_ri/`
- overwrite baseline artifacts
- alter runtime code or config
- reinterpret baseline `NEEDS_REVISION` as runtime readiness
- claim that this tighter subset is a production permission surface
- claim that the closeout document itself approves runtime/integration work

The closeout report may enumerate bounded prerequisites and decision inputs for any future proposal to define a runtime/integration roadmap. It does not open, approve, authorize, or inherit such a roadmap, and it grants no runtime, backtest, config, or deployment approval.

## Planned method

- load the same frozen Phase C entry rows used by the canonical replay
- load the frozen baseline replay metrics and routing trace for comparison
- load the frozen release-probe artifact to obtain categorical support and numeric median/min/max release envelope
- evaluate candidate rows against the frozen baseline previous-route context only
- apply the tighter v2 subset rule defined above
- do not propagate revised route state forward beyond the changed row; downstream rows remain anchored to the frozen baseline route context so containment stays a strict subset of baseline-blocked candidates
- keep all other router and veto semantics identical to baseline
- compute revised routing metrics and revised observational metrics in-memory only
- write one commit-safe JSON summary with exact changed rows and baseline-vs-revised deltas
- write one report for the v2 revision and one lane-level closeout report that cites the full research evidence surface and explicitly separates:
  - what the current research roadmap resolved
  - what remains unresolved but bounded
  - what is out of scope and requires a new runtime/integration roadmap

## Gates required

- `pre-commit run --files docs/decisions/scpe_ri_v1_research_closeout_packet_2026-04-20.md docs/analysis/scpe_ri_v1_no_trade_release_revision_v2_report_2026-04-20.md docs/decisions/scpe_ri_v1_research_closeout_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py results/evaluation/scpe_ri_v1_no_trade_release_revision_v2_2026-04-20.json`
- explicit smoke run of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py` with stable output-hash proof, explicitly treated as the determinism gate for this scoped research artifact lane rather than as runtime decision parity
- explicit baseline replay-root immutability proof that `results/research/scpe_v1_ri/**` is unchanged before vs after both runs
- explicit proof that `scripts/analyze/scpe_ri_v1_no_trade_release_revision_v2.py` does not import from `src/core/**` or `scripts.analyze.scpe_ri_v1_router_replay`
- explicit containment proof that every route delta is a subset of baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` candidates and that changed rows outside that frozen support subset = `0`

## Stop conditions

- scope drift beyond the five scoped files
- any write to `results/research/scpe_v1_ri/**`
- any attempted edit to runtime code or canonical replay script
- any claim that the experimental result is promotion evidence or deployment approval
- inability to keep the revision selective/fail-closed
- any changed row outside the baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` subset
- closeout wording that blurs the line between research closure and runtime approval

## Expected evidence

- exact changed-row count for the tighter v2 rule, expected `7`
- exact count of changed rows outside the allowed baseline-blocked subset, expected `0`
- baseline vs revised counts for:
  - `actual_policy_change_count`
  - `actual_policy_change_rate`
  - `blocked_switch_count`
  - `no_trade_rate`
  - `policy_selection_frequency`
  - observational per-policy trade counts
- explicit note that any revised recommendation remains counterfactual replay-quality evidence only, not runtime approval
- explicit lane closeout statement covering:
  - replay-root recommendation status
  - why the current research lane is considered complete
  - what a future runtime/integration roadmap must treat as entry prerequisites instead of inherited approval

## Done criteria

- bounded v2 counterfactual script implemented and documented
- all listed gates pass
- closeout report written with clear research-vs-runtime boundary language
- Opus post-audit confirms no scope drift and no hidden runtime/canonical replay impact
