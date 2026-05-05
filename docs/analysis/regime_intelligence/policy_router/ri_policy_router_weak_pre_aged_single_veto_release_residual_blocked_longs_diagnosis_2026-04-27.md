# RI policy router weak pre-aged single-veto release residual blocked-longs diagnosis

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / analysis-lane diagnosis / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice refines the interpretation of an already executed fail-set result using existing artifacts plus one read-only router-meta probe, but does not modify runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the single-veto fail-set evidence already exists, and the next honest need is to explain whether the remaining blocked baseline longs are still one seam-A problem or a split residual set before any new candidate framing begins.
- **Objective:** explain why the five residual blocked baseline longs left after same-pocket de-chaining are not one remaining seam-A issue.
- **Base SHA:** `HEAD`

## Scope

### Scope IN

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_release_cooldown_displacement_diagnosis_2026-04-24.md`
- `src/core/strategy/ri_policy_router.py`
- one new docs-only diagnosis note
- one read-only evaluation-hook probe over the already executed fail-B subject to inspect `meta['decision']['state_out']['research_policy_router_debug']`

### Scope OUT

- runtime edits
- config edits
- test edits
- tracked artifact writes beyond this diagnosis note
- findings-bank writes
- seam-B runtime intervention
- keep-set or stress-set verification

## Evidence inputs

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_release_cooldown_displacement_diagnosis_2026-04-24.md`
- `results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_b_2023_dec_candidate_decision_rows.ndjson`
- `src/core/strategy/ri_policy_router.py`
- read-only candidate carrier input: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`

## Analysis method

The existing decision-row artifacts are intentionally thin and do **not** carry `state_out` or router debug.

To diagnose the residual rows without changing tracked code, this slice used one read-only probe over the exact fail-B subject:

- same candidate config and canonical env as the completed fail-set run
- same `tBTCUSD` / `3h` / `2023-12-01 -> 2023-12-31` window
- same `curated_only` and warmup `120`
- a custom in-terminal `evaluation_hook` layered over the existing hook to inspect `meta['decision']['state_out']['research_policy_router_debug']` and `research_policy_router_state`

This probe is observational only and does not reopen runtime integration.

## Diagnosis

### 1. The residual five rows are not one remaining seam-A pocket

After the single-veto latch removed repeated same-pocket re-blocking, five blocked baseline longs still remained:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`
- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

The read-only router-meta probe shows these rows do **not** share one mechanism.

They split across at least two distinct router surfaces:

1. raw no-trade / `insufficient_evidence` rows in the earlier low-zone pocket
2. later `AGED_WEAK_CONTINUATION_GUARD` rows at regime ages `>= 16`

That means the remaining negative fail-set outcome is no longer best described as “one last seam-A release problem.”

### 2. The early residual rows are raw no-trade floor rows, not weak-pre-aged release-guard rows

For `2023-12-21T18:00:00+00:00` and `2023-12-22T09:00:00+00:00`, the router-meta probe shows:

- `raw_target_policy = RI_no_trade_policy`
- `switch_reason = insufficient_evidence`
- `switch_blocked = False`
- `weak_pre_aged_single_veto_latch = False`

The same pattern also appears on `2023-12-20T03:00:00+00:00`:

- `raw_target_policy = RI_no_trade_policy`
- `switch_reason = insufficient_evidence`
- `previous_policy = RI_continuation_policy`
- no seam-A latch activity

So these rows are not residual same-pocket re-blocks from the single-veto seam-A mechanism.
They are earlier raw no-trade-floor suppressions on low-zone rows.

### 3. The actual seam-A single-veto row remains local and behaves as intended

The probe around the intended seam-A transition shows the bounded single-veto behavior clearly:

- `2023-12-22T12:00:00+00:00`
  - `raw_target_policy = RI_no_trade_policy`
  - `switch_reason = insufficient_evidence`
  - latch inactive
- `2023-12-22T15:00:00+00:00`
  - `raw_target_policy = RI_continuation_policy`
  - `switch_reason = WEAK_PRE_AGED_CONTINUATION_RELEASE_GUARD`
  - `switch_blocked = True`
  - latch active
- `2023-12-22T18:00:00+00:00`
  - `raw_target_policy = RI_continuation_policy`
  - `selected_policy = RI_continuation_policy`
  - `switch_reason = continuation_state_supported`
  - `switch_blocked = False`
  - latch remains active, but no second same-pocket veto occurs

This confirms that the single-veto seam-A slice is doing exactly what it was designed to test:

- one bounded weak-pre-aged release veto at `2023-12-22 15:00`
- no recursive same-pocket re-block at `2023-12-22 18:00`

Therefore the earlier residual rows at `2023-12-21 18:00` and `2023-12-22 09:00` should not be attributed to the single-veto seam-A mechanism.

### 4. The `2023-12-20` cluster is a no-trade-floor transition followed by min-dwell retention

The `2023-12-20T03:00:00+00:00` residual row is the first low-zone block in its cluster and is driven by raw no-trade floor:

- `raw_target_policy = RI_no_trade_policy`
- `switch_reason = insufficient_evidence`
- `previous_policy = RI_continuation_policy`

The immediately following rows then show a different downstream pattern:

- `2023-12-20T06:00:00+00:00`
- `2023-12-20T09:00:00+00:00`

At those rows the raw target has already shifted to `RI_defensive_transition_policy`, but the selected policy remains `RI_no_trade_policy` because:

- `switch_reason = switch_blocked_by_min_dwell`

So the `2023-12-20` cluster is not a weak-pre-aged release problem.
It is a raw no-trade-floor entry into a short min-dwell-retained no-trade stretch.

### 5. The late residual rows are an older aged-weak continuation seam

The remaining later blocked baseline longs are not seam-A either.

At both:

- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

the router-meta probe shows:

- `previous_policy = RI_continuation_policy`
- `raw_target_policy = RI_no_trade_policy`
- `switch_reason = AGED_WEAK_CONTINUATION_GUARD`
- `bars_since_regime_change = 19` and `22` respectively
- no single-veto latch activity

These rows therefore belong to the older `aged weak continuation guard` seam, not to the single-veto seam-A slice.

### 6. The residual fail-set is now split across distinct mechanisms

After same-pocket de-chaining, the remaining negative rows are best classified as:

- **Class A — raw low-zone no-trade-floor / insufficient-evidence rows:**
  - `2023-12-20T03:00:00+00:00`
  - `2023-12-21T18:00:00+00:00`
  - `2023-12-22T09:00:00+00:00`
- **Class B — aged weak continuation guard rows:**
  - `2023-12-28T09:00:00+00:00`
  - `2023-12-30T21:00:00+00:00`

The intended seam-A weak-pre-aged single-veto row at `2023-12-22T15:00:00+00:00` is still present, but it is no longer the mechanism driving the residual five-row fail-set story.

## Bounded conclusion

The residual blocked baseline longs left after single-veto de-chaining are **not** one remaining seam-A problem.

More precise statement:

- the single-veto seam-A slice now behaves locally as intended,
- the earlier repeated same-pocket displacement loop is gone,
- the first three residual rows come from raw no-trade-floor / insufficient-evidence behavior,
- the last two residual rows come from the older aged-weak continuation guard.

So the remaining fail-set-negative surface is now **split across distinct router seams**.

## Next admissible implication

The next honest step is no longer “another seam-A refinement” in generic form.

Instead, any follow-up should first choose **one** of the remaining residual surfaces explicitly:

1. low-zone `insufficient_evidence` / no-trade-floor behavior around `2023-12-20 -> 2023-12-22`, or
2. the older `aged weak continuation guard` behavior around `2023-12-28` and `2023-12-30`

Without that split, the residual set risks being misread as one unresolved seam-A issue even though the row-level router evidence now shows otherwise.

## Output of this slice

- one repo-visible diagnosis showing that the post-single-veto residual fail-set is split across distinct router mechanisms rather than one remaining seam-A pocket
- one sharper basis for the next bounded candidate-framing / diagnosis packet
