# Regime Intelligence challenger family — DECISION roadmap

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `roadmap-defined / research-only / no launch authority by roadmap alone`

## Purpose

This roadmap defines the next governed RI continuation after both currently opened SIGNAL lanes closed as
non-improving plateaus.

It answers one narrow question:

- what is the next smallest admissible **Decision** lane, and how should it be driven from roadmap to
  executed outcome without reopening already exhausted seams?

This roadmap does **not** by itself:

- authorize launch
- create a runtime-valid RI candidate
- open comparison, readiness, promotion, or writeback
- authorize source-code changes

## Starting point

The carried-forward anchor for this roadmap is the latest fully executed and closed plateau line:

- canonical anchor YAML:
  `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`
- closing signoff:
  `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_execution_outcome_signoff_summary_2026-03-27.md`

That anchor closed with strict classification `PLATEAU` at validation score `0.26974911658712664`.

## Exact frozen anchor backdrop

Unless a later separately governed packet says otherwise, the Decision lane must inherit the following exact
research-only plateau backdrop:

- `thresholds.entry_conf_overall = 0.27`
- `thresholds.regime_proba.balanced = 0.36`
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
- `multi_timeframe.ltf_override_threshold = 0.38`
- `multi_timeframe.regime_intelligence.regime_definition.adx_trend_threshold = 23.0`
- `multi_timeframe.regime_intelligence.regime_definition.adx_range_threshold = 18.0`
- `multi_timeframe.regime_intelligence.regime_definition.slope_threshold = 0.001`
- `multi_timeframe.regime_intelligence.regime_definition.volatility_threshold = 0.05`
- `multi_timeframe.regime_intelligence.clarity_score.enabled = false`
- `multi_timeframe.regime_intelligence.risk_state.enabled = true`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.enabled = true`

Family identity remains research-only and fixed:

- `strategy_family = ri`
- `multi_timeframe.regime_intelligence.version = v2`
- `multi_timeframe.regime_intelligence.authority_mode = regime_module`
- objective/version/metric surface remains fixed at `score_version = v2`

## Decision seam inventory

### Already exhausted or explicitly not chosen now

The following seams are not the next lane:

- SIGNAL thresholds / zone selectivity
- SIGNAL regime-definition ADX-band surface
- exit/override cadence surface
- gating/selectivity seam:
  - `thresholds.entry_conf_overall`
  - `thresholds.regime_proba.balanced`
  - `gates.hysteresis_steps`
  - `gates.cooldown_bars`

Reason:

- they are already part of the plateau evidence line or explicitly parked as not-chosen-now in prior governance
  documents

### Chosen next seam

The next Decision lane is:

- **EV / edge seam**

Meaning:

- change only `ev.R_default`
- change only `thresholds.min_edge`
- keep all other surfaces exactly frozen to the latest plateau anchor

Why this seam is chosen:

1. it lives inside decision selection/gating rather than signal or objective layers
2. it is directly config-driven in the current runtime path and therefore does not require new code enablement
3. `ev.R_default` appears unsearched in the RI 3h challenger-family YAML line
4. `thresholds.min_edge` has remained fixed at `0.01`, so the pair forms a minimal new information surface

## Roadmap phases

### Phase 1 — pre-code governance packet

Create one launch-preparatory command packet that:

- binds the lane to the exact frozen anchor backdrop above
- authorizes only the EV/edge seam
- lists the exact `3 × 3 = 9` tuple set
- defines improvement and falsification rules
- preserves research-only scope

### Phase 2 — canonical config materialization

Create exactly two research config artifacts in the canonical optimizer zone:

- one canonical full-run YAML
- one bounded smoke YAML in the same config zone

No `src/**` or `tests/**` changes are part of this roadmap.

### Phase 3 — validator and preflight discipline

Before any run longer than smoke:

- validate the canonical YAML
- validate the smoke YAML
- run canonical preflight under canonical flags
- verify exactly two searchable parameters and exactly nine combinations
- verify that `thresholds.min_edge = 0.00` survives as an explicit serialized literal if included

### Phase 4 — bounded smoke

Run one bounded smoke using the smoke YAML and require:

- exit code `0`
- artifact completeness
- no failure markers
- non-zero trades

### Phase 5 — launch authorization

Only if phases 1–4 pass:

- create a separate launch authorization packet
- keep the lane research-only
- authorize exactly one canonical full run

### Phase 6 — full execution and closeout

Run the canonical full grid and then classify outcome as exactly one of:

- `IMPROVING`
- `PLATEAU`
- `FAIL`

That signoff must explicitly state that comparison, readiness, promotion, and writeback remain out of scope for
the same lane.

## Improvement and falsification rules

### Improvement

The Decision lane counts as improving only if at least one validated artifact:

1. strictly exceeds validation score `0.26974911658712664`, and
2. is backed by a clean research-only artifact set under the approved config and run path

### Plateau / falsification

The lane closes as `PLATEAU` if no validated artifact strictly exceeds `0.26974911658712664`.

Equality to the incumbent plateau score is still `PLATEAU`, even if the EV/edge pair differs from the anchor.

## Guardrails for the lane

- no source-code changes
- no test changes
- no objective redesign
- no runtime/default/champion changes
- no widening beyond `ev.R_default` and `thresholds.min_edge`
- no automatic slice2 if slice1 is plateau
- if `thresholds.min_edge = 0.00` is rejected or normalized away by validator, preflight, or emitted artifacts,
  stop and reopen the slice definition before launch

## Bottom line

This roadmap defines a single governed Decision continuation path:

- anchor to the latest closed plateau tuple
- open only the EV/edge seam
- move through packet → config → validator/preflight → smoke → authorization → full run → signoff

The roadmap is research-only and creates no launch authority on its own.
