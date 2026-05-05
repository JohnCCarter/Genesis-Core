# RI policy router insufficient-evidence D1 boundary-gap transport check 2019-06 vs 2020-10/11

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / source-backed third-control transport check / exact 2019-06 vs 2020-10/11`

This slice is the bounded follow-up to the completed D1 exact-pair, second-pair family-survival, and exact-tri-surface boundary-gap reread.
It keeps the exact `2019-06` harmful anchor fixed.
It introduces only one fresh control surface: the exact `2020-10-31 -> 2020-11-02` weak-control cluster that was already row-locked in the older truth-surface-correction work.
It does **not** reopen March as a primary loop, reopen July `2024` as transport logic, recycle late-2024, or restore runtime/default/policy/promotion authority.

The only new question here was:

> does the already-admitted D1 non-age boundary-gap family survive on one third exact weak-control surface once the `2020` side is checked source-backed and `clarity_raw` is required to be directly present rather than inferred?

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** test whether the current D1 boundary-gap family survives on exact `2019-06` versus exact `2020-10/11` without silently downgrading the family.
- **Candidate:** `fixed 2019-06 harmful anchor vs exact 2020-10/11 weak control`
- **Base SHA:** `6ac59ef0c08cb3328348d5e64ad40d83ccd4f9f9`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_precode_packet_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.md`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2020_enabled_vs_absent_action_diffs.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.json`

## Exact commands run

- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_20260504.py`
- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_20260504.py --base-sha 6ac59ef0c08cb3328348d5e64ad40d83ccd4f9f9`
- `pre-commit run --files docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_precode_packet_2026-05-04.md scripts/analyze/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_20260504.py results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.json docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.md GENESIS_WORKING_CONTRACT.md`

## Fixed surface that actually materialized

### Exact harmful surface (`2019-06`)

Claim-bearing harmful target rows (`5`):

- `2019-06-13T06:00:00+00:00`
- `2019-06-13T15:00:00+00:00`
- `2019-06-14T00:00:00+00:00`
- `2019-06-14T09:00:00+00:00`
- `2019-06-15T06:00:00+00:00`

Fixed sibling context row (`1`):

- `2019-06-12T06:00:00+00:00`

Re-asserted local shape:

- `row_role = harmful_target` on the five target rows
- `row_role = context`, `claim_eligible = false` on the sibling row
- target `fwd_16` mean remains harmful-looking at `+8.104614%`

### Exact weak-control surface (`2020-10/11`)

Claim-bearing control target rows (`4`):

- `2020-10-31T21:00:00+00:00`
- `2020-11-01T06:00:00+00:00`
- `2020-11-01T15:00:00+00:00`
- `2020-11-02T00:00:00+00:00`

Fixed context rows (`4`):

- `2020-11-02T03:00:00+00:00`
- `2020-11-02T09:00:00+00:00`
- `2020-11-02T21:00:00+00:00`
- `2020-11-03T03:00:00+00:00`

Re-asserted local shape:

- target rows remain low-zone `LONG -> NONE` `insufficient_evidence` rows under `RI_no_trade_policy`
- context rows remain descriptive only and excluded from PASS/FAIL adjudication
- target `fwd_16` mean remains weak/correct-suppression-looking at `-0.875411%`

## Main result

### 1. The slice did **not** fail closed on `clarity_raw`

The older truth-surface-correction artifact did not materialize `clarity_raw` on the `2020` rows.
That was the honest hinge for this packet.

The source-backed reread now shows that the raw locked `2020` action-diff rows do carry `clarity_raw` directly on all eight required target/context rows:

- `action_edge`: evaluable on all `14` locked rows
- `confidence_gate`: evaluable on all `14` locked rows
- `clarity_raw`: evaluable on all `14` locked rows
- descriptive side reads `clarity_score` and `bars_since_regime_change`: also fully evaluable

So the slice stays on the **same** D1 family rather than silently collapsing to a reduced family.

### 2. The transport check is bounded **non-null** on all three admitted non-age fields

Final artifact status:

- `bounded_boundary_gap_signal_present`

Non-null claim fields:

- `action_edge`
- `confidence_gate`
- `clarity_raw`

No admitted primary field failed and no primary field collapsed to overlap.

### 3. `action_edge` preserves the harmful-smaller boundary-gap ordering

All-context floors:

- harmful `2019-06` floor = `0.042122`
- control `2020-10/11` floor = `0.091692`

Target boundary-gap ranges:

- harmful `2019-06`: `0.008319 .. 0.014321`
- control `2020-10/11`: `0.059708 .. 0.069064`

Required pairwise ordering holds:

- harmful range is strictly smaller
- ranges do not overlap
- separation margin = `0.045387`

### 4. `confidence_gate` preserves the same ordered gap shape

All-context floors:

- harmful `2019-06` floor = `0.521061`
- control `2020-10/11` floor = `0.545846`

Target boundary-gap ranges:

- harmful `2019-06`: `0.004159 .. 0.007160`
- control `2020-10/11`: `0.029854 .. 0.034532`

Required pairwise ordering holds:

- harmful range is strictly smaller
- ranges do not overlap
- separation margin = `0.022694`

### 5. `clarity_raw` also survives cleanly once the `2020` side is checked source-backed

All-context floors:

- harmful `2019-06` floor = `0.369952`
- control `2020-10/11` floor = `0.399969`

Target boundary-gap ranges:

- harmful `2019-06`: `0.005038 .. 0.008672`
- control `2020-10/11`: `0.036156 .. 0.041822`

Required pairwise ordering holds:

- harmful range is strictly smaller
- ranges do not overlap
- separation margin = `0.027484`

So the exact field that could have forced a fail-closed outcome instead survives and confirms the same boundary-gap read.

### 6. Descriptive side reads stay fenced

`clarity_score` also separates on this exact pair:

- harmful gap range = `1.0 .. 1.0`
- control gap range = `4.0 .. 4.0`

But it remains descriptive only because the packet explicitly forbade promoting it into the claim family.

`bars_since_regime_change` remains non-carrying here:

- harmful gap range = `0.0 .. 0.0`
- control gap range = `0.0 .. 0.0`

So the bounded result still belongs to the three admitted non-age fields only.

## What changed relative to the previous D1 state

The earlier D1 chain had already established three bounded facts:

1. one exact harmful/control pair survives on `action_edge`, `clarity_raw`, and `confidence_gate`
2. the same family survives unchanged on a second exact weak-control surface
3. on the fixed `2019-06` / `2022-06` / `2025-03` tri-surface, the harmful target sits materially closer to its local context floor than both weak-control targets do

This transport slice adds one new bounded answer:

> the same boundary-gap family now survives on a third exact weak-control surface once the `2020` side is checked source-backed and `clarity_raw` is admitted honestly rather than assumed.

That is stronger than the pre-run expectation.
It means the current D1 line is no longer hanging on “two controls plus a reread.”
It now has one additional third-control recurrence check with direct `clarity_raw` admission.

## Interpretation

The smallest honest read from this slice is:

> on the exact already-locked `2019-06` versus exact `2020-10/11` surface, the harmful blocked target sits materially closer to its local context floor than the weak-control target does on `action_edge`, `confidence_gate`, and `clarity_raw`, and the `2020` side supports that read without any reduced-family substitution.

This remains:

- exact-surface only
- observational only
- non-authoritative
- target-only for PASS/FAIL
- unsuitable as runtime, policy, promotion, or transport authority by itself

## What this slice does **not** prove

This slice does **not** prove:

- that a portable runtime boundary-gap rule exists
- that the current D1 family is globally classifier-clean
- that the parked July `2024` translation chain should be reopened
- that more year widening is automatically justified
- that runtime/config/default/policy changes are warranted

## Next admissible step

The next honest move is no longer another cheap control transport check by default.
This slice already answered the narrow `2020` admission/recurrence question with a bounded non-null result.

If the user wants to continue this exact insufficient-evidence D1 line, the next smallest honest move is now a **bounded synthesis / re-anchor step** that states clearly what the four-surface D1 chain now does and does not justify before any further widening or candidate discussion is proposed.

That next step must still:

- keep the July `2024` translation chain parked
- avoid reopening March as a primary loop
- avoid late-2024 recycling
- avoid runtime/config-authority/promotion drift
- keep any future interpretation exact-surface only unless a later governed packet proves otherwise
