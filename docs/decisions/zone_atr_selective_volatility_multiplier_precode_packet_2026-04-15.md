# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `HIGH` — runtime sizing-path touch in `decision_sizing.py`, explicit behavior-change candidate behind a default-off research seam
- **Required Path:** `Full`
- **Objective:** Add the smallest default-off research seam needed to replay-validate a selective volatility sizing policy: preserve the locked baseline `high_vol_multiplier=0.90`, but lift high-vol sizing to `1.00` only when the runtime current-bar ATR metric `current_atr` is at or above the ex-ante threshold `763.415054`.
- **Candidate:** `current_atr selective high-vol multiplier`
- **Base SHA:** `8e23ddb45d08784e8a8a340f83334f5842505e0e`

## Scope

- **Scope IN:**
  - `docs/decisions/zone_atr_selective_volatility_multiplier_precode_packet_2026-04-15.md`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_decision_sizing.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_current_atr_selective_vol_mult_cfg.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/baseline_decision_rows.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_decision_rows.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/override_decision_rows.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_volatility_multiplier_replay_validation_2026-04-15.md`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - all optimizer/backtest engine internals
  - champion configs / runtime defaults
  - paper/live execution logic
  - fib gating logic
  - non-research volatility sizing redesign
  - docs outside this packet unless strictly required for evidence
- **Expected changed files:**
  - `docs/decisions/zone_atr_selective_volatility_multiplier_precode_packet_2026-04-15.md`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_decision_sizing.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_current_atr_selective_vol_mult_cfg.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/baseline_decision_rows.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_decision_rows.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/override_decision_rows.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_volatility_multiplier_replay_validation_2026-04-15.md`
- **Max files touched:** `13`

## Skill usage

- **Repo-local skill specs to apply:**
  - `.github/skills/python_engineering.json`
  - `.github/skills/config_authority_lifecycle_check.json`
  - `.github/skills/genesis_backtest_verify.json`
- **Why these skills apply:**
  - the slice adds a narrow Python runtime path adjustment with new config-surface leaves
  - the authority/config surface must remain additive, default-safe, and deterministic
  - the acceptance path depends on locked backtest replay against the `0.90` and `1.00` anchors plus decision-row evidence on the canonical CLI route
- **Parity-evidence boundary for this slice:**
  - disabled-path parity claims in this packet are limited to the explicit pytest gates, golden-trace runtime-semantic test, and locked replay commands listed below
  - this packet does not claim broader feature-parity coverage beyond those enumerated evidence surfaces

## Planned behavior

- Add a new default-off research-only config surface under `multi_timeframe` that is explicitly metric-specific to the runtime `current_atr` seam, with leaves limited to:
  - `enabled`
  - `current_atr_threshold`
  - `high_vol_multiplier_override`
- Preserve the current canonical volatility sizing path exactly when the new surface is absent or disabled.
- Bind the enabled-path override only inside the already-existing high-volatility branch in `decision_sizing.py`; do not duplicate or reorder the volatility classification logic.
- Metric contract for this slice:
  - the enabled-path comparison must use the runtime current-bar `current_atr` value already available to `decision_sizing.py`
  - the implementation must not read `zone_debug`, `zone_atr`, `current_atr_used`, or any post-hoc artifact-only field at runtime
  - ex-ante `zone_atr >= 763.415054` is treated only as observational discovery evidence for the replay candidate; the runtime implementation contract is `current_atr >= 763.415054`
- When enabled, replace the current-bar high-vol multiplier with an explicit override value only when all are true:
  - volatility sizing is enabled
  - the current bar is already inside the existing high-vol branch
  - `current_atr` is not `None`
  - `current_atr >= current_atr_threshold`
- Default research target for replay validation:
  - baseline high-vol multiplier: `0.90`
  - selective override high-vol multiplier: `1.00`
  - runtime threshold: `763.415054`
- Do not alter regime thresholds, HTF sizing, risk-map sizing, clarity logic, cooldown logic, or entry admission behavior.

## Evidence basis for this slice

- The completed ex-ante proxy phase found that `zone_atr` / `current_atr_used` was the strongest interpretable entry-time separator in the active uplift population.
- Observational artifact result:
  - `zone_atr >= 763.415054`
  - selected `128 / 383` active uplift positions
  - captured `134.823452` delta PnL vs baseline
  - capture ratio `0.9117` vs always-`1.00`
- Runtime-contract interpretation for this slice:
  - the observational alias is carried forward as the runtime metric candidate `current_atr >= 763.415054`
  - no runtime code in this slice may branch on `zone_atr`; that name belongs only to the discovery artifact
- This slice exists to replay-validate that observational candidate against the locked anchors:
  - always-`0.90`
  - always-`1.00`

## Gates required

- `pre-commit run --files src/core/strategy/decision_sizing.py src/core/config/schema.py src/core/config/authority.py tests/utils/test_decision_sizing.py tests/utils/test_decision_scenario_behavior.py tests/governance/test_config_schema_backcompat.py tests/integration/test_golden_trace_runtime_semantics.py docs/decisions/zone_atr_selective_volatility_multiplier_precode_packet_2026-04-15.md`
- `python -m pytest tests/utils/test_decision_sizing.py tests/utils/test_decision_scenario_behavior.py tests/governance/test_config_schema_backcompat.py tests/integration/test_golden_trace_runtime_semantics.py`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- canonical parity proof that behavior is unchanged when the new config surface is absent and when it is explicitly disabled
- locked-window replay comparison commands:
  - always-`0.90`:
    - `python scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json --fast-window --precompute-features --decision-rows-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/baseline_decision_rows.json --no-save`
  - selective `current_atr >= 763.415054`:
    - `python scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_current_atr_selective_vol_mult_cfg.json --fast-window --precompute-features --decision-rows-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_decision_rows.json --no-save`
  - always-`1.00`:
    - `python scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_100_vol_thr_75_cfg.json --fast-window --precompute-features --decision-rows-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/override_decision_rows.json --no-save`

## Stop Conditions

- scope drift outside listed files
- any behavior drift when the new surface is absent or disabled
- need to modify entry gating or runtime defaults to make the slice work
- determinism/hash regression
- evidence that the selective seam changes more than the intended high-vol multiplier route

## Output required

- **Implementation Report** — delivered in chat / PR evidence, not as a committed repo file
- **Replay validation note:** `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_volatility_multiplier_replay_validation_2026-04-15.md`

## Evidence wording discipline

- Enabled-path results are research efficacy evidence only.
- No enabled-path result may be cited as default parity, causal proof, or deployment readiness.
- The selective policy remains a research candidate until replay evidence is compared explicitly against both locked anchors.

## Governance and evidence addendum

- **Pre-code governance status:** `APPROVED_WITH_NOTES`
  - binding verification note carried into implementation: prove `surface absent == enabled:false` explicitly on the disabled path
- **Repo-local skill coverage actually applied:**
  - `.github/skills/python_engineering.json`
  - `.github/skills/config_authority_lifecycle_check.json`
  - `.github/skills/genesis_backtest_verify.json`
- **Direct current_atr-only runtime proof points:**
  - `src/core/strategy/decision_sizing.py::_apply_current_atr_selective_high_vol_multiplier`
    - reads only `multi_timeframe.research_current_atr_high_vol_multiplier_override`
    - compares only runtime `current_atr` against `current_atr_threshold`
    - does not branch on `zone_atr`, `zone_debug`, or `current_atr_used`
  - `src/core/config/schema.py::ResearchCurrentATRHighVolMultiplierOverrideConfig`
    - constrains the additive research surface to `enabled`, `current_atr_threshold`, and `high_vol_multiplier_override`
  - `src/core/config/schema.py::MultiTimeframeConfig`
    - mounts the new surface under `research_current_atr_high_vol_multiplier_override`
  - `src/core/config/authority.py`
    - multi-timeframe whitelist admits only the new surface name and only the three approved leaves
- **Direct disabled-path parity proof points:**
  - `tests/utils/test_decision_sizing.py::test_apply_sizing_current_atr_selective_override_absent_matches_explicit_disabled`
  - `tests/integration/test_golden_trace_runtime_semantics.py::test_current_atr_selective_high_vol_multiplier_absent_matches_enabled_false`
  - `tests/governance/test_config_schema_backcompat.py::test_validate_current_atr_selective_override_absent_matches_explicit_false_leaf`
