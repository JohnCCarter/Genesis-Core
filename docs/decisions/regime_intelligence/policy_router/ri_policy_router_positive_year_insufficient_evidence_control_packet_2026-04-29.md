# RI policy router positive-year insufficient-evidence control packet

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / read-only control slice / no behavior change`

Relevant skills: `decision_gate_debug`, `python_engineering`

Skill coverage for this slice is explicit and bounded:

- `decision_gate_debug` governs the exact mechanism separation between `insufficient_evidence`, `stable_continuation_state` displacement, and local suppressive context.
- `python_engineering` governs the helper wrapper structure, minimal-diff implementation, and focused validation.

Lite checks for this slice are explicit:

- wrapper import/materialization smoke on the fixed 2025 subject
- generated artifact row-lock/schema check against the fixed seven timestamps
- March 2021 parity check only if the completed March 2021 helper must be touched for import/runtime reasons

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads one fixed positive-year action-diff file plus curated candles only, emits one bounded JSON artifact plus one analysis note, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the fixed negative-year March 2021 slice is complete, and the next honest question is whether the same `insufficient_evidence` framing behaves differently on a positive annual control before any policy speculation.
- **Objective:** materialize one exact positive-year `insufficient_evidence` local window with the same target-versus-displacement framing used in the March 2021 negative-year slice so selectivity can be tested locally.
- **Candidate:** `2025-03-14 positive-year insufficient-evidence control window`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`

## Exact proposed subject

### Exact positive-year `insufficient_evidence` target cluster

Positive full year: `2025`

Blocked `insufficient_evidence` rows grouped by `<=24h` adjacency:

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

Shared preflight context already verified:

- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `65`

### Exact displacement comparison rows

Nearby true `stable_continuation_state` displacement rows inside the same local envelope:

- `2025-03-13T15:00:00+00:00`
- `2025-03-14T00:00:00+00:00`

Shared preflight comparison context already verified:

- absent action = `NONE`
- enabled action = `LONG`
- switch reason = `stable_continuation_state`
- selected policy = `RI_continuation_policy`
- bars since regime change = `63..64`

The nearby `2025-03-13T21:00:00+00:00` and `2025-03-14T06:00:00+00:00` `stable_continuation_state` rows remain local context only because their action pair is `LONG -> NONE`, not the displacement shape `NONE -> LONG`.

### Exact output paths to materialize

- JSON artifact: `results/evaluation/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_packet_2026-04-29.md`
  - `scripts/analyze/ri_policy_router_positive_year_insufficient_evidence_control_20260429.py`
  - `results/evaluation/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`
  - optional refresh of `GENESIS_WORKING_CONTRACT.md` only if the new control slice materially changes the next admissible step
- **Scope OUT:**
  - no runtime/config/schema/authority/default changes
  - no new backtest reruns
  - if the exact named `2025-03-14..2025-03-16` target rows or the two exact `2025-03-13/2025-03-14` comparison rows cannot be materialized from the existing `2025_enabled_vs_absent_action_diffs.json` rows or matching curated candle timestamps, stop and refresh the packet rather than widen the window
  - no edits to the completed March 2021 helper unless strictly required to resolve import/runtime issues in the new wrapper
  - no promotion/readiness/champion claims
- **Expected changed files:** 4-5
- **Max files touched:** 5

## Evidence anchors

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

## Planned method

1. add one read-only helper wrapper for the exact positive-year control subject using the same local-window framing as the completed March 2021 negative-year slice
2. keep the `insufficient_evidence` target rows, true `stable_continuation_state` displacement rows, and remaining local rows as separate labeled cohorts in the emitted artifact
3. summarize whether the positive-year control shows locally justified `insufficient_evidence` suppression where the negative-year March 2021 slice showed locally favorable blocked rows
4. keep all conclusions descriptive and comparison-only; no runtime follow-up is authorized from this slice alone

## Validation requirements

- `get_errors` on the new packet/script/analysis note and any touched helper/contract file
- wrapper import/materialization smoke on the fixed 2025 subject
- generated artifact row-lock/schema check proving all seven fixed timestamps are echoed exactly and that the two `LONG -> NONE` stable rows remain context-only
- exact helper execution against the fixed 2025 control subject
- `ruff check` on the new helper wrapper and any touched Python file
- `pre-commit run --files` on the touched files
- manual diff review confirming no runtime/config/default/authority drift

## Stop conditions

- the fixed 2025 control window cannot be materialized from the existing action-diff/candle evidence
- the wrapper starts to require new reusable logic outside the already-existing March 2021 helper surface
- the slice starts implying runtime tuning or promotion authority
- scope drifts into multi-window annual re-analysis instead of one fixed local control

## Output required

- one deterministic JSON summary artifact at `results/evaluation/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.json`
- one human-readable analysis note at `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md` stating what the control does and does not justify for the robust-policy question
- exact command run and validation outcomes
