# Regime Intelligence challenger family — DECISION risk-state transition-guard slice1 names-only leaf placement packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `placement-only / names-only / docs-only / no schema binding`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet maps already approved leaf-field names to the same two already reserved subject paths, but must remain narrower than YAML creation, narrower than launch, and non-binding with respect to schema, ordering, requiredness, or serialization shape.
- **Required Path:** `Full gated docs-only`
- **Objective:** Record a names-only leaf-to-path placement for the already approved leaf inventory under the same two reserved transition-guard slice1 subject paths, without values, without schema approval, and without YAML authoring authority.
- **Candidate:** `future tBTCUSD 3h RI DECISION transition-guard slice1 names-only leaf placement`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only placement-only packet; exact same two reserved subject paths; only already approved leaf names from the names-only leaf inventory; names-only leaf-to-path placement; tentative grouping notes only if clearly marked non-binding; explicit deferred items; explicit non-approval statement.
- **Scope OUT:** no source-code changes, no test changes, no changes under `src/core/**`, no changes under `tests/**`, no changes under `config/optimizer/**`, no changes under `tmp/**`, no changes under `results/**`, no YAML authoring, no file creation outside this one docs packet, no YAML/config/result/tmp file creation, no new leaf names, no values, no defaults, no ranges, no step sizes, no types, no requiredness, no ordering rules, no pseudo-YAML, no pseudo-JSON, no schema-like key-tree layout, no serialization claims, no launch, no validator/preflight/smoke execution, no gate claims, no runtime-valid RI conformity, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_names_only_leaf_placement_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet remains names-only placement
- manual wording audit that the packet contains no value, type, ordering, or schema-binding semantics

For interpretation discipline inside this packet:

- only already approved leaf names may appear
- only the same two reserved subject paths may be used as placement targets
- any grouping note must remain explicitly non-ordering and non-schema-binding
- no sentence may imply that placement equals YAML approval, authoring approval, or launch authority
- no sentence may imply parent/child or required/optional semantics beyond names-only placement

### Stop Conditions

- any new leaf name or renamed leaf name
- any third path, fallback path, alias path, or auxiliary bucket
- any values, defaults, ranges, types, requiredness, or ordering rules
- any pseudo-YAML / pseudo-JSON / schema sketch
- any statement that placement is approved serialization shape
- any wording that upgrades this packet into YAML authoring, launch preparation, or execution approval

### Output required

- one reviewable docs-only names-only placement packet
- exact same two reserved subject paths
- names-only leaf-to-path placement
- deferred items / unresolved placement notes
- exact red lines / non-approval statement

## Purpose / decision ask

This packet answers one narrow question only:

- for each already approved leaf-field name in scope, which of the same two already reserved `transition_guard` slice1 subject paths does it belong to for names-only placement purposes?

This packet does **not** answer:

- what value any field should hold
- what type any field should hold
- what order any field should appear in
- what nesting or serialization shape should be used
- whether any YAML should now be created
- whether any execution or launch step may begin

## Approved inputs only

This packet relies only on the already approved upstream chain, especially:

- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_leaf_field_inventory_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_leaf_placement_admissibility_packet_2026-03-27.md`

It also remains downstream of the earlier approved transition-guard chain documents already cited there.

## Reserved subject paths

The only admissible placement targets remain:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_2024_v1.yaml`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_smoke_20260327.yaml`

No third path, fallback path, or alias path is opened here.

## Names-only leaf-to-path placement

The lists below are names-only placement records.
They do not express values, types, ordering, requiredness, nesting, or approved serialization shape.

### Shared placement — both reserved subject paths

- `config/optimizer/description`
- `config/optimizer/strategy_family`
- `constraints/include_scoring_failures`
- `constraints/max_max_dd`
- `constraints/min_profit_factor`
- `constraints/scoring_thresholds/max_max_dd`
- `constraints/scoring_thresholds/min_profit_factor`
- `constraints/scoring_thresholds/min_trades`
- `meta/runs/max_concurrent`
- `meta/runs/max_trials`
- `meta/runs/promotion/enabled`
- `meta/runs/resume`
- `meta/runs/run_intent`
- `meta/runs/sample_end`
- `meta/runs/sample_start`
- `meta/runs/score_version`
- `meta/runs/strategy`
- `meta/runs/use_sample_range`
- `meta/runs/validation/enabled`
- `meta/snapshot_id`
- `meta/symbol`
- `meta/timeframe`
- `meta/warmup_bars`
- `parameters/ev.R_default`
- `parameters/exit.exit_conf_threshold`
- `parameters/exit.max_hold_bars`
- `parameters/exit.stop_loss_pct`
- `parameters/exit.trailing_stop_pct`
- `parameters/gates.cooldown_bars`
- `parameters/gates.hysteresis_steps`
- `parameters/htf_exit_config.fib_threshold_atr`
- `parameters/htf_exit_config.partial_1_pct`
- `parameters/htf_exit_config.partial_2_pct`
- `parameters/htf_exit_config.trail_atr_multiplier`
- `parameters/htf_fib.entry.long_max_level`
- `parameters/htf_fib.entry.short_min_level`
- `parameters/htf_fib.entry.tolerance_atr`
- `parameters/ltf_fib.entry.long_max_level`
- `parameters/ltf_fib.entry.short_min_level`
- `parameters/ltf_fib.entry.tolerance_atr`
- `parameters/multi_timeframe.ltf_override_threshold`
- `parameters/multi_timeframe.regime_intelligence.authority_mode`
- `parameters/multi_timeframe.regime_intelligence.clarity_score.enabled`
- `parameters/multi_timeframe.regime_intelligence.enabled`
- `parameters/multi_timeframe.regime_intelligence.regime_definition.adx_range_threshold`
- `parameters/multi_timeframe.regime_intelligence.regime_definition.adx_trend_threshold`
- `parameters/multi_timeframe.regime_intelligence.regime_definition.slope_threshold`
- `parameters/multi_timeframe.regime_intelligence.regime_definition.volatility_threshold`
- `parameters/multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult`
- `parameters/multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold`
- `parameters/multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult`
- `parameters/multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold`
- `parameters/multi_timeframe.regime_intelligence.risk_state.enabled`
- `parameters/multi_timeframe.regime_intelligence.risk_state.transition_guard.enabled`
- `parameters/multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars`
- `parameters/multi_timeframe.regime_intelligence.risk_state.transition_guard.mult`
- `parameters/multi_timeframe.regime_intelligence.version`
- `parameters/risk.htf_regime_size_multipliers.bear`
- `parameters/risk.volatility_sizing.high_vol_multiplier`
- `parameters/thresholds.entry_conf_overall`
- `parameters/thresholds.min_edge`
- `parameters/thresholds.regime_proba.balanced`
- `parameters/thresholds.regime_proba.bear`
- `parameters/thresholds.regime_proba.bull`
- `parameters/thresholds.regime_proba.ranging`
- `parameters/thresholds.signal_adaptation.atr_period`
- `parameters/thresholds.signal_adaptation.zones.high.entry_conf_overall`
- `parameters/thresholds.signal_adaptation.zones.high.regime_proba`
- `parameters/thresholds.signal_adaptation.zones.low.entry_conf_overall`
- `parameters/thresholds.signal_adaptation.zones.low.regime_proba`
- `parameters/thresholds.signal_adaptation.zones.mid.entry_conf_overall`
- `parameters/thresholds.signal_adaptation.zones.mid.regime_proba`

### Canonical-only placement

- `meta/runs/validation/constraints/include_scoring_failures`
- `meta/runs/validation/constraints/max_max_dd`
- `meta/runs/validation/constraints/min_profit_factor`
- `meta/runs/validation/constraints/min_trades`
- `meta/runs/validation/sample_end`
- `meta/runs/validation/sample_start`
- `meta/runs/validation/top_n`
- `meta/runs/validation/use_sample_range`

### Bounded-smoke-only placement

- none

## Tentative grouping notes

The following notes are non-binding reading aids only:

- `config/optimizer/*` names remain placed with both reserved paths
- `meta/*` names remain placed according to whether the field appears in both or only one reserved path
- `constraints/*` names remain placed according to whether the field appears in both or only one reserved path
- `parameters/*` names remain placed according to whether the field appears in both or only one reserved path

These notes do **not** approve nesting, order, schema shape, or serialization form.

## Deferred items / unresolved placement questions

Still deferred beyond this packet:

- any serialization shape
- any nesting/tree layout
- any ordering or key sequence
- any values, defaults, ranges, or types
- any required/optional semantics
- any YAML authoring or file creation
- any validator/preflight/smoke evidence bundle
- any launch-admissibility or launch-authorization step
- any execution packet or outcome signoff

## Red lines / non-approval statement

This packet must not be read as:

- YAML authoring approval
- schema approval
- ordering approval
- requiredness approval
- value approval
- launch guidance
- execution guidance

Any broader reading is out of scope.

## Bottom line

This packet does one narrow thing only:

- it maps already approved leaf-field names to one of the two already reserved `transition_guard` slice1 subject paths, using names only and without approving values, schema, ordering, or YAML creation.
