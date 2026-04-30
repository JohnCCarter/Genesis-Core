# RI policy router insufficient-evidence counterfactual screen precode packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / read-only bounded evidence slice / no behavior change`

Relevant skill: `decision_gate_debug`

Skill Usage: invoke the relevant repo-local Python engineering / analysis-helper skill for this read-only evidence slice. No runtime-authority or config-authority skill is in scope.

Skill coverage for this slice is explicit and bounded:

- `decision_gate_debug` governs exact mechanism separation across the fixed `insufficient_evidence` suppressor rows, the nearby `stable_continuation_state` comparison/context rows, and the requirement that any candidate behave like a true counterfactual unlock screen rather than a generic blocked-versus-displacement contrast.
- `python_engineering` governs the typed helper structure, deterministic artifact emission, fail-closed loader behavior, and minimal-diff validation path for a Python 3.11+ read-only analysis helper.

Lite checks for this slice are explicit:

- exact row-lock proof on both fixed subjects and their nearby comparison/context rows
- helper import/materialization smoke on the fixed 2024 and 2020 subjects
- artifact schema check for the bounded JSON summary

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice is read-only and confined to one already-materialized 2024 pocket artifact plus one fresh exact 2020 action-diff/candle control subject; it does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the March 2021 / March 2025 four-cohort loop is already closed, and the next honest question is whether any simple decision-time split survives on one genuinely new bounded `insufficient_evidence` surface before any concept or runtime widening is discussed.
- **Objective:** test whether any simple admissible decision-time split can distinguish payoff-harmful `insufficient_evidence` suppression on the exact 2024 pocket from payoff-correct suppression on one fresh exact positive-year 2020 control pocket.
- **Candidate:** `fixed 2024 harmful subset vs fixed 2020 positive-year control`
- **Base SHA:** `9ae9451d9d4d063db874ce14498a756209a2dd07`

## Why this packet exists

The current branch now has three relevant truths at the same time:

1. the March 2021 / March 2025 discriminator loop is already exhausted on the current repo-visible surface
2. the exact 2024 regression pocket is newly materialized and its local weakness is concentrated more clearly on the `insufficient_evidence` subset
3. no fresh exact positive-year `insufficient_evidence` control outside March 2025 was already materialized in repo-visible docs, so the next honest packet must lock one explicitly rather than speak abstractly

This packet therefore opens the next bounded screen on a **new** surface:

- harmful side fixed to the exact 2024 `insufficient_evidence` subset already documented in repo-visible evidence
- control side fixed to one fresh exact positive-year `insufficient_evidence` cluster on the current local annual action-diff surface

This remains research-only and non-authoritative.
It does **not** reopen runtime tuning.
It does **not** authorize config/default changes.
It does **not** convert payoff fields into runtime inputs.

The helper must stay fail-closed on source and row membership:

- `2024` input is restricted to `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
- no raw `2024` action-diff regeneration or fallback is allowed
- `2020` input is restricted to the exact packet timestamps on the annual action-diff surface plus curated candles for observational metrics only
- if any fixed row, count, year, zone, or action-pair lock fails, the helper must exit nonzero and must not broaden the surface

## Exact fixed subjects

### Harmful subject — exact 2024 `insufficient_evidence` subset (`5` rows)

This side is already fixed by the completed 2024 pocket reason-split anchor:

- `2024-11-29T09:00:00+00:00`
- `2024-11-29T18:00:00+00:00`
- `2024-11-30T03:00:00+00:00`
- `2024-12-01T15:00:00+00:00`
- `2024-12-02T00:00:00+00:00`

Locked shape:

- absent action = `LONG`
- enabled action = `NONE`
- `switch_reason = insufficient_evidence`
- `selected_policy = RI_no_trade_policy`
- `zone = low`
- `candidate = LONG`

Already-established nearby local context from the completed 2024 pocket note:

- true displacement row: `2024-12-01T00:00:00+00:00` (`NONE -> LONG`, `stable_continuation_state`)
- stable blocked context row: `2024-12-01T06:00:00+00:00` (`LONG -> NONE`, `stable_continuation_state`)

### Positive-year control subject — exact 2020 low-zone `insufficient_evidence` cluster (`4` rows)

This control is now fixed from the local annual action-diff surface and is outside the exhausted March 2021 / March 2025 loop:

- `2020-10-31T21:00:00+00:00`
- `2020-11-01T06:00:00+00:00`
- `2020-11-01T15:00:00+00:00`
- `2020-11-02T00:00:00+00:00`

Verified shared control shape on the current local action-diff surface:

- full year = `2020`
- absent action = `LONG`
- enabled action = `NONE`
- `switch_reason = insufficient_evidence`
- `selected_policy = RI_no_trade_policy`
- `zone = low`
- `candidate = LONG`
- `bars_since_regime_change = 302`

Verified nearby low-zone local comparison/context rows in the same bounded envelope:

- true displacement rows:
  - `2020-11-02T03:00:00+00:00` (`NONE -> LONG`, `stable_continuation_state`)
  - `2020-11-02T21:00:00+00:00` (`NONE -> LONG`, `stable_continuation_state`)
- stable blocked context rows:
  - `2020-11-02T09:00:00+00:00` (`LONG -> NONE`, `stable_continuation_state`)
  - `2020-11-03T03:00:00+00:00` (`LONG -> NONE`, `stable_continuation_state`)

Mid-zone rows inside the wider envelope may be cited for chronology only, but they must not be widened into the authoritative control cohort.

## Exact research question

The bounded question for this slice is:

> On the fixed 2024 harmful `insufficient_evidence` subset and the fixed 2020 positive-year control cluster, is there any simple decision-time split that would have selectively unlocked the harmful 2024 rows while still leaving the 2020 control rows suppressed?

This packet does **not** allow the weaker question:

> do the two pockets merely show a descriptive mean-gap difference?

The candidate must behave like a **counterfactual unlock screen**, not just a descriptive separator.

## Allowed inputs vs forbidden truth leakage

### Allowed decision-time candidate fields

Candidate screening is limited to the exact already-emitted numeric decision-time fields below and must not widen beyond them:

- `bars_since_regime_change`
- `action_edge`
- `confidence_gate`
- `clarity_score`

No additional field mining is allowed in this slice.
Categorical fields such as `previous_policy`, `selected_policy`, or `raw_target_policy` may be reported descriptively, but they are **not** part of the candidate-screen search space here.

### Payoff / offline truth fields

The following remain **offline truth only**:

- `fwd_4`
- `fwd_8`
- `fwd_16`
- `mfe_16`
- `mae_16`

They may:

- label rows as locally harmful vs locally justified on the observational surface
- score the counterfactual unlock behavior

They must **not**:

- appear as runtime-rule inputs
- be moved into router/default/config authority
- be treated as decision-time admissible state

## Planned method

1. materialize one bounded helper that locks the exact 2024 harmful subset, the exact 2020 control subset, and their explicitly listed comparison/context rows
2. compute observational payoff labels on both fixed subjects using the same bounded proxy family already used in the current chain
3. test only simple candidate forms:
   - one-field threshold splits

- shallow ordered two-field screens only if no single-field rule satisfies the predeclared survival rule below

4. require the candidate to pass the counterfactual unlock question on the fixed target/control cohorts:

- `selection_rate_2024_harmful_target >= 0.80`
- `selection_rate_2020_control_target <= 0.25`
- the helper must first confirm that the fixed `2024` side and fixed `2020` side are still truth-opposed on the offline proxy surface; if they are not, the helper must emit `no_surviving_screen` even if a mechanical cohort separator exists
- the helper must report nearby comparison/context selection rates descriptively, but those rows cannot rescue a candidate that fails the target/control survival rule

5. if no candidate satisfies that exact survival rule, the helper must emit `no_surviving_screen` and stop without broader search

### Explicit survival rule

A candidate survives on this bounded surface only if **all** of the following are true:

1. it uses only the exact candidate fields listed above
2. it is a single-field threshold, or an ordered two-field rule evaluated only after all single-field thresholds fail
3. it selects at least `4 / 5` rows from the fixed `2024` harmful target cohort
4. it selects at most `1 / 4` rows from the fixed `2020` control target cohort
5. it does not require widening to any other year, timestamp, or feature family
6. the fixed target/control sides remain truth-opposed on the offline proxy surface for this exact slice; otherwise the helper must stop at `no_surviving_screen`

If no candidate satisfies those conditions, the helper must write an explicit null result state rather than expanding the search.

## Exact future output paths to materialize

- analysis helper: `scripts/analyze/ri_policy_router_insufficient_evidence_counterfactual_screen_20260430.py`
- JSON artifact: `results/evaluation/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.md`

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_precode_packet_2026-04-30.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_counterfactual_screen_20260430.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.md`
  - optional refresh of `GENESIS_WORKING_CONTRACT.md` only if this packet becomes the active next-step anchor
- **Scope OUT:**
  - no runtime/config/schema/default/authority changes
  - no reopening of the closed March 2021 / March 2025 four-cohort loop as the primary subject
  - no Legacy implementation or Legacy evidence widening
  - no reopening of `AGED_WEAK_CONTINUATION_GUARD` as the first carrier
  - no annual re-mining outside the fixed 2024 and fixed 2020 subjects above
  - no payoff-field admission into runtime logic
- **Expected changed files:** `4-5`
- **Max files touched:** `5`

## Evidence anchors

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_structural_research_roadmap_2026-04-30.md`
- local evidence surface:
  - `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2020_enabled_vs_absent_action_diffs.json`
  - `data/curated/v1/candles/tBTCUSD_3h.parquet`

## Validation requirements

- `get_errors` on the packet, helper, analysis note, and any touched contract file
- exact row-lock proof for:
  - 2024 harmful subject (`5` rows)
  - 2024 nearby comparison/context rows (`1 / 1`)
  - 2020 control subject (`4` rows)
  - 2020 nearby comparison/context rows (`2 / 2`)
- helper import/materialization smoke on both exact subjects
- emitted artifact schema check proving cohort membership and field presence
- `ruff check` on the new helper wrapper and any touched Python file
- `pre-commit run --files` on the touched tracked files
- manual diff review confirming that payoff stays offline and no runtime-authority wording leaks into the analysis note

## Stop conditions

- the helper cannot reproduce the exact fixed 2024 or 2020 row sets above from the named evidence surfaces
- the helper attempts any fallback from the fixed `2024` artifact to raw `2024` action-diff inputs
- the best surviving candidate still only explains generic target-vs-displacement separation rather than harmful-vs-correct suppression
- the candidate unlocks the 2020 control rows at the same time as the harmful 2024 rows
- the slice begins to widen into another annual discovery exercise instead of staying on the fixed exact subjects
- the slice starts implying runtime tuning, readiness, or promotion authority

## Output required

- one deterministic JSON summary at `results/evaluation/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.json`
- one human-readable analysis note at `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.md`
- explicit verdict at closeout:
  - either `no clean counterfactual unlock screen survived on this bounded surface`, or
  - `one bounded candidate survived and only earns a later concept-only packet`

## What this packet does not authorize

This packet does **not** authorize:

- any runtime packet
- any config/default retuning
- any claim that payoff has become runtime-admissible
- any claim that one surviving research candidate is already `införd`
- any inherited authority from the closed March 2021 / March 2025 loop
