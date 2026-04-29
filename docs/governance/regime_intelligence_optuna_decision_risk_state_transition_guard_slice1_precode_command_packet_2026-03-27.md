# Regime Intelligence challenger family — DECISION risk-state transition-guard slice1 pre-code command packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / research-only / docs-only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet narrows the already chosen `DECISION / clarity-risk-state sizing` direction to one minimal proposed first research slice, but must remain docs-only and must not create YAML, launch, admissibility, runtime-validity, comparison, readiness, promotion, or writeback semantics.
- **Required Path:** `Full gated docs-only`
- **Objective:** Define exactly one minimal proposed first research slice inside the already chosen Decision sizing direction by varying only `multi_timeframe.regime_intelligence.risk_state.transition_guard.{guard_bars,mult}` while freezing the carried-forward Decision EV/edge plateau anchor exactly.
- **Candidate:** `tBTCUSD 3h RI DECISION risk-state transition-guard slice1`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Scope

- **Scope IN:** one docs-only pre-code packet selecting exactly one minimal Decision sizing seam; exact fixed versus tunable boundaries; exact future tuple set; exact research-only artifact boundary; exact falsification rule.
- **Scope OUT:** no source-code changes, no test changes, no YAML creation in this packet, no validator/preflight/smoke/launch work, no changes under `src/core/**`, no changes under `tests/**`, no changes under `config/optimizer/**`, no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_decision_risk_state_transition_guard_slice1_precode_command_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet remains pre-code only and does not imply launch or admissibility

For interpretation discipline inside this packet:

- exactly one seam must be selected
- the seam must remain entirely inside already implemented `risk_state.transition_guard`
- no sentence may reinterpret `research_slice` as runtime-valid RI conformity
- no sentence may open YAML, launch, admissibility, comparison, readiness, promotion, or writeback
- all sibling sizing surfaces must remain explicitly frozen or deferred

### Stop Conditions

- any wording that implies the slice is already runnable or launch-admissible now
- any wording that widens the seam beyond `transition_guard.{guard_bars,mult}`
- any wording that reopens `drawdown_guard`, `clarity_score`, `size_multiplier`, `OBJECTIVE`, or `SIGNAL` within this packet
- any wording that weakens family-registry, family-admission, or research-only boundaries

### Output required

- one reviewable docs-only pre-code packet
- exact proposed first-slice seam
- exact frozen backdrop
- exact future tuple set
- exact future research-only artifact boundary
- exact falsification condition

## Purpose

This packet answers one narrow question only:

- what is the smallest governance-admissible first slice inside the already chosen `DECISION / clarity-risk-state sizing` direction?

This packet chooses only a **proposed first research slice**.

It does **not**:

- create a runnable YAML
- authorize validator/preflight/smoke/launch
- create research-level admissibility
- create runtime-valid RI conformity
- reopen comparison, readiness, promotion, or champion/default writeback

## Governing basis

This packet is downstream of the following tracked artifacts and verified repo surfaces:

- `docs/governance/regime_intelligence_optuna_decision_clarity_risk_state_direction_packet_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_decision_ev_edge_slice1_execution_outcome_signoff_summary_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_decision_ev_edge_slice1_precode_command_packet_2026-03-27.md`
- `src/core/strategy/decision_sizing.py`
- `tests/utils/test_decision_sizing.py`
- `tests/utils/test_risk_state_multiplier.py`

Carried-forward meaning:

1. the broader `DECISION` class remains open, but the EV/edge seam is closed as `PLATEAU`
2. the next chosen class-level direction is `DECISION / clarity-risk-state sizing`
3. `decision_sizing.py` already consumes `risk_state.*`, `clarity_score.*`, and sibling `size_multiplier.{min,max}` surfaces
4. the next smaller slice must preserve single-seam attribution rather than reopen multiple sibling sizing surfaces at once
5. any future runnable lane still requires separate pre-code-to-launch governance after this packet

## Exact proposed first-slice seam

### Chosen now

The proposed first slice inside the Decision sizing direction is:

- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult`

Meaning:

- keep the lane inside already implemented `risk_state.transition_guard`
- vary only the duration and size-suppression strength of the post-regime-change transition guard
- keep all drawdown, clarity, EV/edge, signal/regime-definition, exit, and objective surfaces fixed

### Why this seam is chosen

This seam is chosen because it is the smallest remaining already implemented Decision-sizing surface that:

1. belongs to one coherent sub-mechanism
2. is already covered by focused tests
3. avoids reopening `clarity_score` enablement, clarity weights, or `size_multiplier` semantics
4. avoids the broader multi-parameter `drawdown_guard` seam
5. preserves one-seam attribution for any later research result

## Exact future tuple set

If a later runnable slice is opened, it must be limited to exactly `3 × 3 = 9` combinations:

- `(guard_bars=1, mult=0.55)`
- `(guard_bars=1, mult=0.65)`
- `(guard_bars=1, mult=0.75)`
- `(guard_bars=2, mult=0.55)`
- `(guard_bars=2, mult=0.65)`
- `(guard_bars=2, mult=0.75)`
- `(guard_bars=3, mult=0.55)`
- `(guard_bars=3, mult=0.65)`
- `(guard_bars=3, mult=0.75)`

Interpretation:

- `(2, 0.65)` is the anchor-centered point carried from the closed Decision EV/edge line
- `{1,2,3}` keeps the guard-window search local and bounded around the current anchor
- `{0.55,0.65,0.75}` keeps the transition multiplier search local and bounded around the current anchor

No other tuple is admissible in the first slice defined by this packet.

## Exact frozen backdrop

Unless a later separately governed packet says otherwise, everything outside the chosen seam remains frozen to the carried-forward Decision EV/edge plateau anchor.

### Family / authority / identity — frozen

- `strategy_family = ri`
- `meta.runs.strategy = grid`
- `meta.runs.run_intent = research_slice`
- `meta.runs.score_version = v2`
- `multi_timeframe.regime_intelligence.version = v2`
- `multi_timeframe.regime_intelligence.authority_mode = regime_module`

### Signal / regime-definition backdrop — frozen

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
- `multi_timeframe.regime_intelligence.regime_definition.adx_trend_threshold = 23.0`
- `multi_timeframe.regime_intelligence.regime_definition.adx_range_threshold = 18.0`
- `multi_timeframe.regime_intelligence.regime_definition.slope_threshold = 0.001`
- `multi_timeframe.regime_intelligence.regime_definition.volatility_threshold = 0.05`

### EV / edge and execution-management backdrop — frozen

- `ev.R_default = 1.6 / 1.8 / 2.0` is **closed as prior seam** and must not be reopened in this packet
- `thresholds.min_edge = 0.00 / 0.01 / 0.02` is **closed as prior seam** and must not be reopened in this packet
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
- `multi_timeframe.ltf_override_threshold = 0.38`

### Decision sizing freeze-table — exact freeze

The following sizing surfaces are frozen in the first slice:

- `multi_timeframe.regime_intelligence.clarity_score.enabled = false`
- all `multi_timeframe.regime_intelligence.clarity_score.*` weights and related clarity fields remain frozen / unopened
- all `multi_timeframe.regime_intelligence.size_multiplier.{min,max}` fields remain frozen / unopened
- `multi_timeframe.regime_intelligence.risk_state.enabled = true`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold = 0.04`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult = 1.0`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold = 0.06`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult = 0.65`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.enabled = true`
- only `transition_guard.guard_bars` and `transition_guard.mult` are opened by this packet

## Explicitly deferred sibling surfaces

The following surfaces are **not chosen now** and are explicitly deferred to later separate governance:

- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.*`
- `multi_timeframe.regime_intelligence.clarity_score.*`
- `multi_timeframe.regime_intelligence.size_multiplier.{min,max}`
- any mixed `risk_state + clarity` slice
- any `OBJECTIVE` reopening
- any `SIGNAL / feature-surface` reopening

Reason:

- `drawdown_guard` is a broader multi-parameter seam
- `clarity_score` and `size_multiplier` together reopen clarity enablement and weighting semantics
- mixed slices break one-seam attribution

## Future artifacts allowed after separate governance

If and only if a later packet opens a runnable slice, the intended artifact set for that later step is expected to include:

- one canonical optimizer YAML under `config/optimizer/3h/ri_challenger_family_v1/`
- one bounded smoke YAML in the same canonical zone
- validator/preflight/smoke evidence
- later launch authorization packet if gates pass
- later execution outcome signoff summary

This packet itself creates **none** of those artifacts.

## Expected improvement signature

A later transition-guard slice would count as improving only if at least one validated artifact:

1. strictly exceeds validation score `0.26974911658712664`, and
2. does **not** reproduce the closed plateau tuple below:
   - validation score: `0.26974911658712664`
   - profit factor: `1.8845797002042906`
   - max drawdown: `0.027808774550017137`
   - trades: `63`
   - sharpe: `0.20047738907046656`

## Falsification condition

A later transition-guard slice is falsified if either:

1. no validated artifact exceeds `0.26974911658712664`, or
2. the best validated artifact reproduces the exact plateau tuple above

## Evidence basis for this choice

The governing evidence for choosing this seam includes:

- `src/core/strategy/decision_sizing.py` — implementation of `risk_state.transition_guard`, `risk_state.drawdown_guard`, `clarity_score`, and sibling `size_multiplier`
- `tests/utils/test_decision_sizing.py` — multiplicative sizing composition including risk-state and clarity paths
- `tests/utils/test_risk_state_multiplier.py` — focused transition-guard and drawdown-guard behavior coverage

No verified repository-local skill is claimed as sole authority for this packet beyond general governance/reference use already established elsewhere.

## Authority boundary

This packet is **pre-code only**.

It does **not**:

- authorize YAML creation now
- authorize research-level admissibility now
- authorize launch now
- authorize runtime-valid RI conformity
- authorize comparison, readiness, promotion, or writeback

Any later runnable lane still requires a separate packet that explicitly opens those next steps.

## Bottom line

The first proposed slice inside the already chosen `DECISION / clarity-risk-state sizing` direction is now narrowed to one minimal seam:

- **`risk_state.transition_guard.{guard_bars,mult}` only**

Everything else remains explicitly frozen or deferred.

This packet preserves research-only boundaries, single-seam attribution, and keeps YAML/launch/admissibility closed until later separate governance says otherwise.
