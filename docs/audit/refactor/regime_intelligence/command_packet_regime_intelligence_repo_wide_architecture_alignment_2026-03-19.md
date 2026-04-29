# Command packet — RI repo-wide architecture alignment

Date: 2026-03-19
Branch: `master`
Mode: `STRICT`
Category: `docs`
Risk: `MEDIUM`
Constraints: `NO BEHAVIOR CHANGE`

## Objective

Perform a repo-wide semantic alignment pass so active repository guidance matches the locked architecture decision that Regime Intelligence (RI) is a separate `strategy_family`, not a legacy overlay/toggle/migration patch.

## Scope IN

- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`

## Scope OUT

- `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
- `tests/utils/test_validate_optimizer_config.py`
- `tests/core/strategy/test_families.py`
- `scripts/validate/validate_optimizer_config.py`
- `src/core/strategy/family_registry.py`
- All runtime/backtest/optimizer behavior changes
- `src/core/backtest/*`
- `src/core/optimizer/*`
- `src/core/strategy/decision_*`
- any champion/default/runtime JSON/YAML config values
- any search-space tuning, scores, thresholds, probabilities, or regime logic

## Discovery summary

### A. Must update now

1. `docs/features/feature-regime-intelligence-strategy-family-1.md`
   - still presents historical classifier/storage labels (`legacy_family`, `ri_family`, `invalid_hybrid_overlay`) as if they are the active canonical labels
   - needs alignment to current canonical labels `legacy | ri` and fail-closed hybrid handling

2. `docs/analysis/regime_intelligence/core/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`
   - partially clarified already, but still mixes current-state language with historical stub labels and proposed artifacts
   - needs tighter wording so readers do not infer a third persisted family label or active overlay-compatible path

### B. Historical docs requiring clarification only

1. `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
   - overlay language is historically correct, but can benefit from a small clarification that the finding describes a rejected compatibility probe, not an accepted architecture mode

### C. No change needed unless new evidence appears

1. `handoff.md`
   - already states RI is its own strategy family and warns against reintroducing overlay semantics

2. `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
   - already aligned; keep unchanged in this slice

3. `src/core/strategy/family_registry.py`
   - current canonical labels are already `legacy | ri` and hybrid surfaces fail closed

### D. Ambiguous / review carefully

1. `tests/utils/test_validate_optimizer_config.py`
2. `tests/core/strategy/test_families.py`
3. `scripts/validate/validate_optimizer_config.py`

These files are intentionally left untouched in this slice. If wording-only cleanup is still desired later, it must be handled in a separate, narrower packet because current code/test behavior is already aligned.

## Proposed edit policy

- Prefer clarification over rewrite.
- Preserve historical evidence, but label it explicitly as historical or rejected-path evidence.
- Do not remove references to overlay probes when they are needed to document why that model was rejected.
- If code/test changes are made, they must be message/name-only and behavior-neutral.

## Verification plan

Minimum intended checks after edits:

1. targeted semantic grep audit for `legacy_family|ri_family|invalid_hybrid_overlay` in touched docs
2. `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
3. `python -m pytest tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_pipeline_hash_stability tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_ri_parity_artifact_consistency -q`
4. `python -m pytest tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields -q`

## Stop conditions

- Stop if any candidate edit implies runtime or validator behavior drift.
- Stop if any file under Scope OUT appears necessary.
- Stop if Opus review blocks the scope or requires narrower boundaries.

## Expected outcome

- Active docs describe RI as a separate family using canonical labels.
- Historical overlay evidence remains preserved, but clearly marked as non-canonical/rejected-path evidence.
- No runtime, optimizer, backtest, scoring, or family-classification behavior changes.
