# Regime Intelligence Plateau Evidence — Slice7 to Slice10

## Plateau conclusion

Slice7–Slice10 establish a deterministic and reproducible plateau within the current RI exit/override search space.

The search surface is constrained to a small discrete grid while core signal, regime, and gating layers remain fixed.

Observed invariance in validation outcomes indicates that this local parameter surface is exhausted.

No further edge is observed within this constrained surface, suggesting that additional gains require changes to the underlying signal inputs, regime modeling, or decision structure rather than continued local optimization.

This document records plateau and search-surface observations only and does not authorize launch, comparison, promotion, or implementation.

## 1) Slice7–Slice10 outcome table

| Slice   | Run path                                          | Best-train trial | Best-train params (core top-level keys)                                                                                                                                                                                        | Validation artifact(s)                                    |      Validation score |        Profit factor |                 Max DD | Trades |                Sharpe |      Duplicate ratio | Total trials |
| ------- | ------------------------------------------------- | ---------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- | --------------------: | -------------------: | ---------------------: | -----: | --------------------: | -------------------: | -----------: |
| Slice7  | `results/hparam_search/run_20260324_171511`       |      `trial_007` | `thresholds.entry_conf_overall=0.28; thresholds.regime_proba.balanced=0.36; gates.hysteresis_steps=4; gates.cooldown_bars=1; exit.max_hold_bars=8; exit.exit_conf_threshold=0.42; multi_timeframe.ltf_override_threshold=0.40` | `validation/trial_001.json`                               | `0.26974911658712664` | `1.8845797002042906` | `0.027808774550017137` |   `63` | `0.20047738907046656` |            `0.90625` |         `96` |
| Slice8  | `results/hparam_search/ri_slice8_launch_20260326` |      `trial_005` | `thresholds.entry_conf_overall=0.27; thresholds.regime_proba.balanced=0.36; gates.hysteresis_steps=4; gates.cooldown_bars=1; exit.max_hold_bars=8; exit.exit_conf_threshold=0.42; multi_timeframe.ltf_override_threshold=0.40` | `validation/trial_001.json`                               | `0.26974911658712664` | `1.8845797002042906` | `0.027808774550017137` |   `63` | `0.20047738907046656` | `0.2604166666666667` |         `96` |
| Slice9  | `results/hparam_search/run_20260326_090908`       |      `trial_002` | `thresholds.entry_conf_overall=0.27; thresholds.regime_proba.balanced=0.36; gates.hysteresis_steps=4; gates.cooldown_bars=1; exit.max_hold_bars=8; exit.exit_conf_threshold=0.40; multi_timeframe.ltf_override_threshold=0.38` | `validation/trial_001.json`                               | `0.26974911658712664` | `1.8845797002042906` | `0.027808774550017137` |   `63` | `0.20047738907046656` | `0.3466666666666667` |         `75` |
| Slice10 | `results/hparam_search/run_20260327_080025`       |      `trial_002` | `thresholds.entry_conf_overall=0.27; thresholds.regime_proba.balanced=0.36; gates.hysteresis_steps=4; gates.cooldown_bars=1; exit.max_hold_bars=8; exit.exit_conf_threshold=0.40; multi_timeframe.ltf_override_threshold=0.38` | `validation/trial_001.json` … `validation/trial_005.json` | `0.26974911658712664` | `1.8845797002042906` | `0.027808774550017137` |   `63` | `0.20047738907046656` | `0.3466666666666667` |         `75` |

## 2) Exact Optuna search space (slice10)

### Subject

- Config: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`
- Declared family: `strategy_family: ri`
- Run intent: `meta.runs.run_intent: research_slice`
- Score version: `meta.runs.score_version: v2`
- Validation window: `2024-07-01` … `2024-12-31`
- Training window: `2023-12-21` … `2024-06-30`

### Tunable parameters

| Parameter                                | Type    | Exact values                     |
| ---------------------------------------- | ------- | -------------------------------- |
| `exit.max_hold_bars`                     | `int`   | `{7, 8, 9}`                      |
| `exit.exit_conf_threshold`               | `float` | `{0.40, 0.41, 0.42, 0.43, 0.44}` |
| `multi_timeframe.ltf_override_threshold` | `float` | `{0.38, 0.39, 0.40, 0.41, 0.42}` |

- Exact grid cardinality: `3 × 5 × 5 = 75`

### Fixed parameters

#### Family / authority / identity

- `thresholds.min_edge = 0.01`
- `thresholds.regime_proba.bull = 0.5`
- `thresholds.regime_proba.bear = 0.5`
- `thresholds.regime_proba.ranging = 0.5`
- `thresholds.signal_adaptation.atr_period = 14`
- `multi_timeframe.regime_intelligence.enabled = true`
- `multi_timeframe.regime_intelligence.version = "v2"`
- `multi_timeframe.regime_intelligence.authority_mode = "regime_module"`
- `multi_timeframe.regime_intelligence.clarity_score.enabled = false`
- `multi_timeframe.regime_intelligence.risk_state.enabled = true`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.enabled = true`

#### Entry threshold surface

- `thresholds.entry_conf_overall = 0.27`
- `thresholds.regime_proba.balanced = 0.36`
- `thresholds.signal_adaptation.zones.low.entry_conf_overall = 0.14`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall = 0.42`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall = 0.34`
- `thresholds.signal_adaptation.zones.low.regime_proba = 0.32`
- `thresholds.signal_adaptation.zones.mid.regime_proba = 0.52`
- `thresholds.signal_adaptation.zones.high.regime_proba = 0.58`

#### Exit / management surface

- `htf_exit_config.partial_1_pct = 0.5`
- `htf_exit_config.partial_2_pct = 0.45`
- `htf_exit_config.fib_threshold_atr = 0.9`
- `htf_exit_config.trail_atr_multiplier = 2.5`
- `exit.trailing_stop_pct = 0.022`
- `exit.stop_loss_pct = 0.016`

#### HTF / LTF fib entry surface

- `htf_fib.entry.tolerance_atr = 4.0`
- `htf_fib.entry.long_max_level = 0.236`
- `htf_fib.entry.short_min_level = 0.35`
- `ltf_fib.entry.tolerance_atr = 1.5`
- `ltf_fib.entry.long_max_level = 0.146`
- `ltf_fib.entry.short_min_level = 0.236`

#### Risk-state / sizing surface

- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold = 0.04`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult = 1.0`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult = 0.65`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold = 0.06`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult = 0.65`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars = 2`
- `risk.htf_regime_size_multipliers.bear = 0.65`
- `risk.volatility_sizing.high_vol_multiplier = 0.70`

#### Gating surface

- `gates.hysteresis_steps = 4`
- `gates.cooldown_bars = 1`

### Registry / admission constraints

#### Canonical RI family registry cluster (`src/core/strategy/family_registry.py`)

- Required authority mode: `multi_timeframe.regime_intelligence.authority_mode = regime_module`
- Required ATR period: `thresholds.signal_adaptation.atr_period = 14`
- Required gates: `gates.hysteresis_steps = 3`
- Required gates: `gates.cooldown_bars = 2`
- Required canonical threshold cluster:
  - `thresholds.entry_conf_overall = 0.25`
  - `thresholds.regime_proba.balanced = 0.36`
  - `thresholds.signal_adaptation.zones.low.entry_conf_overall = 0.16`
  - `thresholds.signal_adaptation.zones.low.regime_proba = 0.33`
  - `thresholds.signal_adaptation.zones.mid.entry_conf_overall = 0.40`
  - `thresholds.signal_adaptation.zones.mid.regime_proba = 0.51`
  - `thresholds.signal_adaptation.zones.high.entry_conf_overall = 0.32`
  - `thresholds.signal_adaptation.zones.high.regime_proba = 0.57`

#### Optimizer admission (`src/core/strategy/family_admission.py`)

- Exact RI optimizer identity requires:
  - declared `strategy_family = ri`
  - exact `multi_timeframe.regime_intelligence.authority_mode = regime_module`
- `run_intent = research_slice` admits RI-family optimizer surfaces without requiring the canonical RI cluster
- Non-`research_slice` RI admissions require canonical RI cluster matching

## 3) RI signal surface

### Features used

#### Base feature keys (`src/core/strategy/features_asof_parts/base_feature_utils.py`)

- `rsi_inv_lag1`
- `volatility_shift_ma3`
- `bb_position_inv_ma3`
- `rsi_vol_interaction`
- `vol_regime`
- `atr_14`

#### Fibonacci feature keys (`src/core/strategy/features_asof_parts/fibonacci_feature_utils.py`)

- `fib_dist_min_atr`
- `fib_dist_signed_atr`
- `fib_prox_score`
- `fib0618_prox_atr`
- `fib05_prox_atr`
- `swing_retrace_depth`
- `fib05_x_ema_slope`
- `fib_prox_x_adx`
- `fib05_x_rsi_inv`

#### Downstream decision context assembled in `evaluate.py`

- `atr_percentiles`
- `htf_fibonacci`
- `ltf_fibonacci`
- `current_atr`
- `last_close`
- `htf_regime`
- `spread_bp`
- `volume_score`
- `data_quality`

#### Probability model call surface (`evaluate.py`)

- `predict_proba_for(symbol, timeframe, feats, regime=current_regime)`

### Regime definition

- Authoritative regime path:
  - if `authority_mode == regime_module` → `detect_regime_from_candles(...)` → `normalize_authoritative_regime(...)`
  - else → legacy unified regime path
- Slice10 declared authority mode:
  - `multi_timeframe.regime_intelligence.authority_mode = "regime_module"`
- RI registry identity markers:
  - `strategy_family = ri`
  - `thresholds.signal_adaptation.atr_period = 14`
  - RI threshold cluster
  - RI gate tuple
- HTF regime path:
  - `compute_htf_regime(htf_fib_data, current_price=last_close)`
- Risk-state path:
  - `compute_risk_state_multiplier(cfg, equity_drawdown_pct, bars_since_regime_change)`

### Entry logic

- Candidate selection inputs:
  - `p_buy`
  - `p_sell`
  - `regime`
  - `risk_ctx`
  - `thresholds.*`
  - `gates.*`
- EV gate:
  - `ev_long = p_buy * R_default - p_sell`
  - `ev_short = p_sell * R_default - p_buy`
  - require `max(ev_long, ev_short) > 0`
- Hard blocks:
  - `risk_ctx.event_block`
  - `risk_ctx.risk_cap_breached`
- Threshold root:
  - `thresholds.entry_conf_overall`
- ATR-adaptive zone selection:
  - `thresholds.signal_adaptation.atr_period`
  - `atr_percentiles[p40, p80]`
  - zones: `low`, `mid`, `high`
- Zone-adaptive threshold surface:
  - `thresholds.signal_adaptation.zones.<zone>.entry_conf_overall`
  - `thresholds.signal_adaptation.zones.<zone>.regime_proba`
- Regime probability threshold surface:
  - `thresholds.regime_proba.<regime>`
- Candidate pass conditions:
  - `p_buy >= threshold`
  - `p_sell >= threshold`
- Confidence gate:
  - candidate-side confidence must be `>= conf_thr`
- Edge gate:
  - `thresholds.min_edge`

### Exit logic

#### Slice10 explicit exit-control surface

- `exit.max_hold_bars ∈ {7, 8, 9}`
- `exit.exit_conf_threshold ∈ {0.40, 0.41, 0.42, 0.43, 0.44}`
- `exit.stop_loss_pct = 0.016`
- `exit.trailing_stop_pct = 0.022`
- `htf_exit_config.partial_1_pct = 0.5`
- `htf_exit_config.partial_2_pct = 0.45`
- `htf_exit_config.fib_threshold_atr = 0.9`
- `htf_exit_config.trail_atr_multiplier = 2.5`

### Gating logic

#### Decision gates (`src/core/strategy/decision_gates.py`)

- Hysteresis gate:
  - `gates.hysteresis_steps`
  - switch candidate only after `decision_steps >= hysteresis_steps`
- Cooldown gate:
  - `gates.cooldown_bars`
  - block while `cooldown_remaining > 0`
- Confidence gate:
  - `CONF_TOO_LOW`
- Edge gate:
  - `EDGE_TOO_SMALL`
- Event/risk gates:
  - `R_EVENT_BLOCK`
  - `RISK_CAP`

#### Fib gating (`src/core/strategy/decision_fib_gating.py`)

- HTF fib gate runs before LTF fib gate
- LTF fib override context is prepared before HTF gate
- Slice10 fib gate surface:
  - `htf_fib.entry.tolerance_atr = 4.0`
  - `htf_fib.entry.long_max_level = 0.236`
  - `htf_fib.entry.short_min_level = 0.35`
  - `ltf_fib.entry.tolerance_atr = 1.5`
  - `ltf_fib.entry.long_max_level = 0.146`
  - `ltf_fib.entry.short_min_level = 0.236`
  - `multi_timeframe.ltf_override_threshold ∈ {0.38, 0.39, 0.40, 0.41, 0.42}`

#### RI transition / sizing guards (`src/core/strategy/decision_sizing.py`)

- `multi_timeframe.regime_intelligence.risk_state.enabled = true`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.enabled = true`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult = 0.65`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars = 2`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold = 0.04`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult = 1.0`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold = 0.06`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult = 0.65`
- `risk.htf_regime_size_multipliers.bear = 0.65`
- `risk.volatility_sizing.high_vol_multiplier = 0.70`
- `multi_timeframe.regime_intelligence.clarity_score.enabled = false`

## Source paths

- `results/hparam_search/run_20260324_171511/run_meta.json`
- `results/hparam_search/run_20260324_171511/best_trial.json`
- `results/hparam_search/run_20260324_171511/validation/trial_001.json`
- `results/hparam_search/ri_slice8_launch_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_launch_20260326/best_trial.json`
- `results/hparam_search/ri_slice8_launch_20260326/validation/trial_001.json`
- `results/hparam_search/run_20260326_090908/run_meta.json`
- `results/hparam_search/run_20260326_090908/best_trial.json`
- `results/hparam_search/run_20260326_090908/validation/trial_001.json`
- `results/hparam_search/run_20260327_080025/run_meta.json`
- `results/hparam_search/run_20260327_080025/best_trial.json`
- `results/hparam_search/run_20260327_080025/validation/trial_001.json`
- `results/hparam_search/run_20260327_080025/validation/trial_002.json`
- `results/hparam_search/run_20260327_080025/validation/trial_003.json`
- `results/hparam_search/run_20260327_080025/validation/trial_004.json`
- `results/hparam_search/run_20260327_080025/validation/trial_005.json`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/features_asof.py`
- `src/core/strategy/features_asof_parts/base_feature_utils.py`
- `src/core/strategy/features_asof_parts/fibonacci_feature_utils.py`
- `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `config/strategy/champions/tBTCUSD_3h.json`
