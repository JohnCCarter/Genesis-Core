# Regime Intelligence challenger family — DECISION risk-state transition-guard slice1 YAML shape review packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `review-only / proposal-only / docs-only / no YAML authoring or launch authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet documents only a proposed future YAML shape for two already reserved subject paths, plus later evidence-collection requirements, but must remain narrower than YAML authoring and narrower than launch authorization.
- **Required Path:** `Full gated docs-only`
- **Objective:** Review the proposed future canonical and bounded-smoke YAML shapes for the already reserved `transition_guard` slice1 subject paths without creating files, without authoring save-ready YAML, and without authorizing execution.
- **Candidate:** `future tBTCUSD 3h RI DECISION transition-guard slice1 YAML-shape review`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only proposal/review packet; the already reserved future canonical subject path; the already reserved future bounded smoke subject path; proposed future shape description only; exact fixed backdrop restatement; exact `transition_guard` grid restatement; later evidence-collection requirements; explicit non-claims and non-authorizations.
- **Scope OUT:** no source-code changes, no test changes, no changes under `src/core/**`, no changes under `tests/**`, no changes under `config/optimizer/**`, no changes under `tmp/**`, no changes under `results/**`, no file creation under the reserved paths, no save-ready YAML, no validator/preflight/smoke execution, no gate-pass claims, no launch authorization, no runtime-valid RI conformity, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_yaml_shape_review_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet remains proposal-only, review-only, and narrower than YAML authoring
- manual wording audit that no sentence claims launch, gate pass, or config materialization

For interpretation discipline inside this packet:

- the seam must remain strictly limited to `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`
- the tunable grid must remain exactly `{1,2,3} × {0.55,0.65,0.75}`
- the already reserved subject paths must be referenced only, not materialized
- any future YAML shape description must remain non-authoritative and non-save-ready
- no sentence may reopen or re-rank the closed `EV / edge` seam
- no sentence may reopen `risk_state.drawdown_guard.*`, `clarity_score.*`, `size_multiplier.{min,max}`, `OBJECTIVE`, or `SIGNAL / feature-surface`
- no sentence may imply runtime-validity, comparison, readiness, promotion, or writeback authority

### Stop Conditions

- any wording that reads like file creation instructions under `config/optimizer/**`
- any full YAML block that is effectively save-ready
- any wording that upgrades this packet from proposal/review to authoring or execution approval
- any wording that widens the seam beyond `transition_guard.{guard_bars,mult}`
- any wording that changes the exact nine-tuple grid
- any wording that silently re-adjudicates plateau-equivalent EV variants
- any wording that claims or implies passed gates, launch readiness, or approved execution

### Output required

- one reviewable docs-only YAML-shape review packet
- exact references to the two already reserved future subject paths
- proposed future canonical shape description only
- proposed future bounded-smoke shape description only
- exact fixed backdrop restatement
- exact tunable surface restatement
- later evidence-collection requirements only
- exact non-claims and non-authorizations

## What this packet is and is not

This packet is:

- docs-only
- review-only
- proposal-only
- shape/evidence scoping only

This packet is **not**:

- YAML authoring
- YAML materialization
- a gate-pass packet
- a launch-admissibility packet
- a launch-authorization packet
- an execution packet
- an outcome-signoff packet

No file is created or modified under `config/optimizer/**` by this packet.

## Prior governance references

This packet is downstream of the following already tracked governance chain:

- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_clarity_risk_state_direction_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_precode_command_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_launch_admissibility_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_setup_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_decision_ev_edge_slice1_execution_outcome_signoff_summary_2026-03-27.md`

Carried-forward meaning:

1. the active class-level direction remains `DECISION / clarity-risk-state sizing surface`
2. the only open first seam remains `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}`
3. the only admissible grid remains exactly nine tuples
4. the setup packet reserved future subject paths, but did not author YAML
5. this packet may review only a proposed future shape for those reserved paths and what later evidence must prove

## Reserved future subject paths referenced only

The only reserved future subject paths referenced by this packet are:

### Proposed future canonical subject path — referenced only

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_2024_v1.yaml`

### Proposed future bounded-smoke subject path — referenced only

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_smoke_20260327.yaml`

These paths remain reserved references only.
This packet does not create, edit, or approve files at those paths.

## Proposed future canonical YAML shape — review only

The lists below are review descriptors only.
They are not save-ready YAML and must not be materialized from this packet.

### Proposed future canonical meta / run envelope

For proposal-only future shape scoping, the reserved future canonical subject would preserve the following exact envelope:

- `strategy_family = ri`
- `description = Regime Intelligence Decision risk-state transition-guard slice1: bounded 9-combination research grid over transition_guard guard_bars and mult on 2023-12-21..2024-06-30, validate 2024-07-01..2024-12-31 (3h)`
- `meta.symbol = tBTCUSD`
- `meta.timeframe = 3h`
- `meta.snapshot_id = snap_tBTCUSD_3h_2023-12-21_2024-06-30_v1`
- `meta.warmup_bars = 120`
- `meta.runs.strategy = grid`
- `meta.runs.score_version = v2`
- `meta.runs.run_intent = research_slice`
- `meta.runs.use_sample_range = true`
- `meta.runs.sample_start = 2023-12-21`
- `meta.runs.sample_end = 2024-06-30`
- `meta.runs.validation.enabled = true`
- `meta.runs.validation.use_sample_range = true`
- `meta.runs.validation.sample_start = 2024-07-01`
- `meta.runs.validation.sample_end = 2024-12-31`
- `meta.runs.validation.top_n = 5`
- `meta.runs.validation.constraints.include_scoring_failures = false`
- `meta.runs.validation.constraints.min_trades = 20`
- `meta.runs.validation.constraints.min_profit_factor = 1.05`
- `meta.runs.validation.constraints.max_max_dd = 0.35`
- `meta.runs.resume = false`
- `meta.runs.max_trials = 9`
- `meta.runs.max_concurrent = 1`
- `meta.runs.promotion.enabled = false`

### Proposed future canonical constraints

For proposal-only future shape scoping, the reserved future canonical subject would preserve the following constraint envelope:

- `constraints.include_scoring_failures = false`
- `constraints.max_max_dd = 0.60`
- `constraints.min_profit_factor = 0.80`
- `constraints.scoring_thresholds.min_trades = 10`
- `constraints.scoring_thresholds.min_profit_factor = 0.0`
- `constraints.scoring_thresholds.max_max_dd = 1.0`

### Proposed future canonical fixed backdrop

For proposal-only future YAML-shape scoping, and without reopening or comparing the closed EV/edge seam, the packet may carry forward the already cited `validation/trial_001` fixed values (`ev.R_default = 1.6`, `thresholds.min_edge = 0.01`) as a proposed freeze anchor only; this does not authorize execution, does not materialize YAML, and does not re-rank plateau-equivalent EV alternatives.

All other proposed future canonical fixed values would remain:

- `thresholds.regime_proba.bull = 0.5`
- `thresholds.regime_proba.bear = 0.5`
- `thresholds.regime_proba.ranging = 0.5`
- `thresholds.signal_adaptation.atr_period = 14`
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
- `thresholds.entry_conf_overall = 0.27`
- `thresholds.regime_proba.balanced = 0.36`
- `thresholds.signal_adaptation.zones.low.entry_conf_overall = 0.14`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall = 0.42`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall = 0.34`
- `thresholds.signal_adaptation.zones.low.regime_proba = 0.32`
- `thresholds.signal_adaptation.zones.mid.regime_proba = 0.52`
- `thresholds.signal_adaptation.zones.high.regime_proba = 0.58`
- `htf_exit_config.partial_1_pct = 0.5`
- `htf_exit_config.partial_2_pct = 0.45`
- `htf_exit_config.fib_threshold_atr = 0.9`
- `htf_exit_config.trail_atr_multiplier = 2.5`
- `exit.trailing_stop_pct = 0.022`
- `exit.stop_loss_pct = 0.016`
- `exit.max_hold_bars = 8`
- `exit.exit_conf_threshold = 0.40`
- `htf_fib.entry.tolerance_atr = 4.0`
- `htf_fib.entry.long_max_level = 0.236`
- `htf_fib.entry.short_min_level = 0.35`
- `ltf_fib.entry.tolerance_atr = 1.5`
- `ltf_fib.entry.long_max_level = 0.146`
- `ltf_fib.entry.short_min_level = 0.236`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold = 0.04`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult = 1.0`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold = 0.06`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult = 0.65`
- `risk.htf_regime_size_multipliers.bear = 0.65`
- `risk.volatility_sizing.high_vol_multiplier = 0.70`
- `gates.hysteresis_steps = 4`
- `gates.cooldown_bars = 1`
- `multi_timeframe.ltf_override_threshold = 0.38`

### Proposed future canonical tunable surface only

The only proposed future canonical tunables remain:

- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult`

The only proposed future canonical grid remains exactly:

- `(guard_bars=1, mult=0.55)`
- `(guard_bars=1, mult=0.65)`
- `(guard_bars=1, mult=0.75)`
- `(guard_bars=2, mult=0.55)`
- `(guard_bars=2, mult=0.65)`
- `(guard_bars=2, mult=0.75)`
- `(guard_bars=3, mult=0.55)`
- `(guard_bars=3, mult=0.65)`
- `(guard_bars=3, mult=0.75)`

This remains an exact $3 \times 3 = 9$ tuple surface.
No other tunable is proposed here.

## Proposed future bounded-smoke YAML shape — review only

This section is also review-only and proposal-only.
It does not approve smoke execution.

### Proposed future bounded-smoke meta / run envelope

For proposal-only future shape scoping, the reserved future bounded-smoke subject would preserve the same structural family/backdrop as the proposed canonical subject, with the following bounded-smoke envelope:

- `strategy_family = ri`
- `description = Regime Intelligence Decision risk-state transition-guard slice1 smoke: bounded 9-combination research grid over transition_guard guard_bars and mult on 2024-01-02..2024-03-02 (3h)`
- `meta.symbol = tBTCUSD`
- `meta.timeframe = 3h`
- `meta.snapshot_id = snap_tBTCUSD_3h_2023-12-21_2024-06-30_v1`
- `meta.warmup_bars = 120`
- `meta.runs.strategy = grid`
- `meta.runs.score_version = v2`
- `meta.runs.run_intent = research_slice`
- `meta.runs.use_sample_range = true`
- `meta.runs.sample_start = 2024-01-02`
- `meta.runs.sample_end = 2024-03-02`
- `meta.runs.validation.enabled = false`
- `meta.runs.resume = false`
- `meta.runs.max_trials = 9`
- `meta.runs.max_concurrent = 1`
- `meta.runs.promotion.enabled = false`

### Proposed future bounded-smoke constraints and fixed backdrop

For proposal-only future shape scoping, the reserved future bounded-smoke subject would preserve:

- the same fixed family / authority / regime-definition / exit / fib / risk-state backdrop as the proposed canonical subject
- the same proposal-only freeze anchor for the closed EV/edge seam:
  - `ev.R_default = 1.6`
  - `thresholds.min_edge = 0.01`
- the same single-seam tunable attribution to `transition_guard.{guard_bars,mult}` only

The only bounded-smoke-specific proposal-only constraint differences would be:

- `constraints.scoring_thresholds.min_trades = 5`
- `meta.runs.validation.enabled = false`
- shortened bounded sample window as listed above

These bounded-smoke shape notes are proposed future review descriptors only.
They are not smoke authorization, not save-ready YAML, and not evidence that smoke semantics are already approved for execution.

### Proposed future bounded-smoke tunable surface only

The only proposed future bounded-smoke tunables remain exactly the same nine-tuple grid:

- `(guard_bars=1, mult=0.55)`
- `(guard_bars=1, mult=0.65)`
- `(guard_bars=1, mult=0.75)`
- `(guard_bars=2, mult=0.55)`
- `(guard_bars=2, mult=0.65)`
- `(guard_bars=2, mult=0.75)`
- `(guard_bars=3, mult=0.55)`
- `(guard_bars=3, mult=0.65)`
- `(guard_bars=3, mult=0.75)`

No other smoke tunable is proposed here.

## Exact fixed backdrop — restated for review only

For this proposal-only packet, the exact fixed backdrop means all of the following stay fixed outside `transition_guard.{guard_bars,mult}`:

- family / authority / identity markers
- signal / regime-definition thresholds and adaptation backdrop
- the proposal-only EV/edge freeze anchor carried from cited `validation/trial_001`
- exit / management backdrop
- HTF/LTF fib backdrop
- `risk_state.drawdown_guard.*`
- `clarity_score.*`
- `size_multiplier.{min,max}`
- `OBJECTIVE` deferred state
- `SIGNAL / feature-surface` deferred state

Nothing in this packet opens any of those surfaces.

## Exact tunable surface — restated for review only

The only surface proposed for later authoring review remains:

- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult`

The only proposed grid remains exactly:

- `guard_bars ∈ {1,2,3}`
- `mult ∈ {0.55,0.65,0.75}`

This packet opens no other dimension.

## Later evidence-collection requirements only

This packet does not claim any evidence has been collected or passed.
It records only what a later separate evidence-collection / authoring review step would still need to show.

### Later canonical evidence would need to show

A later separate evidence step would need to show that the future canonical subject:

1. if a later separately approved authoring step occurs, any resulting YAML would need to exist only at the already reserved canonical path
2. preserves the exact fixed backdrop listed in this packet
3. varies only `transition_guard.guard_bars` and `transition_guard.mult`
4. enumerates exactly the nine tuples listed in this packet
5. preserves research-only settings with promotion disabled
6. does not widen the seam, grid, or frozen backdrop

### Later bounded-smoke evidence would need to show

A later separate evidence step would need to show that the future bounded-smoke subject:

1. if a later separately approved authoring step occurs, any resulting YAML would need to exist only at the already reserved bounded-smoke path
2. preserves the same fixed backdrop and same proposal-only EV/edge freeze anchor as the future canonical subject
3. preserves the same exact nine-tuple `transition_guard` surface
4. remains bounded as a seam-check artifact only
5. does not become comparison, readiness, promotion, or launch authority by implication

### Later validator / preflight / smoke evidence would need to show

If later separately approved, a future evidence bundle would still need to show:

1. validator confirms only the exact reserved single seam and exact nine-tuple grid
2. preflight confirms the same research-only boundary and unchanged frozen backdrop
3. any smoke evidence remains bounded to seam-checking and artifact completeness only
4. no execution evidence is interpreted as runtime-valid RI conformity, comparison opening, readiness, promotion, or writeback authority

## Explicit non-claims and non-authorizations

This packet does **not** claim any of the following:

- that either reserved YAML subject already exists
- that either reserved YAML subject is approved for creation now
- that the proposed future canonical shape is save-ready
- that the proposed future bounded-smoke shape is save-ready
- that validator has passed
- that preflight has passed
- that smoke has passed
- that the slice is launch-admissible now
- that the slice is launch-authorized now
- that the slice is runtime-valid RI conformity
- that comparison, readiness, promotion, or writeback is open

## Next admissible step after this packet

If this packet is accepted, the next admissible step remains only:

- a later separate docs-only authoring-admissibility / evidence review for the same two already reserved subject paths

That later step would remain separate from YAML creation, launch authorization, and any execution approval unless independently approved.
That later step would still need its own separate bounded evidence before any execution packet could even be considered.

## Bottom line

This packet does one narrow thing only:

- it reviews a **proposed future** canonical shape and a **proposed future** bounded-smoke shape for the already reserved `transition_guard` slice1 subject paths, while keeping the seam, grid, fixed backdrop, and authority boundaries explicit and unchanged.

Anything broader must stop and return to new governance review.
