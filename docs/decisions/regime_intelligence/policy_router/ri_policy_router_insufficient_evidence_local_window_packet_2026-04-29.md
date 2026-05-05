# RI policy router insufficient-evidence local window packet

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / read-only evidence slice / no behavior change`

Relevant skills: `decision_gate_debug`, `python_engineering`

Skill coverage for this slice is explicit and bounded:

- `decision_gate_debug` governs the gate-oriented reading and mechanism separation.
- `python_engineering` governs the helper script structure, focused validation, and any test-only reusable logic.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads existing action-diff JSONs and curated candles only, emits one bounded summary artifact plus one analysis note, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the annual blocker split already says `insufficient_evidence` is the sharper suppressor suspect, so the next honest step is to test one exact local carrier window before any runtime framing is considered.
- **Objective:** localize one exact negative-year `insufficient_evidence` carrier window inside the blocked low-zone bars-`8+` cohort and compare it against nearby `stable_continuation_state` displacement rows so suppression and displacement do not get mixed again.
- **Candidate:** `2021-03-26 insufficient-evidence local window`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`

## Exact proposed subject

### Exact `insufficient_evidence` carrier cluster

Negative year: `2021`

Blocked `insufficient_evidence` rows grouped by `<=24h` adjacency:

- `2021-03-26T12:00:00+00:00`
- `2021-03-27T06:00:00+00:00`
- `2021-03-27T15:00:00+00:00`
- `2021-03-28T00:00:00+00:00`

Shared context already verified in preflight inspection:

- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- bars since regime change = `71..72`
- selected policy = `RI_no_trade_policy`

### Nearby displacement rows to compare locally

Nearby `stable_continuation_state` rows inside the same local envelope:

- `2021-03-26T15:00:00+00:00`
- `2021-03-29T00:00:00+00:00`

These rows are intentionally comparison-only and must not be treated as the same mechanism as the `insufficient_evidence` cluster.
The nearby `2021-03-26T21:00:00+00:00` `stable_continuation_state` row remains local context only because its action pair is `LONG -> NONE`, not the displacement shape `NONE -> LONG`.

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_packet_2026-04-29.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_local_window_20260429.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_local_window_2026-04-29.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
  - one focused unit test for the helper's local-window grouping or comparison selection if new reusable logic is introduced
- **Scope OUT:**
  - no runtime/config/schema/authority/default changes
  - no new backtest reruns
  - no widening to additional years or new local windows unless the exact named `2021-03-26..2021-03-28` `insufficient_evidence` subject cannot be materialized from the existing `2021_enabled_vs_absent_action_diffs.json` rows or matching curated candle timestamps
  - no promotion/readiness/champion claims
  - no edits to `GENESIS_WORKING_CONTRACT.md` unless the slice changes the next admissible step materially
- **Expected changed files:** 4-5
- **Max files touched:** 5

## Evidence anchors

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_active_carrier_truth_parked_handoff_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2021_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

## Planned method

1. use one read-only helper to materialize the exact local window around the fixed 2021 `insufficient_evidence` cluster
2. join the fixed timestamps against curated `3h` candles for descriptive `fwd_4`, `fwd_8`, `fwd_16`, `mfe_16`, and `mae_16` proxies only
3. keep `insufficient_evidence` rows and nearby `stable_continuation_state` rows as separate labeled cohorts in the emitted artifact
4. summarize whether the local picture supports `insufficient_evidence` as a candidate over-binding seam rather than just continuation displacement packaging

## Validation requirements

- `get_errors` on the new packet/script/analysis note/test file
- targeted test for any new reusable helper logic if introduced
- exact helper execution against the fixed subject
- `ruff check` on the new script and test file
- `pre-commit run --files` on the touched files
- manual diff review confirming no runtime/config/default/authority drift

## Stop conditions

- the fixed 2021 window cannot be materialized from the existing action-diff/candle evidence
- the slice starts to depend on runtime imports from `src/**`
- the slice needs more than one negative-year window to make its point
- the analysis starts implying runtime tuning or promotion authority
- scope drifts into broad annual re-analysis or new backtest reruns

## Output required

- one deterministic JSON summary artifact for the fixed local window
- one human-readable analysis note stating what the local window does and does not justify
- exact command run and validation outcomes
