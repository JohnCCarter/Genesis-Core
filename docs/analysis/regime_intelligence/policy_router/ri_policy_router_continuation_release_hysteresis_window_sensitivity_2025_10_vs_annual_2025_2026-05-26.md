# RI policy router continuation_release_hysteresis window sensitivity 2025-10 vs annual 2025

Date: 2026-05-26
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Status: `completed / read-only window-sensitivity probe / observational only`

This slice follows directly from the annual `2025` control.

The annual control said the seam is flat on the full-year `2025` same-stack surface.
But the earlier exact `2025-10` local read still showed a positive seam delta.

So the bounded question becomes:

> is exact `2025-10` actually the same observed surface as October reached through the full-year `2025` path, or is the October seam footprint anchor-sensitive?

This slice does **not**:

- reopen runtime tuning
- convert exact-month evidence into an annual claim
- weaken the standing warning that the policy can still damage good years such as `2024`
- claim a portable calendar-month law

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/research-next-bounded-case-2026-05-25`
- **Risk:** `LOW`
- **Required Path:** `Quick`
- **Lane:** `Research-evidence`
- **Objective:** compare exact `2025-10` against October embedded inside the full-year `2025` path under both baseline and `release_zero`
- **Candidate:** `continuation_release_hysteresis window sensitivity 2025-10 vs annual 2025`
- **Base SHA:** `67ae999293336ed30020babef85576a4f69f6f89`

## Evidence inputs

- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_20260526.py`
- `results/evaluation/ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_2026-05-26.json`
- `results/evaluation/ri_policy_router_continuation_release_hysteresis_annual_2025_control_2026-05-26.json`
- `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`

Context only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_annual_2025_control_2026-05-26.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_annual_2024_contribution_2026-05-26.md`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m black scripts/analyze/ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_20260526.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_20260526.py`

## Main result

The exact `2025-10` subject is **not** equivalent to October as reached through the full-year `2025` path.

Topline contrast:

- exact `2025-10` seam delta: `exact_total_return_diff = 0.171348`
- annual `2025` seam delta: `annual_total_return_diff = 0.0`

Artifact status:

- `exact_october_vs_embedded_october_window_sensitivity_detected`

So the local October seam signal is anchor- or carry-in-sensitive.
It is not a simple property of calendar rows viewed in isolation.

## Observed

### 1. The first union diff starts at the month boundary, but the first shared observed diff starts later

Union-level first diff timestamps:

- baseline first union row diff: `2025-10-01T00:00:00+00:00`
- `release_zero` first union row diff: `2025-10-01T00:00:00+00:00`

Shared observed-window first diff timestamps:

- baseline first shared row diff: `2025-10-16T00:00:00+00:00`
- `release_zero` first shared row diff: `2025-10-16T00:00:00+00:00`

That matters because it separates trivial path-entry differences from true divergence on timestamps both paths actually observe.

### 2. Shared October rows still diverge heavily even after warmup and unmatched-row effects are excluded

Shared-window counts:

- baseline `shared_row_diff_count = 121`
- baseline `shared_action_diff_count = 24`
- baseline `shared_behavioral_row_diff_count = 121`
- baseline `shared_continuation_release_presence_diff_count = 13`

- `release_zero` `shared_row_diff_count = 121`
- `release_zero` `shared_action_diff_count = 24`
- `release_zero` `shared_behavioral_row_diff_count = 121`
- `release_zero` `shared_continuation_release_presence_diff_count = 10`

So the window difference is not just a warmup artifact.
The shared October surface itself diverges materially.

### 3. `continuation_release` exists in exact October but disappears when October is reached through the annual path

Continuation-release counts:

- baseline exact October `continuation_release` rows: `13`
- baseline annual-embedded October `continuation_release` rows: `0`
- `release_zero` exact October `continuation_release` rows: `10`
- `release_zero` annual-embedded October `continuation_release` rows: `0`

That is the most direct mechanism-level difference in the slice.
The seam-relevant local state exists on the exact month path and vanishes on the annual-embedded path.

### 4. The annual path remains flat even while the exact month shows a local seam delta

Annual surface read:

- baseline annual `total_return = 2.926866%`
- `release_zero` annual `total_return = 2.926866%`
- annual seam delta stays `0.0`

Exact-month read:

- exact `2025-10` seam delta remains positive on this observed surface

So exact-month evidence and annual evidence are not answering the same question.

## Inferred

The contradiction is now resolved cleanly.

The earlier local `2025-10` positive read does **not** mean the seam contributes to the full-year `2025` surface.
It means the exact month and the month embedded inside the annual carry-in path are different state paths.

That is the bounded reading:

- annual `2025` is flat because the seam-relevant local state never materializes there
- exact `2025-10` can still show a positive local seam delta because it begins from a different anchor/carry-in state

So the seam remains the wrong object for a broad annual explanation.
The right conclusion is not “October proves the seam matters annually.”
It is “October proves the local month is path-sensitive.”

## Unverified

This slice does **not** prove:

- that every exact month is anchor-sensitive in the same way
- that the exact `2025-10` local gain is portable or generalizable
- that the seam never matters on any local surface
- that runtime tuning is justified

## Consequence

This slice closes the seam contradiction instead of reopening the year/month search.

The honest next move is therefore not “scan more years and months.”
It is to pivot away from the seam as the broad annual-harm explanation and continue on the non-seam leaf-level root-cause surface.

That keeps the `2024` warning explicit and prevents exact-month positives from being over-read as annual truth.

## Verification

- `black` on `scripts/analyze/ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_20260526.py` -> pass
- `ruff check` on `scripts/analyze/ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_20260526.py` -> pass
- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_window_sensitivity_2025_10_vs_annual_2025_20260526.py` -> emitted artifact with status `exact_october_vs_embedded_october_window_sensitivity_detected`

## What changed and what did not

What changed:

- one new read-only helper now compares exact October against annual-embedded October on the same carrier
- one new evaluation artifact now records union vs shared-row divergence and continuation-release presence differences
- the seam evidence chain now has a bounded explanation for why exact `2025-10` and annual `2025` can disagree without contradiction

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no seam parameter was retuned
- no portable monthly rule was claimed
- no readiness or promotion claim was made
