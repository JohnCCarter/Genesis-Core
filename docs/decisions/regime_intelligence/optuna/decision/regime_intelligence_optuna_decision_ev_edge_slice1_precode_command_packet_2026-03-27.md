# Regime Intelligence challenger family — DECISION EV/edge slice1 pre-code command packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code / research-only / config-only lane proposed`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: this packet opens a research-only optimizer lane through docs and research configs only, with no `src/**`, `tests/**`, runtime authority, champion, or objective changes.
- **Required Path:** `Full`
- **Objective:** Open the first admissible Decision slice by searching only the EV/edge seam while freezing the latest plateau anchor tuple exactly.
- **Candidate:** `tBTCUSD 3h RI Decision EV/edge slice1`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Artifacts

- docs/governance decision roadmap
- docs/governance slice1 pre-code packet
- canonical optimizer YAML under `config/optimizer/3h/ri_challenger_family_v1/`
- smoke YAML in the same canonical optimizer zone
- validator/preflight/smoke/full-run research artifacts under `results/**`
- launch authorization packet
- execution outcome signoff summary

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Usage mode in this packet:** required guardrail reference for validator, preflight, baseline discipline, and canonical comparability before any long Optuna/grid-style research run

### Constraints

- `NO SOURCE-CODE CHANGE`
- `NO TEST CHANGE`
- `research-only`
- `config-only lane`
- `objective/version/metric fixed`
- `no comparison/readiness/promotion/writeback`
- `no reopen of exhausted signal or gating/selectivity seams`

### Scope

- **Scope IN:**
  - one Decision slice1 roadmap-to-launch packet chain
  - exact frozen anchor tuple carried from the latest closed plateau line
  - exact `3 × 3 = 9` EV/edge tuple set
  - canonical YAML + smoke YAML creation in `config/optimizer/3h/ri_challenger_family_v1/`
  - validator/preflight/smoke/full-run execution under canonical flags
  - launch authorization and final outcome signoff
- **Scope OUT:**
  - no `src/**` changes
  - no `tests/**` changes
  - no `config/strategy/champions/**` changes
  - no `runtime.json` or runtime authority changes
  - no objective/scoring/version changes
  - no comparison opening
  - no readiness opening
  - no promotion opening
  - no writeback
  - no reopening of signal threshold, regime-definition, exit/override, or gating/selectivity seams
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_roadmap_2026-03-27.md`
  - `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_ev_edge_slice1_precode_command_packet_2026-03-27.md`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_2024_v1.yaml`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_smoke_20260327.yaml`
  - later launch/signoff docs if gates pass
- **Max files touched:** `6` before results artifacts

### Gates required

- `pre-commit run --files <touched docs/yaml files>` or equivalent lint/format validation for touched docs/YAML
- `python scripts/validate/validate_optimizer_config.py <canonical yaml>`
- `python scripts/validate/validate_optimizer_config.py <smoke yaml>`
- `python scripts/preflight/preflight_optuna_check.py <canonical yaml>` under canonical flags
- bounded smoke execution with artifact completeness proof
- determinism replay test (decision parity)
- feature cache invariance test
- pipeline invariant check (component order hash)
- one canonical full run if and only if prior gates pass and launch authorization is written

### Stop Conditions

- any scope drift outside the EV/edge seam
- any attempt to change `src/**`, `tests/**`, runtime authority, objective, or champions
- any ambiguity about the exact frozen anchor tuple
- validator or preflight hard failure
- `thresholds.min_edge = 0.00` is rejected, normalized away, or emitted ambiguously in artifacts
- smoke artifacts missing, failing, or showing zero trades
- determinism, feature-cache, or pipeline-invariant regression

### Output required

- reviewable Decision slice1 packet
- canonical full-run YAML
- canonical smoke YAML
- validator/preflight/smoke evidence
- launch authorization packet if gates pass
- execution outcome signoff summary classifying exactly `IMPROVING`, `PLATEAU`, or `FAIL`

## Purpose

This packet opens exactly one new RI Decision surface after the two SIGNAL lanes closed as plateau.

It does **not**:

- reopen already exhausted signal/gating surfaces
- authorize source-code enablement
- claim runtime-valid RI conformity
- authorize comparison, readiness, promotion, or writeback

## Governing basis

This packet is downstream of the following current evidence:

- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_execution_outcome_signoff_summary_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_plateau_evidence_slice7_slice10_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_seam_decision_packet_2026-03-27.md`
- `src/core/strategy/decision_gates.py`
- `src/core/config/schema.py`

Carried-forward meaning:

1. threshold-only SIGNAL closed as plateau
2. regime-definition SIGNAL closed as plateau
3. gating/selectivity seam is not the next seam
4. Decision must now open a smaller new surface that does not backdoor other lane changes
5. `ev.R_default` and `thresholds.min_edge` are already canonical config paths in the decision layer

## Exact frozen anchor

### Anchor sources

- plateau-closing signoff:
  `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_execution_outcome_signoff_summary_2026-03-27.md`
- frozen baseline config:
  `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`

### Exact frozen tuple carried into Decision slice1

All non-EV/edge surfaces must remain exactly frozen to:

- `strategy_family = ri`
- `meta.runs.strategy = grid`
- `meta.runs.run_intent = research_slice`
- `meta.runs.score_version = v2`
- `thresholds.entry_conf_overall = 0.27`
- `thresholds.regime_proba.balanced = 0.36`
- `thresholds.regime_proba.bull = 0.5`
- `thresholds.regime_proba.bear = 0.5`
- `thresholds.regime_proba.ranging = 0.5`
- `thresholds.signal_adaptation.atr_period = 14`
- `thresholds.signal_adaptation.zones.low.entry_conf_overall = 0.14`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall = 0.42`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall = 0.34`
- `thresholds.signal_adaptation.zones.low.regime_proba = 0.32`
- `thresholds.signal_adaptation.zones.mid.regime_proba = 0.52`
- `thresholds.signal_adaptation.zones.high.regime_proba = 0.58`
- `gates.hysteresis_steps = 4`
- `gates.cooldown_bars = 1`
- `exit.max_hold_bars = 8`
- `exit.exit_conf_threshold = 0.40`
- `exit.trailing_stop_pct = 0.022`
- `exit.stop_loss_pct = 0.016`
- `htf_exit_config.partial_1_pct = 0.5`
- `htf_exit_config.partial_2_pct = 0.45`
- `htf_exit_config.fib_threshold_atr = 0.9`
- `htf_exit_config.trail_atr_multiplier = 2.5`
- `htf_fib.entry.tolerance_atr = 4.0`
- `htf_fib.entry.long_max_level = 0.236`
- `htf_fib.entry.short_min_level = 0.35`
- `ltf_fib.entry.tolerance_atr = 1.5`
- `ltf_fib.entry.long_max_level = 0.146`
- `ltf_fib.entry.short_min_level = 0.236`
- `multi_timeframe.ltf_override_threshold = 0.38`
- `multi_timeframe.regime_intelligence.enabled = true`
- `multi_timeframe.regime_intelligence.version = v2`
- `multi_timeframe.regime_intelligence.authority_mode = regime_module`
- `multi_timeframe.regime_intelligence.clarity_score.enabled = false`
- `multi_timeframe.regime_intelligence.risk_state.enabled = true`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.enabled = true`
- `multi_timeframe.regime_intelligence.regime_definition.adx_trend_threshold = 23.0`
- `multi_timeframe.regime_intelligence.regime_definition.adx_range_threshold = 18.0`
- `multi_timeframe.regime_intelligence.regime_definition.slope_threshold = 0.001`
- `multi_timeframe.regime_intelligence.regime_definition.volatility_threshold = 0.05`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold = 0.04`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult = 1.0`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult = 0.65`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold = 0.06`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult = 0.65`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars = 2`
- `risk.htf_regime_size_multipliers.bear = 0.65`
- `risk.volatility_sizing.high_vol_multiplier = 0.70`

## Chosen search seam

### Chosen now

- `ev.R_default`
- `thresholds.min_edge`

### Not chosen now

- `thresholds.entry_conf_overall`
- `thresholds.regime_proba.balanced`
- `gates.hysteresis_steps`
- `gates.cooldown_bars`
- `multi_timeframe.regime_intelligence.clarity_score.*`
- `multi_timeframe.regime_intelligence.risk_state.*`
- any regime-definition or exit/override surface

## Exact slice1 tuple set

Slice1 is limited to exactly `9` combinations:

- `(ev.R_default=1.6, thresholds.min_edge=0.00)`
- `(ev.R_default=1.6, thresholds.min_edge=0.01)`
- `(ev.R_default=1.6, thresholds.min_edge=0.02)`
- `(ev.R_default=1.8, thresholds.min_edge=0.00)`
- `(ev.R_default=1.8, thresholds.min_edge=0.01)`
- `(ev.R_default=1.8, thresholds.min_edge=0.02)`
- `(ev.R_default=2.0, thresholds.min_edge=0.00)`
- `(ev.R_default=2.0, thresholds.min_edge=0.01)`
- `(ev.R_default=2.0, thresholds.min_edge=0.02)`

Interpretation:

- `1.8 / 0.01` is the anchor-centered point
- `1.6` tests stricter EV acceptance
- `2.0` tests looser EV acceptance
- `0.00` explicitly disables edge gating only if it survives validator, preflight, and emitted artifacts as an explicit serialized value

No other search widening is allowed in slice1.

## Expected improvement signature

Decision slice1 counts as improving only if at least one validated artifact strictly exceeds:

- validation score `0.26974911658712664`

Improvement must come from the approved EV/edge seam only.

## Plateau / falsification rule

Decision slice1 closes as `PLATEAU` if no validated artifact strictly exceeds `0.26974911658712664`.

Equality to `0.26974911658712664` remains `PLATEAU`, even if the EV/edge pair differs from the anchor pair.

## Required evidence details

Before launch authorization, evidence must show:

1. exactly two searchable parameters
2. exactly nine enumerated combinations
3. `thresholds.min_edge = 0.00` appears as an explicit literal in config and emitted artifacts if retained
4. validator returned no hard failure
5. canonical preflight returned overall `[OK]`
6. smoke artifacts are complete, non-failing, and non-zero-trade
7. determinism replay, feature cache invariance, and pipeline invariant checks remain green

If `0.00` is rejected or normalized away, stop and amend the lane before smoke or launch.

## Research-only interpretation boundary

This packet authorizes only a research-only slice definition path.

It does **not** authorize:

- runtime-valid RI claims
- canonical family rewrite
- comparison against incumbent in the same packet
- readiness opening
- promotion opening
- champion/default writeback

Any improving result may open only a separate later comparison/readiness packet.

## Bottom line

The first Decision slice is opened as a strict config-only EV/edge lane:

- freeze the latest plateau tuple exactly
- search only `ev.R_default × thresholds.min_edge`
- require explicit evidence for the `0.00` literal
- classify equal-score outcomes as `PLATEAU`

Nothing in this packet authorizes launch by itself; launch still requires validator, preflight, smoke, and a separate authorization packet.
