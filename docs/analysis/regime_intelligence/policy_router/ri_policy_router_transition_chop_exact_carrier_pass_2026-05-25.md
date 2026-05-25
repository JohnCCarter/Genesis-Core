# RI policy router transition chop exact carrier pass

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Status: `completed / read-only exact-carrier pass / observational only`

This slice answers one bounded follow-up left open by the fixed-subject taxonomy pass:

> if `transition_chop` did not materialize on the `2023-12` vs late-`2024` carrier, does it materialize on the already-known exact selected-defensive transition pocket?

The slice stays read-only.
It uses the previously audited selected-defensive transition-window artifact only.
It does **not** rerun replay, widen the year set, change runtime behavior, or introduce a new policy identity.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/research-next-bounded-case-2026-05-25`
- **Risk:** `LOW` — exact-carrier read-only pass over an existing audited JSON artifact
- **Required Path:** `Quick`
- **Lane:** `Research-evidence`
- **Objective:** test whether the smallest repo-visible selected-defensive pocket is a valid exact carrier for the `transition_chop` state label
- **Candidate:** `transition chop exact carrier`
- **Base SHA:** `9acaecc958dce04ea039c47bc11d81c528cfb65b`

## Scope

### Scope IN

- one read-only exact-carrier helper
- one JSON artifact over the previously audited selected-defensive transition-window artifact
- one short evidence note describing whether `transition_chop` materializes on the exact carrier and fails on the nearest stable comparators

### Scope OUT

- `src/**`
- `tests/**`
- runtime routing changes
- threshold changes
- new policy identities
- replay reruns
- year widening
- readiness/promotion/runtime claims

## Evidence inputs

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_defensive_probe_exact_carrier_evidence_2026-04-29.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md`
- `results/evaluation/scpe_ri_v1_selected_defensive_transition_window_audit_2026-04-20.json`
- `results/evaluation/ri_policy_router_transition_chop_exact_carrier_pass_2026-05-25.json`
- `scripts/analyze/ri_policy_router_transition_chop_exact_carrier_pass_20260525.py`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_transition_chop_exact_carrier_pass_20260525.py --base-sha 9acaecc958dce04ea039c47bc11d81c528cfb65b`

## Main result

Yes.
On the already-known two-row selected-defensive pocket, `transition_chop` materializes cleanly as an exact carrier label.

Bounded verdict from the artifact:

- `transition_chop_materializes_on_selected_defensive_rows = true`
- `transition_chop_materializes_on_nearest_min_dwell = false`
- `transition_chop_materializes_on_nearest_threshold = false`

So the current repo-visible reading is now sharper:

> `transition_chop` does not appear on the earlier `2023-12` vs late-`2024` fixed carrier, but it **does** materialize on the tiny fresh selected-defensive transition pocket.

## Observed

### 1. The exact selected-defensive pocket satisfies the full bounded carrier check

The exact carrier rows are:

1. `2024-01-16T00:00:00`
   - `bars_since_regime_change = 1.0`
   - `transition_bucket = acute`
   - `zone = low`
   - `raw_switch_reason = transition_pressure_detected`
   - `selected_policy = RI_defensive_transition_policy`
2. `2024-01-17T12:00:00`
   - `bars_since_regime_change = 5.0`
   - `transition_bucket = recent`
   - `zone = low`
   - `raw_switch_reason = defensive_transition_state`
   - `selected_policy = RI_defensive_transition_policy`

Both rows passed every bounded exact-carrier check:

- selected policy remains defensive
- bars since regime change stays within the fresh window (`<= 5`)
- transition bucket remains `acute` or `recent`
- zone remains `low`
- raw switch reason remains transition-local

That is why the emitted exact-carrier artifact gives the pocket:

- `dominant_state_label = transition_chop`

### 2. The nearest stable comparators fail the carrier for structural reasons, not naming reasons

Nearest min-dwell comparator:

- `2025-01-28T06:00:00`
- `bars_since_regime_change = 21.0`
- `transition_bucket = stable`
- `zone = mid`
- `selected_policy = RI_no_trade_policy`

Failed checks:

- `selected_policy_is_defensive`
- `fresh_transition_window`
- `fresh_transition_bucket`
- `low_zone`

Nearest threshold-retained comparator:

- `2024-03-22T12:00:00`
- `bars_since_regime_change = 119.0`
- `transition_bucket = stable`
- `zone = low`
- `selected_policy = RI_continuation_policy`

Failed checks:

- `selected_policy_is_defensive`
- `fresh_transition_window`
- `fresh_transition_bucket`

So the rejection is structural and local:

- not fresh enough
- not in an acute/recent transition bucket
- no longer selected defensive

### 3. The exact carrier is tiny and sharply bounded in recency

Observed selected-defensive window:

- minimum recency: `1.0`
- maximum recency: `5.0`
- transition buckets: `acute = 1`, `recent = 1`
- zones: `low = 2`

Observed comparator gaps from the selected-defensive ceiling:

- nearest min-dwell floor: `21.0`
  - gap from selected-defensive ceiling: `16.0`
- nearest threshold floor: `119.0`
  - gap from selected-defensive ceiling: `114.0`

This keeps the label narrow.
It is not leaking across the wider stable defensive population.

## Inferred

The bounded repo-visible state picture is now more complete:

- `clean_continuation` materializes on the `2023-12` continuation carrier
- `aging_continuation` appears only as an embedded later segment inside that continuation carrier
- `blocked_mixed` materializes on the harmful late-`2024` carrier
- `transition_chop` materializes on the tiny fresh selected-defensive pocket

That means the missing label was not absent in principle.
It was absent on the first fixed carrier because that carrier did not contain the right structural pocket.

The best current reading is therefore:

> `transition_chop` is a small fresh-transition state carrier, not a broad stable defensive class and not a renamed policy.

## Unverified

This slice does **not** prove:

- that `transition_chop` should become a runtime state label now
- that the exact five-bar fresh window is portable outside this retained carrier
- that defensive selection alone defines the state
- that a runtime policy or threshold change is justified
- that annual performance conclusions should be widened from this tiny pocket

## What changed and what did not

What changed:

- the repo now has a reproducible exact-carrier pass that materializes `transition_chop` on a real retained carrier
- the state taxonomy now has a repo-visible carrier for the previously missing label
- the distinction between `state` and `policy` is now cleaner on the defensive-transition seam

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no new policy identity was introduced
- no replay was rerun
- no thresholds or routing logic changed
- no readiness or promotion claim was made
