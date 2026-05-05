# RI policy router insufficient-evidence D1 context-clean selectivity falsifier 2026-05-05

Date: 2026-05-05
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / fixed four-surface bank reread / bounded context-clean non-null`

This slice is the first fresh post-synthesis follow-up after the completed four-surface D1 re-anchor.
It keeps the already-locked D1 bank fixed:

- exact harmful `2019-06`
- exact weak-control `2022-06`
- exact weak-control `2025-03`
- exact source-backed weak-control `2020-10/11`

It does **not** reopen July `2024`, March as a primary loop, late-2024, annual raw rereads, or any runtime/config/promotion authority.

The only new question here was:

> if the exact four-surface D1 bank is frozen and reread as one combined target bank versus one combined context bank, does any admitted non-age D1 field remain context-clean on that fixed bank when the test is defined as `target_ceiling < context_min`?

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** test whether the already-admitted D1 non-age family remains context-clean on the exact frozen four-surface bank without widening the subject set or reintroducing threshold search
- **Candidate:** `fixed four-surface target-bank ceiling vs fixed four-surface context-bank minimum`
- **Base SHA:** `6ac59ef0c08cb3328348d5e64ad40d83ccd4f9f9`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_precode_packet_2026-05-05.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_to_local_context_floor_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_four_surface_synthesis_2026-05-05.md`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_exact_subject_pair_2019_06_vs_2022_06_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_family_survival_2019_06_vs_2025_03_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_boundary_gap_transport_check_2019_06_vs_2020_10_11_2026-05-04.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json`

## Exact commands run

- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_20260505.py`
- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_20260505.py --base-sha 6ac59ef0c08cb3328348d5e64ad40d83ccd4f9f9`
- `Get-FileHash results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json -Algorithm SHA256 ; rerun helper ; Get-FileHash ...` -> identical replay hash `E388D53B5371981BB021E22082B34E9A94DA482C99A5A011EEC5FCE8FC18BD12`
- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pre_commit run --files docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_precode_packet_2026-05-05.md scripts/analyze/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_20260505.py results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.md GENESIS_WORKING_CONTRACT.md`

## Fixed bank that actually materialized

Claim-bearing target bank (`19` rows total):

- harmful `2019-06`: `5`
- control `2020-10/11`: `4`
- control `2022-06`: `5`
- control `2025-03`: `5`

Fixed context bank (`14` rows total):

- harmful sibling/context `2019-06`: `1`
- control context `2020-10/11`: `4`
- control context `2022-06`: `4`
- control context `2025-03`: `5`

Re-asserted bank locks:

- shared harmful `2019-06` rows still match across the first-pair and family-survival artifacts
- the transport artifact still matches the same `2019-06` harmful summary surface
- the source-backed `2020` target/context rows remain the exact locked eight-row set from the prior transport slice
- all four evaluated fields are directly evaluable on all `33` locked rows

## Main result

### 1. The slice returns a bounded non-null result on all three admitted non-age fields

Final artifact status:

- `bounded_context_clean_selectivity_present`

Non-null claim fields:

- `action_edge`
- `confidence_gate`
- `clarity_raw`

No admitted claim field failed on overlap and no admitted claim field lost evaluability.

### 2. The bank-level ceiling stays below the bank-level context minimum for all three admitted fields

The fixed bank-level reread is:

- `target_ceiling = max(all claim-eligible target rows)`
- `context_min = min(all fixed context rows)`
- context-clean survivor iff `target_ceiling < context_min`

That condition holds on the exact frozen bank for all three admitted non-age fields.

### 3. `action_edge` is context-clean on the fixed bank

Global bank values:

- `target_ceiling = 0.033803` at `2019-06-14T00:00:00+00:00`
- `context_min = 0.042122` at `2019-06-12T06:00:00+00:00`
- global separation margin = `0.008319`
- leaky context rows = `0`

Per-surface separation margins:

- harmful `2019-06`: `0.008319`
- control `2025-03`: `0.025155`
- control `2022-06`: `0.048356`
- control `2020-10/11`: `0.059708`

So the tightest bank constraint is still the harmful-side sibling row, and even that row stays strictly above the full target bank ceiling.

### 4. `confidence_gate` is also context-clean on the same bank

Global bank values:

- `target_ceiling = 0.516902` at `2019-06-14T00:00:00+00:00`
- `context_min = 0.521061` at `2019-06-12T06:00:00+00:00`
- global separation margin = `0.004159`
- leaky context rows = `0`

Per-surface separation margins:

- harmful `2019-06`: `0.004159`
- control `2025-03`: `0.012578`
- control `2022-06`: `0.024178`
- control `2020-10/11`: `0.029854`

Again, the tightest bank bound is the harmful sibling row rather than one of the control surfaces.

### 5. `clarity_raw` survives the same reread cleanly

Global bank values:

- `target_ceiling = 0.364914` at `2019-06-14T00:00:00+00:00`
- `context_min = 0.369952` at `2019-06-12T06:00:00+00:00`
- global separation margin = `0.005038`
- leaky context rows = `0`

Per-surface separation margins:

- harmful `2019-06`: `0.005038`
- control `2025-03`: `0.015233`
- control `2022-06`: `0.029282`
- control `2020-10/11`: `0.036156`

So the source-backed `2020` admission holds inside the new bank reread too, but it is **not** the tightest constraint. The fixed harmful sibling remains tighter.

### 6. `clarity_score` also separates, but stays fenced as descriptive only

Global bank values:

- `target_ceiling = 36.0`
- `context_min = 37.0`
- global separation margin = `1.0`
- leaky context rows = `0`

This is intentionally excluded from PASS/FAIL because the packet allowed it only as a descriptive side read, not as part of the admitted claim family.

## What changed relative to the previous four-surface synthesis

The synthesis note had already established a bounded four-surface recurrence bank on `action_edge`, `confidence_gate`, and `clarity_raw`, but it still described the line honestly as context-leaky and reopened only by a fresh governed question.

This falsifier slice adds one new bounded answer:

> on the exact already-frozen four-surface D1 bank, the admitted non-age target bank still sits cleanly below the fixed context bank on `action_edge`, `confidence_gate`, and `clarity_raw` when the reread is defined as bank-level ceiling versus bank-level context minimum.

That is stronger than simple “another control recurrence.”
It means the current D1 line is no longer only target-vs-control separable while leaking on the fixed sibling/context rows **within this exact bank reread**.
The harmful-side sibling row remains the tightest constraint, and the target bank still stays below it.

## Interpretation

The smallest honest read from this slice is:

> on the exact frozen four-surface D1 bank, the already-admitted non-age family remains context-clean under the bounded bank reread `target_ceiling < context_min`, with the tightest constraint coming from the harmful-side sibling row rather than from any weak-control context row.

This remains:

- exact-bank only
- observational only
- non-authoritative
- insufficient for runtime/policy/promotion authority
- insufficient for claiming broader portability beyond the fixed four-surface bank

## What this slice does **not** prove

This slice does **not** prove:

- that a portable runtime rule now exists
- that the D1 family is globally classifier-clean outside the frozen four-surface bank
- that any new fifth recurrence surface should be opened automatically
- that July `2024`, March, late-2024, or annual raw rereads should be reopened by default
- that runtime/config/default/policy/promotion changes are warranted

## Next admissible step

The next honest move is **not** another cheap recurrence extension by default.
The fixed four-surface bank now supports both bounded recurrence and one bounded context-clean reread.

If the user wants to continue this line, the next smallest admissible question should therefore be one of only two shapes:

1. a bounded falsifier that tries to break this context-clean read on one genuinely new exact surface chosen by fresh packet logic, or
2. a bounded docs-only synthesis that states the new bank-level support and the remaining non-portability limits before any future reopening.

Until such a fresh packet exists, keep this result:

- exact-bank only
- observational only
- non-authoritative
- outside runtime/config/promotion scope
