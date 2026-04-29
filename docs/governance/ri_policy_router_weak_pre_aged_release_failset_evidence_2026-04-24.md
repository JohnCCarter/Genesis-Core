# RI policy router weak pre-aged release fail-set evidence

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / fail-set evidence only / negative result`

## Scope summary

This slice ran the first bounded fail-set evidence pass for the implemented
`weak pre-aged continuation release guard` candidate.

### Scope IN

- paired fail-set backtests on the same `3h` runtime bridge subject
- decision-row capture for baseline vs seam-A candidate
- bounded row-level comparison focused on the intended seam-A target and the
  surrounding December substitution window

### Scope OUT

- keep-set verification (`2024`, `2025`)
- stress-set verification (`2018`, `2020 H1`)
- further runtime edits
- config/authority changes
- candidate-promotion claims

## Canonical env for all runs

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`

## Exact commands run

### Fail B: December full local-failure window

Baseline:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-31 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_policy_router_weak_pre_aged_release_guard_20260424/fail_b_2023_dec_baseline_decision_rows.ndjson --decision-rows-format ndjson`

Candidate:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-31 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json --decision-rows-out results/backtests/ri_policy_router_weak_pre_aged_release_guard_20260424/fail_b_2023_dec_candidate_decision_rows.ndjson --decision-rows-format ndjson`

### Fail A: December micro-window anchor

Baseline:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-24 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_policy_router_weak_pre_aged_release_guard_20260424/fail_a_2023_dec_micro_baseline_decision_rows.ndjson --decision-rows-format ndjson`

Candidate:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-24 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json --decision-rows-out results/backtests/ri_policy_router_weak_pre_aged_release_guard_20260424/fail_a_2023_dec_micro_candidate_decision_rows.ndjson --decision-rows-format ndjson`

## Outcomes

### Fail B summary (`2023-12-01 -> 2023-12-31`)

- baseline return: `-0.10%`
- candidate return: `-0.21%`
- baseline trades: `15`
- candidate trades: `12`
- baseline Sharpe: `0.069`
- candidate Sharpe: `-0.072`
- baseline max drawdown: `0.25%`
- candidate max drawdown: `0.32%`
- baseline profit factor: `1.38`
- candidate profit factor: `0.85`
- baseline score: `0.1057`
- candidate score: `-100.0839`
- verdict: **worse**

### Fail A summary (`2023-12-01 -> 2023-12-24`)

- baseline return: `-0.03%`
- candidate return: `-0.07%`
- baseline trades: `8`
- candidate trades: `7`
- baseline Sharpe: `0.117`
- candidate Sharpe: `0.008`
- baseline max drawdown: `0.25%`
- candidate max drawdown: `0.25%`
- baseline profit factor: `1.49`
- candidate profit factor: `1.08`
- baseline score: `-99.8385`
- candidate score: `-99.9795`
- verdict: **worse**

## Decision-row findings

### The intended seam-A target is hit

At the intended seam-A target `2023-12-22T15:00:00+00:00`:

- baseline: `NONE` with `COOLDOWN_ACTIVE`
- candidate: `NONE` with `RESEARCH_POLICY_ROUTER_NO_TRADE`

This means the new release guard does hit the targeted weak pre-aged release seam.

### Seam B remains untouched

At `2023-12-24T21:00:00+00:00`:

- baseline: `NONE` with `COOLDOWN_ACTIVE`
- candidate: `LONG` with `RESEARCH_POLICY_ROUTER_CONTINUATION;ENTRY_LONG`

So the already-strong continuation seam remains out of scope and unchanged in the
sense that seam-A does not solve it.

### The candidate broadens action churn beyond the intended seam

Action-level drift was materially broader than one isolated seam-A correction.

#### Full fail window (`Fail B`)

- action diff count: `34`
- size diff count: `0`
- reason-only diff count: `18`

Representative blocked baseline longs:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`
- `2023-12-22T18:00:00+00:00`

Representative replacement continuation entries admitted later:

- `2023-12-23T00:00:00+00:00`
- `2023-12-23T09:00:00+00:00`
- `2023-12-23T18:00:00+00:00`
- `2023-12-24T03:00:00+00:00`
- `2023-12-24T21:00:00+00:00`
- `2023-12-25T06:00:00+00:00`
- `2023-12-25T15:00:00+00:00`

#### Micro fail window (`Fail A`)

- action diff count: `10`
- size diff count: `0`
- reason-only diff count: `14`

Representative pattern:

- earlier baseline longs are suppressed on `2023-12-20`, `2023-12-21`, and `2023-12-22`
- replacement continuation entries then appear around `2023-12-23`

## Bounded interpretation

The seam-A candidate is **not** a pure local improvement even though it blocks the
intended `2023-12-22 15:00` seam.

It does two things at once:

1. blocks the targeted weak pre-aged release path
2. broadens December action churn by suppressing additional earlier longs and then
   admitting later continuation entries anyway

That trade-off is unfavorable on both fail-set windows.

## Conclusion

The implemented `weak pre-aged continuation release guard` is a **negative fail-set
result**.

More precise statement:

- it hits the intended seam-A target,
- but it worsens both fail-set windows,
- and it does so while introducing materially broader action churn than the intended
  one-row seam correction.

Therefore the candidate should **not** advance to keep-set or stress-set verification
in its current form.

## Next admissible step

The next honest step is **not** `2024/2025` or stress-set replay.

It is a new bounded analysis/refinement slice that explains why blocking the intended
weak pre-aged release seam still worsens the December windows through broader churn
across the `2023-12-21 -> 2023-12-25` pocket.

That next slice should stay explicit about two separate facts:

- seam A (`2023-12-22 15:00`) is now reachable and blockable
- seam B (`2023-12-24 21:00`) still remains outside the solved surface
