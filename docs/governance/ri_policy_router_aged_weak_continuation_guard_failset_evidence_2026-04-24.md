# RI policy router aged weak continuation guard fail-set evidence

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / fail-set evidence only / negative result`

## Scope summary

This slice ran the first bounded evidence pass for the implemented `aged weak continuation guard` candidate.

### Scope IN

- paired fail-set backtests on the same `3h` runtime bridge subject
- decision-row capture for baseline vs guarded candidate
- bounded delta analysis against both:
  - baseline bridge
  - prior router-enabled December artifact

### Scope OUT

- keep-set verification (`2024`, `2025`)
- stress-set verification (`2018`, `2020 H1`)
- further runtime edits
- config/authority changes
- candidate-promotion claims

## Exact commands run

Canonical env for all runs:

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`

### Fail B: December full local-failure window

Baseline:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-31 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_policy_router_aged_weak_continuation_guard_20260424/fail_b_2023_dec_baseline_decision_rows.ndjson --decision-rows-format ndjson`

Candidate:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-31 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_aged_weak_continuation_guard_20260424.json --decision-rows-out results/backtests/ri_policy_router_aged_weak_continuation_guard_20260424/fail_b_2023_dec_candidate_decision_rows.ndjson --decision-rows-format ndjson`

### Fail A: December micro-window anchor

Baseline:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-24 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_policy_router_aged_weak_continuation_guard_20260424/fail_a_2023_dec_micro_baseline_decision_rows.ndjson --decision-rows-format ndjson`

Candidate:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-24 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_aged_weak_continuation_guard_20260424.json --decision-rows-out results/backtests/ri_policy_router_aged_weak_continuation_guard_20260424/fail_a_2023_dec_micro_candidate_decision_rows.ndjson --decision-rows-format ndjson`

## Outcomes

### Fail B summary (`2023-12-01 -> 2023-12-31`)

- baseline return: `-0.10%`
- candidate return: `-0.35%`
- baseline trades: `15`
- candidate trades: `13`
- baseline Sharpe: `0.069`
- candidate Sharpe: `-0.180`
- baseline max drawdown: `0.25%`
- candidate max drawdown: `0.46%`
- verdict: **worse**

### Fail A summary (`2023-12-01 -> 2023-12-24`)

- baseline return: `-0.03%`
- candidate return: `-0.11%`
- baseline trades: `8`
- candidate trades: `7`
- baseline Sharpe: `0.117`
- candidate Sharpe: `-0.061`
- baseline max drawdown: `0.25%`
- candidate max drawdown: `0.25%`
- verdict: **worse**

## Decision-row findings

### The guard did not hit the intended late-December seam

The previously localized target seam remained unchanged in the new candidate runs:

- `2023-12-20T03:00:00+00:00`
  - baseline: `ENTRY_LONG`
  - candidate: `RESEARCH_POLICY_ROUTER_NO_TRADE`
- `2023-12-22T15:00:00+00:00`
  - baseline: `COOLDOWN_ACTIVE`
  - candidate: `RESEARCH_POLICY_ROUTER_CONTINUATION;ENTRY_LONG`
- `2023-12-24T21:00:00+00:00`
  - baseline: `COOLDOWN_ACTIVE`
  - candidate: `RESEARCH_POLICY_ROUTER_CONTINUATION;ENTRY_LONG`

That means the guard did **not** remove the two known late continuation losers that motivated the slice.

### Guard-only delta vs previous router-enabled December artifact

Comparing the new guarded candidate to the prior router-enabled December artifact showed only `6` changed rows.

The meaningful route-admission deltas were:

- `2023-12-28T06:00:00+00:00`
  - old router-enabled: `RESEARCH_POLICY_ROUTER_CONTINUATION;ENTRY_LONG`
  - new candidate: `RESEARCH_POLICY_ROUTER_NO_TRADE`
- `2023-12-30T18:00:00+00:00`
  - old router-enabled: `RESEARCH_POLICY_ROUTER_CONTINUATION;ENTRY_LONG`
  - new candidate: `RESEARCH_POLICY_ROUTER_NO_TRADE`

The remaining changed rows were downstream cooldown/no-trade propagation around those two blocked entries.

### Seam diagnosis from read-only router replay

A bounded read-only replay against the current guarded candidate confirms that the intended target rows do not share the same router-local shape as the rows the guard actually blocks.

#### `2023-12-20T03:00:00+00:00` is not a guard hit

This row was already `RESEARCH_POLICY_ROUTER_NO_TRADE` in the prior router-enabled December artifact.

Observed router-local state on the guarded replay:

- `bars_since_regime_change = 7`
- `confidence_gate = 0.5060`
- `action_edge = 0.0121`
- `switch_reason = insufficient_evidence`
- `raw_target_policy = RI_no_trade_policy`

So this bar is outside the `aged weak continuation` seam entirely; it is an evidence-floor no-trade.

#### `2023-12-22T15:00:00+00:00` is weak continuation, but not aged

Observed router-local state:

- `bars_since_regime_change = 7`
- `confidence_gate = 0.5411`
- `action_edge = 0.0823`
- `switch_reason = continuation_state_supported`
- `mandate_level = 2`
- `previous_policy = RI_no_trade_policy`

This is exactly the weak-continuation shape the guard intends to veto, but it is still far below the current age gate of `16` bars.

#### `2023-12-24T21:00:00+00:00` is already strong continuation

Observed router-local state:

- `bars_since_regime_change = 13`
- `confidence_gate = 0.5579`
- `action_edge = 0.1157`
- `switch_reason = stable_continuation_state`
- `mandate_level = 3`
- `previous_policy = RI_continuation_policy`
- `switch_proposed = false`

This row is not weak continuation at all. It is already in stable continuation, so the current weak-continuation guard cannot intercept it even if the age threshold is lowered.

#### Rows the guard actually blocks

The two meaningful guard-hit rows were:

- `2023-12-28T06:00:00+00:00`
  - `bars_since_regime_change = 19`
  - `confidence_gate = 0.5335`
  - `action_edge = 0.0669`
  - `switch_reason = AGED_WEAK_CONTINUATION_GUARD`
- `2023-12-30T18:00:00+00:00`
  - `bars_since_regime_change = 22`
  - `confidence_gate = 0.5271`
  - `action_edge = 0.0541`
  - `switch_reason = AGED_WEAK_CONTINUATION_GUARD`

These rows match the implemented guard almost perfectly: late in regime age, below strong confidence, and below strong edge.

#### Bounded inference

The intended late-December losing seam is heterogeneous:

- one target row is `weak continuation but not aged enough` (`2023-12-22T15:00:00+00:00`)
- one target row is `already strong continuation` (`2023-12-24T21:00:00+00:00`)

The current candidate only targets `aged + weak continuation`, so it is structurally incapable of removing both target rows.

## Conclusion

The first implemented `aged weak continuation guard` is a **negative fail-set result**.

Bounded interpretation:

- it does change the enabled router path,
- but it does **not** hit the intended late-December substitution seam,
- and it worsens both the local December fail window and the micro-window anchor.

Therefore the candidate should **not** advance to keep-set verification in its current form.

More precise statement after the seam replay:

- the guard is not merely miscalibrated,
- it is also mismatched to the observed target seam,
- because the two intended losing rows do not share the same router-local predicate.

## Next admissible step

The next honest step is **not** `2024/2025` verification yet.

It is a new bounded analysis/refinement slice that explains why the target losing continuation entries on:

- `2023-12-22T15:00:00+00:00`
- `2023-12-24T21:00:00+00:00`

remain untouched while the guard only suppresses later bars around:

- `2023-12-28T06:00:00+00:00`
- `2023-12-30T18:00:00+00:00`

Any next candidate should stay continuation-local and explicitly justify why it will hit the intended seam before broader evidence runs are reopened.

At minimum, any next candidate packet should state whether it is trying to address:

- weak continuation before the current `16`-bar age threshold,
- already-strong continuation,
- or only one of those seams at a time.
