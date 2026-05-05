# RI policy router 2024 regression pocket isolation packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / read-only fixed-pocket evidence slice / no behavior change`

Relevant skills: `decision_gate_debug`, `python_engineering`

Skill coverage for this slice is explicit and bounded:

- `decision_gate_debug` governs the separation between blocked target rows, true `stable_continuation_state` displacement, and context-only stable rows inside the selected 2024 pocket.
- `python_engineering` governs the bounded helper shape, any focused pure-helper test, and minimal-diff validation.
- Implementation for the read-only helper and any focused tests in this slice uses the repository `python_engineering` skill.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads one fixed 2024 annual action-diff JSON plus curated candles only, emits one bounded JSON artifact plus one analysis note, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest genuinely new lane now: the March 2021/March 2025 four-cohort artifact loop is exhausted, so the next honest step is one new exact 2024 regression pocket already inside the documented blocked-baseline / later-`stable_continuation_state` family.
- **Objective:** materialize one exact 2024 late low-zone regression pocket that contains the mixed `AGED_WEAK_CONTINUATION_GUARD` / `insufficient_evidence` blocked target cluster plus its nearby true `stable_continuation_state` displacement row and nearby context-only stable blocked row.
- **Candidate:** `2024-11-28 regression pocket isolation`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`

## Exact proposed subject

### Exact 2024 target cluster

Fixed target rows (`9`) inside the selected 2024 regression pocket:

- `2024-11-28T15:00:00+00:00`
- `2024-11-29T00:00:00+00:00`
- `2024-11-29T09:00:00+00:00`
- `2024-11-29T18:00:00+00:00`
- `2024-11-30T03:00:00+00:00`
- `2024-11-30T12:00:00+00:00`
- `2024-11-30T21:00:00+00:00`
- `2024-12-01T15:00:00+00:00`
- `2024-12-02T00:00:00+00:00`

Expected target shape:

- absent action = `LONG`
- enabled action = `NONE`
- `zone = low`
- `candidate = LONG`
- `bars_since_regime_change >= 8`
- `switch_reason in {AGED_WEAK_CONTINUATION_GUARD, insufficient_evidence}`

Expected target reason counts from preflight lock:

- `AGED_WEAK_CONTINUATION_GUARD = 4`
- `insufficient_evidence = 5`

### Exact nearby displacement row

True nearby displacement comparison row (`1`):

- `2024-12-01T00:00:00+00:00`

Expected comparison shape:

- absent action = `NONE`
- enabled action = `LONG`
- `switch_reason = stable_continuation_state`

### Exact nearby context-only stable blocked row

Context-only stable blocked row (`1`):

- `2024-12-01T06:00:00+00:00`

Expected context-only shape:

- absent action = `LONG`
- enabled action = `NONE`
- `switch_reason = stable_continuation_state`

### Local envelope lock

- local envelope start: `2024-11-27T15:00:00+00:00`
- local envelope end: `2024-12-03T00:00:00+00:00`

## Allowed input surface

This slice may read only:

- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2024_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- committed analysis anchors that already motivate the 2024 regression pocket:
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`

No new year selection, no fresh subject search beyond the exact timestamps above, and no reuse of the exhausted March 2021/March 2025 artifact loop as the primary subject are allowed.
Allowed motivating anchors are restricted to the explicit enumerated file list in this packet; generic anchor categories are not permitted. If an anchor path is not listed verbatim here, it is out of scope for this slice.

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_isolation_packet_2026-04-30.md`
  - `scripts/analyze/ri_policy_router_2024_regression_pocket_isolation_20260430.py`
  - `tests/backtest/test_ri_policy_router_2024_regression_pocket_isolation.py`
  - `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.md`
  - optional refresh of `GENESIS_WORKING_CONTRACT.md` only if the pocket evidence materially changes the next admissible step
- **Scope OUT:**
  - no runtime/config/schema/authority/default changes
  - no new backtest reruns
  - no widening to additional years or additional 2024 pockets
  - no neighbor discovery beyond the fixed local envelope and exact rows above
  - no promotion/readiness/champion claims
- **Expected changed files:** 5-6
- **Max files touched:** 6

## Planned method

1. read the exact 2024 fixed pocket rows only
2. keep the mixed blocked target cluster, true nearby displacement row, and context-only stable blocked row as separate labeled cohorts
3. join those rows against curated `3h` candles for the same bounded observational proxies already used in the prior local-window notes (`fwd_4`, `fwd_8`, `fwd_16`, `mfe_16`, `mae_16`)
4. document whether this exact 2024 regression pocket behaves like a locally harmful blocked cluster, a mixed displacement pocket, or a broader suppression/displacement blend

This slice is descriptive and non-authoritative. It does not authorize runtime threshold changes, router-policy changes, family/champion/promotion claims, readiness claims, or any reopen of already closed low-zone / aged-weak runtime lines.
This slice is observational and non-authoritative. Any conclusion is limited to the fixed 2024 pocket defined here and does not authorize runtime router, strategy, backtest, optimizer, config, or promotion changes.
The helper is fail-closed: if the expected timestamp set, cohort counts, action transitions, reason split, or envelope membership differ from this packet, the run must abort rather than widen scope.

## Validation requirements

- `get_errors` on the new packet/script/test/note and any touched working-contract file
- repo baseline lint outcome reported
- exact helper execution against the fixed 2024 subject
- deterministic repeat-run proof with stable identical JSON output
- artifact row-lock/signature check proving the emitted target/displacement/context timestamps match the packet exactly and that the expected action-pair / reason shapes hold
- focused unit test for any new reusable helper logic introduced
- `ruff check` on the new Python files
- `pre-commit run --files` on the touched files
- reported pass/no-drift outcomes for the repository determinism replay, feature cache invariance, and pipeline invariant selectors
- git visibility check for the new `results/evaluation` artifact
- manual diff review confirming no drift beyond the fixed 2024 pocket slice

Artifact packaging note:

- the generated JSON artifact is a local reproducibility artifact for this slice and remains ignored under current repo policy unless explicitly staged

Done criteria for this slice:

- the script produces one deterministic JSON artifact from the fixed 2024 inputs only
- target/displacement/context rows materialize exactly as packeted
- the note remains descriptive/non-authoritative
- green lint, a direct smoke of the fixed-pocket helper, and reported selector outcomes for determinism replay, feature-cache invariance, and pipeline invariant checks are included in the final report
- no widening beyond this exact 2024 pocket occurs

## Stop conditions

- the exact 2024 fixed rows cannot be materialized from the existing 2024 action-diff file
- the slice starts depending on new year selection or new pocket discovery
- the note starts implying runtime tuning or policy authority
- the helper needs to broaden into a generic annual pocket miner rather than a fixed-subject helper

## Output required

- one deterministic JSON summary artifact for the fixed 2024 pocket
- one human-readable analysis note stating what the pocket does and does not justify
- exact validation outcomes
