# RI advisory environment-fit Phase 3 partial baseline packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded deterministic partial baseline / results-only / default unchanged`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded research-only deterministic scoring on already captured RI evidence with outputs confined to `results/**`; no runtime/default/authority changes.
- **Required Path:** `Full`
- **Objective:** test whether a narrow deterministic partial baseline built from clarity/recency/reliability signals separates the Phase 2 outcome/state taxonomy more honestly than the current implicit picture.
- **Candidate:** `RI advisory environment-fit Phase 3 partial baseline`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`

### Scope

- **Scope IN:**
  - `docs/governance/ri_advisory_environment_fit_phase3_partial_baseline_packet_2026-04-17.md`
  - one bounded research script under `tmp/`
  - one results directory under `results/research/ri_advisory_environment_fit/`
  - one deterministic evaluation memo under `docs/analysis/`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - runtime authority changes
  - default behavior changes
  - ML/model work
  - full RI role-map claims
  - direct `market_fit_score` promotion claims
- **Expected changed files:**
  - this packet
  - one `tmp/` script
  - one `docs/analysis/` memo
  - results artifacts confined to one new result subdirectory
- **Max files touched:** `8`

### Fixed evidence source

- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- Phase 2 taxonomy SSOT:
  - `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`

### Allowed score outputs

This slice may define only:

1. `decision_reliability_score`
2. proxy `transition_risk_score`

These outputs must be deterministic, interpretable, and derived only from pre-entry fields already admissible under Phase 2.
Admissibility in this slice is limited to a bounded partial baseline that emits only `decision_reliability_score` and a proxy `transition_risk_score`, both derived solely from Phase 2-admissible pre-entry fields.
Capture v2 does **not** admit use of `shadow_regime_*`, `authoritative_regime`, or `ri_risk_state_*` as evidentiary inputs for this slice, and `market_fit_score` remains deferred pending a separate admissibility review.

### Explicitly deferred output

This slice does **not** authorize a full `market_fit_score`.

Reason:

- the current evidence surface still lacks realized-entry disagreement variation and non-flat transition-multiplier surfaces
- claiming a full market-role map now would overstate the available evidence

### Allowed scoring-time inputs

- `ri_clarity_score`
- `ri_clarity_raw`
- `bars_since_regime_change`
- probability / confidence context already captured pre-entry
- bounded sizing/context descriptors already captured pre-entry

### Explicit allowlist

Implementation must emit a selector-audit artifact showing the exact consumed columns.
That allowlist may contain only:

- `ri_clarity_score`
- `ri_clarity_raw`
- `bars_since_regime_change`
- `proba_buy`
- `proba_sell`
- `proba_edge`
- `conf_buy`
- `conf_sell`
- `conf_overall`
- `decision_size`
- `current_atr_used`
- `atr_period_used`
- `action`
- `side`
- `htf_regime`
- `zone`

### Forbidden scoring-time inputs

- any post-entry outcome field
- any Phase 2 outcome label used as a score input
- any `shadow_regime_*` field
- `authoritative_regime`
- `authority_mode`
- `authority_mode_source`
- any `ri_risk_state_*` field
- any injected disagreement branch when disagreement coverage is zero
- any fabricated transition-multiplier branch when that field is absent
- any cross-family logic
- any aggregation to `market_fit_score`

### Required evaluation outputs

- bounded bucket tables versus:
  - `supportive_context_outcome`
  - `hostile_context_outcome`
  - `ambiguous_state`
  - `transition_risk_state`
- explicit `2025` contradiction-year reporting
- explicit zero-coverage note for disagreement-state handling on this surface
- one selector-audit artifact showing exact consumed input columns
- one label-surface audit stating whether the exact Phase 2 supportive / hostile label contract is materially joinable on the capture-v2 rows
- failure taxonomy coverage:
  - false-supportive
  - false-hostile
  - transition miss
  - disagreement miss / zero-coverage
  - contradiction-year inversion

If the exact Phase 2 supportive / hostile label surface is **not** materially joinable, the slice must stop and emit a label-gap memo or explicitly bounded provisional-evaluation review.
It must not silently substitute raw `total_pnl` sign for the Phase 2 label contract.

### Gates required

- `pre-commit run --files <packet> <tmp script> <analysis memo>`
- `pytest tests/backtest/test_runner_direct_includes_merged_config.py`
- `pytest tests/backtest/test_backtest_engine.py::test_engine_run_skip_champion_merge_does_not_load_champion`
- `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- bounded execution of the partial-baseline script itself
- parity checks proving:
  - capture-v2 `unmatched_positions == 0`
  - capture-v2 evidence bundle hash unchanged
  - capture-v2 containment verdict remains `PASS`
  - all writes remain inside approved `tmp/`, `results/`, and docs surfaces

### Stop Conditions

- any attempt to move logic into runtime code
- any need to mutate capture-v2 evidence rows or upstream artifacts
- capture-v2 `unmatched_positions != 0`
- evidence-bundle hash drift
- capture-v2 containment verdict not equal to `PASS`
- any output write outside approved `tmp/`, `results/`, or docs surfaces
- any touch to `src/**`, `tests/**`, `config/**`, or runtime defaults/config semantics
- inability to materialize the exact Phase 2 supportive / hostile label surface, unless the slice stops and records that gap explicitly
- any substitution of raw `total_pnl` sign for the Phase 2 supportive / hostile contract without separate admissibility approval
- any claim that the baseline covers disagreement-state logic despite zero coverage
- any attempt to synthesize transition-multiplier branches not present in the evidence
- any post-entry leakage into score inputs
- any result that only looks useful in `2024` and inverts in `2025` without being reported plainly

### Output required

- one bounded `tmp/` partial-baseline script
- one results directory with deterministic score/evaluation artifacts
- one selector-audit artifact recording the exact consumed input columns
- one label-surface audit artifact, or a label-gap memo if the exact Phase 2 supportive / hostile contract is not materially joinable
- one analysis memo stating whether the partial baseline is useful enough to justify continued Phase 4 shadow evaluation

## Bottom line

This packet proposes one narrow next step only:

- do not force a full RI role-map baseline
- do test whether clarity/recency/reliability already support a useful deterministic partial baseline on the newly admissible evidence surface

This packet does **not** authorize full RI role-map claims, promotion framing, or runtime-shadow escalation without a later separate review.

If that partial baseline fails honestly, the lane should record that instead of inflating scope.
