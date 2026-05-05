# RI policy router insufficient-evidence D1 family survival 2019-06 vs 2025-03

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only fixed-family survival check / second exact pair`

This slice is the bounded follow-up to the completed exact D1 pair `2019-06 harmful` vs `2022-06 weak control`.
It does not search for a new separator.
It does not reopen the parked July `2024` transport chain.
It does not authorize runtime, default, policy, config, or promotion work.

It asks only whether the already-observed non-age D1 threshold family survives when the harmful side remains fixed at exact `2019-06` and the control side is swapped to exact `2025-03`.

All returns and excursion values in this slice are timestamp-close observational proxies on existing evidence rows only.
They are descriptive only and do not establish realized trade PnL, fill-aware row truth, causal authority, runtime readiness, or transport authorization.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: the helper reads two fixed annual action-diff files plus curated candles only and evaluates pre-registered thresholds on a locked row set.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** test whether the already-observed non-age D1 threshold family survives on one second fixed harmful/control pair without threshold edits, field search, or control-family substitution.
- **Candidate:** `fixed 2019-06 harmful anchor vs exact 2025-03 weak control`
- **Base SHA:** `cbd03a763a22f8ab0902e2b7a8db73e8d581e7d5`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_precode_packet_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2019_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.json`

## Exact commands run

- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_20260504.py`
- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_20260504.py --base-sha cbd03a763a22f8ab0902e2b7a8db73e8d581e7d5`
- identical second helper run on the same locked pair with SHA256 hash check before/after

Determinism check on the emitted artifact:

- SHA256 before rerun: `81D8B30B4EA25814B58EB37443B74EC9E5E5DA68D1020167EC9E6FE9983A68F7`
- SHA256 after rerun: `81D8B30B4EA25814B58EB37443B74EC9E5E5DA68D1020167EC9E6FE9983A68F7`

## Fixed pair that actually materialized

### Exact harmful target (`2019-06`) (`5` rows)

- `2019-06-13T06:00:00+00:00`
- `2019-06-13T15:00:00+00:00`
- `2019-06-14T00:00:00+00:00`
- `2019-06-14T09:00:00+00:00`
- `2019-06-15T06:00:00+00:00`

Shared target context re-asserted by the helper:

- year = `2019`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `164`

Offline proxy read still holds:

- `fwd_16` mean = `+8.104614%`

### Exact harmful sibling context (`1` row)

- `2019-06-12T06:00:00+00:00`
- `switch_reason = AGED_WEAK_CONTINUATION_GUARD`
- `action_pair = LONG -> NONE`
- `claim_eligible = false`

### Exact weak-control target (`2025-03`) (`5` rows)

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

Shared target context re-asserted by the helper:

- year = `2025`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `65`

Offline proxy read still holds:

- `fwd_16` mean = `-1.017927%`

### Exact control supporting rows (`5` rows, context only)

Displacement rows:

- `2025-03-13T15:00:00+00:00`
- `2025-03-14T00:00:00+00:00`

Stable blocked context rows:

- `2025-03-13T21:00:00+00:00`
- `2025-03-14T06:00:00+00:00`

Aged-weak context row:

- `2025-03-16T12:00:00+00:00`

All five supporting rows were emitted with:

- `row_role = context`
- `claim_eligible = false`

Only the `harmful_target` and `control_target` rows were claim-eligible for PASS/FAIL adjudication.

## Main result

### 1. The non-age D1 family survives on the second exact pair

All three inherited non-age rules remained perfectly separating on the exact harmful-target vs control-target pair:

- `action_edge >= 0.027801`
- `confidence_gate >= 0.513901`
- `clarity_raw >= 0.361280`

For each of the three rules:

- all `5/5` harmful target rows were selected
- all `0/5` control target rows were selected
- `perfect_target_control_separation = true`
- `survives_on_target_pair = true`

So the current D1 non-age family is **not** just a `2019-06` vs `2022-06` one-off.
On this second exact pair, the family survives unchanged.

### 2. `clarity_raw` remained fully evaluable and also survived

The packet required `clarity_raw` to fail closed if it was missing on any locked target row.
That did **not** happen here.

`clarity_raw` status:

- evaluability = `evaluable`
- missing timestamps = none

Target ranges on the second pair:

- harmful target `clarity_raw`: `0.361280 .. 0.364914`
- control target `clarity_raw`: `0.351678 .. 0.357855`

So `clarity_raw >= 0.361280` remained a valid and separating fixed-family member on this pair.

### 3. The age-only comparator does not carry the result

The descriptive-only age comparator was recorded exactly as packeted:

- `bars_since_regime_change <= 164`

It did **not** separate the fixed harmful/control target pair:

- harmful target selected: `5/5`
- control target selected: `5/5`
- `perfect_target_control_separation = false`
- `excluded_from_pass_fail = true`

That matters because the second-pair read does **not** collapse back to an age-only story.
The surviving answer remains genuinely non-age on this locked pair.

### 4. The family still selects every context row and therefore remains context-leaky

The second-pair survival result is real, but it is not classifier-clean.
Each surviving non-age rule also selected all fixed context rows:

- harmful sibling context selected: `1/1`
- control displacement context selected: `2/2`
- control stable blocked context selected: `2/2`
- control aged-weak context selected: `1/1`

This means the family is recurring on the second pair, but it is still broad enough to cover:

- the harmful blocked target,
- the harmful sibling context row,
- the weak-control blocked target envelope’s surrounding stable rows,
- and the one aged-weak context row.

So the honest description is:

> the non-age D1 family survives the second pair, but it still behaves like a broad local-envelope marker rather than a clean harmful-vs-correct-suppression selector.

## Comparison against the first exact pair

The first D1 exact pair already showed that the same three non-age thresholds separated `2019-06 harmful` from `2022-06 weak control`, while still selecting sibling/context rows.

This second pair sharpens that read in two directions:

1. **recurrence:** the family survives a fresh positive-year weak control without threshold edits or field substitution
2. **limitation remains:** the family still selects all fixed context rows, so the recurrence does not rescue it into a transport-ready or classifier-clean rule

That is stronger than the first pair alone because the family now survives two distinct exact harmful/control pairs.
But it is still bounded, descriptive, and leakage-prone.

## Interpretation

The smallest honest read from this slice is now:

> the current D1 non-age family has second-pair recurrence, but the recurrence remains context-leaky and therefore does not yet justify a harmful-vs-correct suppression transport claim.

What this slice now supports:

- the existing non-age family is not merely a `2019-06` vs `2022-06` accident
- `2025-03` does not force the family to collapse back to age-only behavior
- `clarity_raw` remains a legitimate member of the fixed family on the current locked pair

What this slice still does **not** support:

- runtime threshold promotion
- July `2024` reopen
- transport of the family into a clean selector claim
- any statement that the surviving rules distinguish harmful blocked targets from all correct-suppression or context rows

## What this slice does not prove

This slice does **not** prove:

- exact realized trade contribution
- that the surviving family is globally stable outside the two fixed pairs
- that the surviving family is context-clean
- that a one-rule or three-rule runtime discriminator is justified
- that the parked July chain should be reopened
- that any promotion or readiness claim is warranted

## Next admissible step

The next honest read-only question is no longer whether the current non-age family survives a second pair.
This slice answered that with a bounded **yes**.

The next honest question becomes:

> can any still-bounded residual check separate the harmful-vs-correct target rows without also selecting the full fixed context envelope, or is the current family best interpreted as pair-recurring but context-broad?

That keeps the work inside research-evidence and avoids pretending that second-pair survival already solved the classifier-clean part of the problem.
