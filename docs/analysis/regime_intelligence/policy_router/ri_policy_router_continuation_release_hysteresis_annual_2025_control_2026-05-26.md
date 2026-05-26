# RI policy router continuation_release_hysteresis annual 2025 control

Date: 2026-05-26
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Status: `completed / read-only annual control / observational only`

This slice extends the same seam question from the fixed annual `2024` surface to a positive-year full-year control.

The question is deliberately narrow:

> on the fixed `2025` full-year same-stack surface, does `continuation_release_hysteresis` contribute positively, negatively, or only through compensated row changes when baseline is compared against `release_zero`?

This slice does **not**:

- reopen runtime tuning
- widen into a fresh year-by-year hunt
- claim that one exact month can stand in for the whole year
- weaken the standing warning that the policy can also harm a broadly good year such as `2024`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/research-next-bounded-case-2026-05-25`
- **Risk:** `LOW`
- **Required Path:** `Quick`
- **Lane:** `Research-evidence`
- **Objective:** test whether the continuation-release hysteresis seam has a directional annual contribution on the fixed positive-year `2025` control surface
- **Candidate:** `continuation_release_hysteresis annual 2025 control`
- **Base SHA:** `b5fb83191f17a836c57a6276ba5b4decedba9cc4`

## Evidence inputs

- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2025_control_20260526.py`
- `results/evaluation/ri_policy_router_continuation_release_hysteresis_annual_2025_control_2026-05-26.json`
- `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`

Context only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_annual_2024_contribution_2026-05-26.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_issue_104_evidence_first_comparison_2026-05-26.md`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m black scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2025_control_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2025_control_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2025_control_20260526.py`

## Main result

The annual `2025` control is top-line flat between baseline and `release_zero`.

Observed topline deltas:

- `total_return_diff = 0.0`
- `final_capital_diff = 0.0`
- `profit_factor_diff = 0.0`
- `max_drawdown_pct_diff = 0.0`
- `num_trades_diff = 0.0`
- `net_position_pnl_diff = 0.0`

So the seam does **not** produce a directional annual edge on the fixed `2025` full-year same-stack surface.

## Observed

### 1. The seam changes many annual rows, but only parametrically

Annual row-diff inventory:

- `all_row_diff_count = 2790`
- `action_diff_count = 0`
- `behavioral_row_diff_count = 0`
- `reason_only_diff_count = 2790`
- `parameter_only_diff_count = 2790`

That means the seam still touches many rows on the annual surface, but only inside parameter/debug state rather than action or behavior.

### 2. `continuation_release` never appears on the annual `2025` control surface

Observed continuation-release counts:

- baseline `continuation_release_row_count = 0`
- `release_zero` `continuation_release_row_count = 0`
- `continuation_release_diff_count = 0`

So this is stronger than a merely flat annual result.
The seam does not just fail to move the top line.
It never even enters `continuation_release` on this fixed annual `2025` surface.

### 3. Baseline and release-zero performance summaries are identical

Baseline annual summary:

- `final_capital = 10292.686600`
- `total_return = 2.926866%`
- `profit_factor = 2.189868`
- `max_drawdown = 2.622936%`
- `num_trades = 100`

`release_zero` annual summary matches those same topline values exactly on the observed surface.

## Inferred

The seam still does not graduate into a broad annual explanation.

Combined with the already-landed annual `2024` read, the bounded annual evidence now says:

- annual `2024`: top-line flat, action-neutral, seam not a broad annual-harm explanation
- annual `2025`: top-line flat, action-neutral, and no `continuation_release` entry at all

That is a stronger negative result than “the seam sometimes helps and sometimes hurts.”
On these two fixed annual same-stack surfaces, the seam is not carrying the broad annual story.

This keeps the user’s warning intact:

> think about the fact that the policy also made good years worse, such as `2024`.

The new `2025` control does not undo that warning.
It just says the continuation-release hysteresis seam is not the right broad annual explanation for it.

## Unverified

This slice does **not** prove:

- that the seam is irrelevant on every exact-month or local-window surface
- that monthly positives such as exact `2025-10` can be annualized safely
- that another local carrier state cannot still explain a smaller pocket
- that runtime tuning is justified

## Consequence

The honest next step after this control is not “search more annual years until something wins.”
It is to compare the exact-month positive read against the annual path and ask whether the local month is anchor-sensitive.

That is the bounded question this control leaves behind.

## Verification

- `black` on `scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2025_control_20260526.py` -> pass
- `ruff check` on `scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2025_control_20260526.py` -> pass
- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2025_control_20260526.py` -> emitted artifact with status `annual_2025_topline_mixed_or_flat_between_baseline_and_release_zero`

## What changed and what did not

What changed:

- one new read-only helper now materializes the annual `2025` same-stack control for the seam
- one new evaluation artifact now records the annual comparison and row-diff inventory
- the seam evidence chain now includes a positive-year annual control, not only the annual `2024` harmful-year surface

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no annual screening universe was widened beyond this fixed `2025` control
- no policy threshold was retuned
- no readiness or promotion claim was made
