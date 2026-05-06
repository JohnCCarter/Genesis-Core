# RI policy router insufficient-evidence D1 late-2024 external-surface falsifier 2026-05-06

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-05`
Mode: `RESEARCH`
Status: `completed / exact external-surface falsifier / observational only`

This slice is the first fresh external-surface falsifier after the completed D1 four-surface synthesis and the completed D1 context-clean bank reread.
It keeps the exact D1 bank frozen.
It keeps the late-2024 surface frozen.
It does **not** reopen March as a primary loop, July `2024` as a primary subject, late-2024 as recycled transport logic, or the closed `2024` versus `2020` counterfactual screen.
It does **not** authorize runtime/config/default/policy/promotion work.

The only new question here was:

> if the exact D1 bank ceilings from the completed 2026-05-05 context-clean artifact are transported unchanged onto one exact late-2024 external surface, does any admitted claim field survive the unchanged `5 / 5 target + 0 / 6 anti-target` transport test there?

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-05`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** pressure-test the fixed D1 bank ceilings on one exact late-2024 external surface without threshold search, source widening, or runtime interpretation.
- **Candidate:** `fixed D1 bank ceilings on exact late-2024 external surface`
- **Base SHA:** `e958bd3e266830ecbc66150d1e5021c0a68df56c`
- **Skill Usage:** `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_precode_packet_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.md`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_late_2024_recurrence_falsifier_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`
- `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
- `results/evaluation/ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_2026-05-06.json`

## Exact commands run

- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_20260506.py tests/backtest/test_ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier.py`
- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier.py`
- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_20260506.py --base-sha e958bd3e266830ecbc66150d1e5021c0a68df56c`
- `(Get-FileHash results/evaluation/ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_2026-05-06.json -Algorithm SHA256).Hash ; rerun helper ; (Get-FileHash ...).Hash` -> identical replay hash `48C15691567F97CEF64F70E7026DB13ACA0863C3CA9F2CAF60B2AA7BFACED630`
- `c:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py tests/backtest/test_backtest_determinism_smoke.py tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

## Fixed late-2024 external surface

### Exact target rows (`5`)

- `2024-11-29T09:00:00+00:00`
- `2024-11-29T18:00:00+00:00`
- `2024-11-30T03:00:00+00:00`
- `2024-12-01T15:00:00+00:00`
- `2024-12-02T00:00:00+00:00`

Shared target context:

- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- zone = `low`
- candidate = `LONG`

### Exact anti-target rows (`6`)

`AGED_WEAK_CONTINUATION_GUARD` sibling rows (`4`):

- `2024-11-28T15:00:00+00:00`
- `2024-11-29T00:00:00+00:00`
- `2024-11-30T12:00:00+00:00`
- `2024-11-30T21:00:00+00:00`

Nearby stable context rows (`2`):

- true displacement row: `2024-12-01T00:00:00+00:00`
- stable blocked context row: `2024-12-01T06:00:00+00:00`

Exact external-surface lock:

- `5` target rows
- `6` anti-target rows
- `11` total locked rows
- additional unlabeled local rows = `0`

## Main result

### 1. The slice fails closed to `external_surface_falsified`

Final artifact status:

- `external_surface_falsified`

No admitted claim field survives the unchanged exact transport rubric on the late-2024 external surface.

### 2. No admitted claim field survives the unchanged `5 / 5 target + 0 / 6 anti-target` transport test

Transported D1 bank ceilings were locked to the completed 2026-05-05 context-clean artifact:

- `action_edge <= 0.033803`
- `confidence_gate <= 0.516902`
- `clarity_raw <= 0.364914`
- `clarity_score <= 36.0` (descriptive only)

Outcome on the exact late-2024 surface:

- admitted survivor fields: none
- admitted falsified fields: `action_edge`, `confidence_gate`
- not-evaluable admitted claim fields: `clarity_raw`
- descriptive-only fields remain descriptive only

### 3. `action_edge` stays directionally close, but fails exact transport on one target row

`action_edge` on the exact late-2024 surface:

- transported ceiling: `0.033803`
- selected target rows: `4 / 5`
- selected anti-target rows: `0 / 6`
- missed target row:
  - `2024-11-30T03:00:00+00:00` with `action_edge = 0.034684`

So the field remains locally consistent with the weak-signal direction, but it does **not** survive exact transport because the external surface contains one target row just above the frozen D1 bank ceiling.

### 4. `confidence_gate` fails at the same exact late-2024 target row

`confidence_gate` on the exact late-2024 surface:

- transported ceiling: `0.516902`
- selected target rows: `4 / 5`
- selected anti-target rows: `0 / 6`
- missed target row:
  - `2024-11-30T03:00:00+00:00` with `confidence_gate = 0.517342`

So the second admitted claim field reproduces the same shape as `action_edge`: close, clean on anti-target exclusion, but not exact on the external target side.

### 5. `clarity_raw` fails closed to `not_evaluable`

`clarity_raw` remains an admitted claim field in the frozen D1 bank, but it is absent on the late-2024 source artifact.
Therefore this slice records:

- `clarity_raw` admission on the external surface = `missing`
- `clarity_raw` claim status = `not_evaluable`
- no backfill
- no substitute field
- no inference

This absence does **not** by itself create slice-level authority in either direction.
It only removes `clarity_raw` from transport adjudication on this exact external surface.

### 6. `clarity_score` also misses one target row and stays descriptive only

`clarity_score` on the exact late-2024 surface:

- transported ceiling: `36.0`
- selected target rows: `4 / 5`
- selected anti-target rows: `0 / 6`
- missed target row:
  - `2024-11-30T03:00:00+00:00` with `clarity_score = 37.0`

So even the descriptive side read fails exact transport on the same row.
More importantly, it remains descriptive only and carries **no PASS/FAIL authority** regardless of its local shape.

## What changed relative to the completed D1 context-clean bank reread

The completed 2026-05-05 bank reread showed that on the exact frozen four-surface D1 bank, the target-bank ceilings stayed below the fixed context-bank minimum on `action_edge`, `confidence_gate`, and `clarity_raw`.

This slice adds one new bounded answer:

> the same fixed D1 bank ceilings do **not** survive exact unchanged transport on the first fresh late-2024 external surface, because both evaluable admitted claim fields miss the same exact target row and the third admitted claim field (`clarity_raw`) is absent there.

That matters because it separates:

- **internal exact-bank context-clean support**, from
- **external exact-surface portability**.

The D1 bank remains internally coherent.
It is simply **not yet external-surface clean** on this first fresh late-2024 test.

## Interpretation

The smallest honest read from this slice is:

> the current D1 line is stronger than a simple pair-local recurrence story, because the frozen bank survives its own context-clean reread, but it still fails exact unchanged transport on the first fresh late-2024 external surface.

That means the current D1 read is now best treated as:

- bounded exact-bank evidence
- observational only
- non-authoritative
- not yet transport-clean on fresh external surfaces
- insufficient for runtime/policy/promotion authority

## What this slice does **not** prove

This slice does **not** prove:

- that the D1 family is globally invalid
- that the D1 bank reread was wrong
- that `clarity_raw` is unimportant in general
- that a runtime weakening/strengthening rule should be proposed
- that March, July `2024`, or annual raw rereads should be reopened
- that late-2024 should keep widening as an open transport loop

## Next admissible step

The next honest move should now be one of only two shapes:

1. a bounded docs-only synthesis stating the current D1 state clearly: exact-bank context-clean support is real, but unchanged external-surface transport is now falsified on the first fresh late-2024 subject, or
2. one fresh governed packet on a second genuinely new exact external surface if the user explicitly wants another external falsifier.

What should stay closed after this slice:

- late-2024 as a recycled transport loop
- March subjects as primary loop
- July `2024` as primary subject
- runtime/config/default/promotion interpretation

## Validation notes

- exact late-2024 row lock held: `5` target + `6` anti-target = `11` rows with `0` unlabeled extras
- targeted hermetic test passed
- repo-standard smoke / determinism / feature-cache / pipeline selectors passed
- deterministic double-run hash proof held on the emitted JSON artifact:
  - `48C15691567F97CEF64F70E7026DB13ACA0863C3CA9F2CAF60B2AA7BFACED630`
- the emitted JSON artifact is still ignored by Git under the current `results/` ignore rule:
  - `!! results/evaluation/ri_policy_router_insufficient_evidence_d1_late_2024_external_surface_falsifier_2026-05-06.json`
- because that path remains git-ignored on the current repository surface, this slice treats the JSON as a regenerate-on-demand artifact rather than retained commit evidence; the verified double-run SHA256 for regeneration is `48C15691567F97CEF64F70E7026DB13ACA0863C3CA9F2CAF60B2AA7BFACED630`
- all claims in this note remain observational, bounded, and non-authoritative
