# RI policy router defensive-probe exact carrier evidence

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `read-only evidence defined / concept-only / non-authorizing`

This note records one bounded read-only evidence slice for the `defensive_probe` concept line
using already-generated audited artifacts only. It does **not** run new evidence, does **not**
modify runtime/config/default surfaces, and does **not** authorize runtime follow-up.

## Scope summary

### Scope IN

- `docs/governance/ri_policy_router_defensive_probe_exact_carrier_evidence_2026-04-29.md`
- `GENESIS_WORKING_CONTRACT.md`
- existing audited artifacts only

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `results/**` writes
- `artifacts/**`
- new replay or backtest execution
- more years or wider window sweeps
- runtime/default/config/family/readiness/promotion surfaces

## Evidence used

- `docs/governance/ri_policy_router_defensive_probe_concept_precode_packet_2026-04-29.md`
- `docs/governance/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md`
- `docs/governance/scpe_ri_v1_defensive_scarcity_audit_report_2026-04-20.md`
- `results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json`
- `results/evaluation/scpe_ri_v1_defensive_scarcity_audit_2026-04-20.json`
- `results/research/scpe_v1_ri/routing_trace.ndjson`

## Exact carrier chosen

The smallest honest repo-visible carrier is the two-row observed selected-defensive pocket on
the frozen baseline replay surface:

1. `2024-01-16T00:00:00`
   - `raw_switch_reason = transition_pressure_detected`
   - `bars_since_regime_change = 1.0`
   - `transition_bucket = acute`
   - `zone = low`
   - `selected_policy = RI_defensive_transition_policy`
   - `final_routed_action = NONE`
   - `veto_reason = state_below_veto_floor`
2. `2024-01-17T12:00:00`
   - `raw_switch_reason = defensive_transition_state`
   - `bars_since_regime_change = 5.0`
   - `transition_bucket = recent`
   - `zone = low`
   - `selected_policy = RI_defensive_transition_policy`
   - `final_routed_action = LONG`
   - `veto_reason = defensive_transition_cap`

The key bounded fact is simple: on the frozen baseline surface, the only selected-defensive row
whose raw reason is `defensive_transition_state` is the `2024-01-17T12:00:00` row above.

## Comparator boundary

Nearest retained `RI_no_trade_policy` comparator from the same raw defensive population:

- `2025-01-28T06:00:00`
  - `raw_switch_reason = defensive_transition_state`
  - `bars_since_regime_change = 21.0`
  - `transition_bucket = stable`
  - `zone = mid`
  - `selected_policy = RI_no_trade_policy`
  - `switch_reason = switch_blocked_by_min_dwell`
  - `veto_reason = policy_no_trade`

Nearest threshold-retained continuation comparator:

- `2024-03-22T12:00:00`
  - `raw_switch_reason = defensive_transition_state`
  - `bars_since_regime_change = 119.0`
  - `transition_bucket = stable`
  - `zone = low`
  - `selected_policy = RI_continuation_policy`
  - `switch_reason = confidence_below_threshold`
  - `veto_reason = no_veto`

## Descriptive result

- The lone baseline `defensive_transition_state` row that actually reaches selected defensive does
  **not** sit inside a broad stable defensive class.
- It sits inside the same tiny fresh low-zone pocket as the stronger
  `transition_pressure_detected` row.
- The selected-defensive ceiling for this pocket is `5.0` bars since regime change.
- The nearest retained no-trade comparator begins at `21.0` bars, already outside that pocket.
- The nearest threshold-retained continuation comparator begins at `119.0` bars, far outside the
  same pocket.

## Bounded verdict

Current repo-visible evidence supports this bounded reading only:

1. the smallest honest `defensive_probe` carrier is the two-row selected-defensive pocket around
   `2024-01-16T00:00:00 .. 2024-01-17T12:00:00`
2. within that pocket, the `defensive_transition_state` member reads as the weaker edge row beside
   the stronger `transition_pressure_detected` row, not as a separate broad personality
3. this is enough to preserve a concept-only bounded carrier, but **not** enough to justify
   runtime/default/config follow-up or a wider annual reinterpretation

## What this note does not authorize

- claiming `defensive_probe` is already implemented
- treating `defensive_transition_state` as a new runtime personality
- opening a runtime/config packet from this note alone
- widening back into more years, more windows, or fresh execution
- promotion, readiness, or family-rule claims

## Bottom line

The exact carrier exists, but it is tiny: one two-row fresh low-zone pocket, with only one
baseline `defensive_transition_state` member. On current repo-visible evidence, that keeps
`defensive_probe` concept-only and local rather than proving a distinct runtime personality.
