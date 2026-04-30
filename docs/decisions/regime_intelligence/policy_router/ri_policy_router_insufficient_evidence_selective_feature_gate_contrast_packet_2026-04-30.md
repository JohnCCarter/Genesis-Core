# RI policy router insufficient-evidence selective feature-gate contrast packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / read-only selective contrast / no behavior change`

Relevant skills: `decision_gate_debug`, `python_engineering`

Active repository skill for this slice: `python_engineering.json`, covering the read-only
analysis script, any focused pure-helper test, and the associated evidence-note updates.

Skill coverage for this slice is explicit and bounded:

- `decision_gate_debug` governs the gate-oriented reading and mechanism separation between the already-fixed March 2021 negative-year cluster and the already-fixed March 2025 positive-year control.
- `python_engineering` governs the typed helper structure, focused unit test coverage for any new pure logic, and the minimal-diff validation path.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads existing action-diff JSONs plus curated candles only, emits one bounded JSON artifact plus one analysis note, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the March 2021 negative-year window and March 2025 positive-year control are already frozen, so the next honest move is one exact feature/gate contrast on those same rows rather than fresh annual aggregation or runtime speculation.
- **Objective:** compare the already-fixed March 2021 negative-year `insufficient_evidence` target cluster against the already-fixed March 2025 positive-year `insufficient_evidence` target cluster on the smallest available feature/gate surface, so the selective-discriminator question becomes more concrete.
- **Candidate:** `fixed March 2021 vs March 2025 insufficient_evidence feature-gate contrast`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`

## Exact proposed subject

### Fixed target clusters already locked by prior slices

Negative-year March 2021 target cluster:

- `2021-03-26T12:00:00+00:00`
- `2021-03-27T06:00:00+00:00`
- `2021-03-27T15:00:00+00:00`
- `2021-03-28T00:00:00+00:00`

Positive-year March 2025 target cluster:

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

### Allowed comparison surface

This slice is fail-closed to two pre-fixed `insufficient_evidence` target cohorts only: the
exact March 2021 target timestamps and the exact March 2025 target timestamps already
identified in the existing enabled-vs-absent action-diff JSON artifacts. No representative-
comparison-row reselection, nearest-neighbor expansion, threshold sweep, year-wide mining, or
runtime-semantics inference is in scope.

The helper may read only the existing action-diff rows and their existing router-debug payloads from:

- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2021_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

The helper may summarize only repo-visible, already-materialized fields such as:

- `bars_since_regime_change`
- `action_edge`
- `confidence_gate`
- `clarity_raw`
- `clarity_score`
- `confidence_level`
- `mandate_level`
- `dwell_duration`
- `regime`
- `selected_policy`
- `raw_target_policy`
- `previous_policy`
- `switch_reason`
- `switch_proposed`
- `switch_blocked`
- `size_multiplier`
- observational candle proxies already used in the fixed-window notes (`fwd_4`, `fwd_8`, `fwd_16`, `mfe_16`, `mae_16`)

The helper may derive simple descriptive deltas such as:

- 2021-target mean minus 2025-target mean
- threshold shortfall / surplus relative to the embedded `router_params` floor values if those params are present in the row payload
- cohort-level min/max/median summaries

### Exact output paths to materialize

- JSON artifact: `results/evaluation/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.md`

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_packet_2026-04-30.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_20260430.py`
  - `tests/backtest/test_ri_policy_router_insufficient_evidence_selective_feature_gate_contrast.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.md`
  - optional refresh of `GENESIS_WORKING_CONTRACT.md` only if the new contrast materially sharpens the next admissible step
- **Scope OUT:**
  - no runtime/config/schema/authority/default changes
  - no new backtest reruns
  - no widening to all positive or all negative years
  - no representative-comparison-row mining, stronger-row benchmarking, or alternate cohort discovery
  - no edits to the completed March 2021 helper or March 2025 wrapper unless strictly required to resolve import/runtime issues in the new contrast helper; if that becomes necessary, stop and re-review rather than widening silently
  - no promotion/readiness/champion claims
- **Expected changed files:** 5-6
- **Max files touched:** 6

## Evidence anchors

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2021_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

## Planned method

1. load the exact already-fixed 2021 and 2025 target rows only
2. normalize one bounded descriptive signature per row from existing `enabled.router_debug` fields plus the same candle-side observational proxies already used in the earlier notes
3. summarize cohort-level differences between the 2021 target cluster and the 2025 target cluster, keeping all conclusions descriptive and non-authoritative
4. record whether the first selective contrast points more toward regime-age / edge-strength / confidence-floor distance / clarity shape, or whether the two windows remain too similar to support a concrete discriminator yet

This slice is observational and non-authoritative. It does not propose runtime threshold
changes, policy swaps, family/champion changes, promotion decisions, or readiness claims; if
`GENESIS_WORKING_CONTRACT.md` is refreshed, the update may only sharpen the next admissible
evidence step.

## Validation requirements

- `get_errors` on the new packet/script/test/note and any touched contract file
- exact helper execution against the fixed 2021 and 2025 target clusters
- deterministic repeat-run proof with stable identical JSON output
- artifact row-lock/signature check proving the emitted target timestamps match the previously fixed windows exactly and that the required router-debug fields exist on every target row
- focused unit tests for new pure helper logic only if such logic is introduced
- `ruff check` on the new Python files
- `pre-commit run --files` on the touched files
- determinism replay, feature-cache invariance, and pipeline-invariant selector outcomes recorded for this non-trivial slice
- explicit ignored/staging check on the new `results/evaluation` artifact
- manual diff review confirming no runtime/config/default/authority drift

Done criteria for this slice:

- the script produces one deterministic JSON artifact from the fixed inputs only
- a repeat run confirms stable output ordering/content
- missing or duplicate target rows, missing required fields, unstable artifact output, or widened selector logic are FAIL
- runtime/config/default/authority surfaces remain untouched

Artifact packaging note:

- the generated JSON artifact is reproducible local evidence for this slice and was verified by identical
  SHA256 across two runs: `A107B62D0CAE4E360F9DFE067BDB3637C73DB60209F812137D37E134E29144CE`
- new `results/evaluation` artifacts remain ignored in the current repo state, so this JSON may remain
  untracked unless the repo's artifact-visibility policy is changed explicitly

## Stop conditions

- the helper starts depending on runtime imports from `src/**`
- the feature/gate contrast requires widening into fresh annual sweeps or extra local windows to say anything at all
- the row payloads do not expose enough stable fields to compare the fixed windows honestly
- the note starts implying runtime tuning or promotion authority
- scope drifts into editing the already-completed March 2021 or March 2025 slice files instead of adding one bounded contrast layer

## Output required

- one deterministic JSON summary artifact for the fixed 2021-vs-2025 target contrast
- one human-readable analysis note stating what the contrast does and does not justify for the robust-policy question
- exact command run and validation outcomes
