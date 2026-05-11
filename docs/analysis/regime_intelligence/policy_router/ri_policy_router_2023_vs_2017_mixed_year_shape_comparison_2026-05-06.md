# RI policy router 2023 vs 2017 mixed-year shape comparison

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `completed / helper-backed / bounded annual comparison`

This note closes one bounded cross-year question on the exact curated annual enabled-vs-absent action-diff surfaces for the only two mixed **full** years already named in the curated annual evidence note:

> when the fixed shared-shape families are counted on the exact annual surfaces for `2017` and `2023`, is the completed `2023` read — December-led combined mass, December-led continuation displacement, and June-led suppression — actually distinctive, or is that simply what a mixed annual surface looks like on the same family definition?

It does **not** reopen the spent D1 line.
It does **not** widen beyond `2017` and `2023`.
It does **not** authorize runtime/default/config/policy/promotion work.
It does **not** claim transport-clean or runtime-ready authority.

Its purpose is narrower:

> determine whether the two mixed annual surfaces share the same top-month shape, or whether the overlap is limited to one component while the combined and continuation tops diverge.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW`
- **Required Path:** `approved non-trivial RESEARCH helper-backed evidence path`
- **Lane:** `Research-evidence`
- **Objective:** compare the fixed shared-shape month composition of annual `2023` versus annual `2017` on the exact curated enabled-vs-absent action-diff surfaces
- **Candidate:** `2023 vs 2017 mixed-year shape comparison`
- **Base SHA:** `0d8b665cf8d16b76b7c22775fd2a159130ad463e`
- **Skill Usage:** `python_engineering`, `decision_gate_debug`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES` on `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_precode_packet_2026-05-06.md`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_precode_packet_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
- `scripts/analyze/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_20260506.py`
- `tests/backtest/test_ri_policy_router_2023_vs_2017_mixed_year_shape_comparison.py`
- regenerate-on-demand artifact: `results/evaluation/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.json`

## Fixed family definition

Only the following pre-registered families were counted on the exact annual surfaces for both years:

1. **suppression**
   - absent action: `LONG`
   - enabled action: `NONE`
   - zone: `low`
   - switch reason in `{insufficient_evidence, AGED_WEAK_CONTINUATION_GUARD}`
2. **continuation displacement**
   - absent action: `NONE`
   - enabled action: `LONG`
   - zone: `low`
   - switch reason: `stable_continuation_state`

No other families were counted.
No year search was widened beyond `2017` and `2023`.

## Measured annual result

### 1. The two mixed years do **not** share the same top combined month

Counted-row totals on the fixed family surface:

- `2017`: `381` counted rows
- `2023`: `317` counted rows

Combined month ranking top section for `2017`:

- `July` -> `42` (`11.0236%`)
- `March` -> `41` (`10.7612%`)
- `August` -> `39` (`10.2362%`)
- `December` -> `38` (`9.9738%`)
- `June` -> `37` (`9.7113%`)

Combined month ranking top section for `2023`:

- `December` -> `38` (`11.9874%`)
- `June` -> `33` (`10.4101%`)
- `August` -> `33` (`10.4101%`)
- `July` -> `32` (`10.0946%`)
- `April` -> `30` (`9.4637%`)

So the two mixed years diverge immediately at the combined top:

- `2017` top combined month = `July`
- `2023` top combined month = `December`

That means the completed `2023` December-led combined read is **not** just a generic mixed-year template on the only other mixed full-year control.

### 2. June-led suppression is **shared**, not unique to 2023

Suppression month ranking top section for `2017`:

- `June` -> `30` (`11.4943%`)
- `August` -> `27` (`10.3448%`)
- `July` -> `26` (`9.9617%`)
- `March` -> `24` (`9.1954%`)
- `December` -> `24` (`9.1954%`)

Suppression month ranking top section for `2023`:

- `June` -> `19` (`10.9827%`)
- `April` -> `18` (`10.4046%`)
- `August` -> `18` (`10.4046%`)
- `November` -> `18` (`10.4046%`)
- `March` -> `16` (`9.2486%`)

So the exact cross-year comparison says:

- `2017` top suppression month = `June`
- `2023` top suppression month = `June`

This is the most important overlap in the slice.
The June-led suppression feature is therefore **shared across both mixed years**, not a `2023`-only signature.

### 3. The continuation side is where the divergence sharpens most clearly

Continuation-displacement month ranking top section for `2017`:

- `March` -> `17` (`14.1667%`)
- `July` -> `16` (`13.3333%`)
- `December` -> `14` (`11.6667%`)
- `October` -> `13` (`10.8333%`)
- `August` -> `12` (`10.0000%`)

Continuation-displacement month ranking top section for `2023`:

- `December` -> `22` (`15.2778%`)
- `July` -> `18` (`12.5000%`)
- `May` -> `17` (`11.8056%`)
- `August` -> `15` (`10.4167%`)
- `June` -> `14` (`9.7222%`)

So the continuation tops are different as well:

- `2017` top continuation month = `March`
- `2023` top continuation month = `December`

That makes the `2023` December-led continuation read look genuinely distinctive relative to the only other mixed full-year control, even while suppression itself is shared.

### 4. December means different things in the two mixed years

On the exact combined ranking:

- `2023` December rank = `1`
- `2017` December rank = `4`

So December is still materially present in `2017`, but it does **not** dominate the mixed-year shape there the way it does in the completed `2023` annual read.

## Exact cross-year comparison verdict

The helper returned:

- status = `mixed_year_shape_differs_between_2017_and_2023`
- `same_top_combined_month_set = false`
- `same_top_continuation_month_set = false`
- `same_top_suppression_month_set = true`

On the exact `2017` vs `2023` mixed-year monthly action-diff surface only, the helper resolved `status = mixed_year_shape_differs_between_2017_and_2023`. This is observational research evidence only; it does **not** authorize runtime/default changes, D1 widening, or widening beyond `2017` / `2023`.

That is the cleanest summary of the slice:

> the two mixed years share the same suppression lead (`June`), but they do **not** share the same combined or continuation lead. `2023` is December-led on combined mass and continuation displacement, while `2017` is July-led on combined mass and March-led on continuation displacement.

## Honest synthesis

The smallest honest reading is now:

> `2023` is not merely “another mixed year with June suppression.” The exact control comparison shows a split result: the suppression side overlaps with `2017`, but the combined and continuation tops diverge. So the strongest `2023`-specific signal on this bounded annual surface is the December-led continuation-plus-combined shape, not June suppression by itself.

That is stronger than saying “mixed years all look alike.”
It is weaker than claiming a runtime-ready or transport-clean discriminator.

## What this slice now supports

This slice now supports all of the following bounded statements:

1. the only two mixed **full** years on the curated annual surface do **not** share the same top combined month
2. `2023` remains December-led on the combined annual shape
3. `2023` remains December-led on the continuation side specifically
4. June-led suppression is **shared** by both mixed years and is therefore not distinctive to `2023`
5. the exact cross-year divergence sits in the combined and continuation tops, not in suppression
6. the result remains observational only and non-authoritative

## What this slice does **not** support

This slice does **not** support any of the following:

- a claim that June suppression makes `2023` unique among mixed years
- a claim that `2017` confirms a generic December-led mixed-year template
- a runtime/default/config/policy/family/champion/promotion claim
- a widening beyond `2017` and `2023` without a fresh packet
- a transport-clean discriminator claim from annual composition alone

## Validation and retention

Focused validation completed:

- `pytest tests/backtest/test_ri_policy_router_2023_vs_2017_mixed_year_shape_comparison.py` -> `3 passed`
- helper execution on the exact repo-visible annual surfaces -> passed
- deterministic artifact replay -> passed

Deterministic rerun hash on the same input/base SHA:

- SHA256 before rerun: `8EEC3D4895BA872FEF3DF80F4C03564310C75370E6558D5226547A0C6E6C171C`
- SHA256 after rerun: `8EEC3D4895BA872FEF3DF80F4C03564310C75370E6558D5226547A0C6E6C171C`

Git visibility check on this exact artifact returned:

- `!! results/evaluation/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.json`
- ignore source: `.gitignore:232:results/`

So the correct retention posture remains:

> `results/evaluation/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.json` is treated as **regenerate-on-demand** unless intentionally force-added for retention. Do **not** assume normal staging.

Reproducibility for that ignored artifact is anchored by SHA256 `8EEC3D4895BA872FEF3DF80F4C03564310C75370E6558D5226547A0C6E6C171C` from two identical replays on the same base SHA.

Feature-cache invariance and pipeline invariant checks are **N/A by scope** for this slice because `src/**`, config-authority, runtime/default, and backtest execution surfaces are untouched; the helper reads only fixed JSON inputs.

## Re-anchor verdict

The correct current mixed-year annual read is therefore:

- `2023` and `2017` do **not** share the same top combined month
- `2023` and `2017` do **not** share the same top continuation month
- `2023` and `2017` **do** share the same top suppression month (`June`)
- `2023` remains December-led on combined mass and continuation displacement
- the strongest `2023`-specific signal on this bounded annual surface is the December-led combined/continuation shape rather than June suppression
- category unchanged: observational only, non-authoritative

That makes this a useful bounded cross-year comparison, not a runtime opening and not proof that mixed-year annual shape alone can carry policy authority. It is, however, a much better lie detector than pretending all mixed years wear the same seasonal costume.
