# SCPE RI V1 no-trade release revision packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Required Path: `Full`
Category: `obs`
Constraint: baseline runtime + canonical replay remain unchanged; behavior change candidate is confined to a research-only counterfactual analysis script
Objective: run a bounded semantics-changing research revision test for `RI_no_trade_policy` release timing by simulating a selective early-release exception over the frozen RI evidence surface, without modifying the canonical replay root or any runtime path.
Base SHA: `bda42e70`
Skills used: `python_engineering`

This is a counterfactual replay-only research slice on frozen Phase C rows. It does not change runtime, the canonical replay root `results/research/scpe_v1_ri/`, the baseline replay recommendation `NEEDS_REVISION`, or any deployment/approval status.

This slice is a research-only counterfactual replay probe. The early-release override is row-local, non-propagating, and does not modify runtime logic, canonical replay logic, or release recommendations; it is not a production proposal.

## Commit contract

### Scope IN

- `docs/governance/scpe_ri_v1_no_trade_release_revision_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_no_trade_release_revision_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
- `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`

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
- edits to baseline replay recommendation semantics
- any threshold/config authority change outside the experimental script

### Expected changed files

- packet
- report
- one new experimental analysis script
- one new commit-safe JSON artifact

### Max files touched

- 4

## Revision hypothesis

The bounded hypothesis is that a selective subset of blocked exits from `RI_no_trade_policy` can be released earlier without opening the door to blanket no-trade exit relaxation.

The experimental early-release exception may only trigger when all of the following hold:

1. previous selected policy is `RI_no_trade_policy`
2. the raw target policy is `RI_continuation_policy`
3. the switch would otherwise be blocked only by `min_dwell`, proven by exact baseline blocker identity `switch_reason = switch_blocked_by_min_dwell` with `switch_blocked = true`
4. the row sits inside the frozen successful-release categorical support from `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
5. the row also meets the frozen successful-release median-floor for:
   - `ri_clarity_score`
   - `conf_overall`
   - `action_edge`
6. `bars_since_regime_change` remains inside the frozen successful-release numeric support

This revision is selective and fail-closed by design. It is not a permission surface, not a policy authority surface, and not a runtime proposal by itself.

## Boundaries

This slice is semantics-changing only inside a research-only counterfactual replay performed by a new analysis script. It must not:

- modify the canonical replay root under `results/research/scpe_v1_ri/`
- overwrite baseline artifacts
- alter runtime code or config
- reinterpret baseline `NEEDS_REVISION` as runtime readiness
- claim that support-envelope membership means a row “should have released” in production

The release-probe artifact is used here only as a frozen evidence surface for bounded experimental eligibility, not as runtime authority. The experimental script must record the exact release-probe artifact path and SHA256 in its output.

## Planned method

- load the same frozen Phase C entry rows used by the canonical replay
- load the frozen baseline replay metrics and routing trace for comparison
- load the frozen release-probe artifact to obtain categorical support and numeric median/min/max release envelope
- replay the RI-only router inside the new script with one explicit counterfactual change:
  - evaluate candidate rows against the frozen baseline previous-route context
  - bypass `min_dwell` only for the selective continuation-shaped subset defined above
  - do not propagate revised route state forward beyond the changed row; downstream rows remain anchored to the frozen baseline route context so containment stays a strict subset of baseline-blocked candidates
- keep all other router and veto semantics identical to baseline
- compute revised routing metrics and revised observational metrics in-memory only
- write one commit-safe JSON summary that compares baseline vs revised metrics and counts exactly which baseline-blocked exits were experimentally released

## Gates required

- `pre-commit run --files docs/governance/scpe_ri_v1_no_trade_release_revision_packet_2026-04-20.md docs/governance/scpe_ri_v1_no_trade_release_revision_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_release_revision.py results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`
- explicit smoke run of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_revision.py` with stable output-hash proof
- explicit baseline replay-root immutability proof that `results/research/scpe_v1_ri/**` is unchanged before vs after both runs
- explicit proof that `scripts/analyze/scpe_ri_v1_no_trade_release_revision.py` does not import from `src/core/**`
- explicit containment proof that every route delta is a subset of baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` candidates and that changed rows outside that frozen support subset = `0`

## Stop conditions

- scope drift beyond the four scoped files
- any write to `results/research/scpe_v1_ri/**`
- any attempted edit to runtime code or canonical replay script
- any claim that the experimental result is promotion evidence or deployment approval
- inability to keep the revision selective/fail-closed
- any changed row outside the baseline-blocked `RI_no_trade_policy -> RI_continuation_policy` subset

## Expected evidence

- exact blocked-exit count that meets the selective early-release rule
- exact count of changed rows outside the allowed baseline-blocked subset, expected `0`
- baseline vs revised counts for:
  - `actual_policy_change_count`
  - `blocked_switch_count`
  - `no_trade_rate`
  - `policy_selection_frequency`
  - observational per-policy trade counts
- explicit note that any revised recommendation is counterfactual replay-quality evidence only, not runtime approval
- explicit containment equality proof: `allowed_candidate_count == changed_row_count` and `changed_outside_allowed_count == 0`

## Done criteria

- bounded counterfactual script implemented and documented
- all listed gates pass
- Opus post-audit confirms no scope drift and no hidden runtime/canonical replay impact
