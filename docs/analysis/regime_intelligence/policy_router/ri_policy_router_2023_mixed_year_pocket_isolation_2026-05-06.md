# RI policy router 2023 mixed-year pocket isolation

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-05`
Mode: `RESEARCH`
Status: `completed / helper-backed / bounded annual decomposition`

This note closes one bounded annual decomposition question on the exact curated `2023` enabled-vs-absent action-diff surface:

> does the mixed `2023` annual surface materially concentrate into one December-anchored shared-shape pocket when we count only the pre-registered low-zone suppression and continuation-displacement families?

It does **not** reopen the spent D1 line.
It does **not** authorize runtime/default/config/policy/promotion work.
It does **not** claim transport-clean or runtime-ready authority.

Its purpose is narrower:

> state the smallest honest read of whether mixed `2023` compresses into one December-centered annual shared-shape pocket, while keeping the full-month ranking visible and the fixed December anchor overlap explicit.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-05`
- **Risk:** `MEDIUM`
- **Required Path:** `approved non-trivial RESEARCH helper-backed evidence path`
- **Lane:** `Research-evidence`
- **Objective:** test whether mixed `2023` materially concentrates into one December-anchored shared-shape pocket on the exact annual surface.
- **Candidate:** `2023 mixed-year pocket isolation`
- **Base SHA:** `e958bd3e266830ecbc66150d1e5021c0a68df56c`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED` on `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_precode_packet_2026-05-06.md`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_precode_packet_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_bounded_contribution_evidence_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `scripts/analyze/ri_policy_router_2023_mixed_year_pocket_isolation_20260506.py`
- `tests/backtest/test_ri_policy_router_2023_mixed_year_pocket_isolation.py`
- regenerate-on-demand artifact: `results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json`

## Fixed family definition

Only the following pre-registered families were counted on the exact annual `2023` action-diff surface:

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
The note keeps the full month ranking visible rather than forcing a December-only lens.

## Measured annual result

### 1. December is the top combined month, but not by enough to collapse the year into a single-pocket story

On the exact annual `2023` surface, the fixed shared-shape family contributes `317` counted rows in total.

Combined month ranking top section:

- `2023-12` -> `38`
- `2023-06` -> `33`
- `2023-08` -> `33`
- `2023-07` -> `32`
- `2023-04` -> `30`
- `2023-05` -> `30`
- `2023-11` -> `30`

So December is first, but only at `38 / 317 = 11.9874%` of the counted shared-shape mass.
That is a real concentration signal, but not a year-collapsing monopoly.

### 2. The continuation side is what actually peaks in December

Continuation-displacement month ranking begins:

- `2023-12` -> `22`
- `2023-07` -> `18`
- `2023-05` -> `17`
- `2023-08` -> `15`
- `2023-06` -> `14`

So December is the top continuation month at `22 / 144 = 15.2778%` of continuation rows.

### 3. The suppression side does **not** peak in December

Suppression month ranking begins:

- `2023-06` -> `19`
- `2023-04` -> `18`
- `2023-08` -> `18`
- `2023-11` -> `18`
- `2023-03` -> `16`
- `2023-10` -> `16`
- `2023-12` -> `16`

So the suppression component peaks in June, not December.
That matters because it means the combined December lead is carried by the continuation side plus a still-large but non-leading December suppression pocket.

### 4. The remembered fixed December anchor set does **not** cleanly map onto the annual family

The fixed December anchor timestamps were:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`
- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

Exact annual-surface result:

- only `2023-12-20T03:00:00+00:00` appears on the annual surface as a counted shared-shape row
- that surviving overlap is a low-zone `suppression` row with switch reason `insufficient_evidence`
- the other four remembered anchor timestamps are absent from the annual counted surface entirely

So the annual December concentration is real, but it is **not** the same thing as saying the previously remembered fixed December anchor set cleanly reappears as one annual cluster.

## Annual comparison context

The locked annual comparison remains the same curated `2023` subject already used to choose this mixed-year slice:

- enabled total return: `0.9902908234750066%`
- absent total return: `1.784507508825045%`
- enabled profit factor: `2.0258867738235318`
- absent profit factor: `2.419239619119911`
- action diff count: `701`
- reason-only diff count: `2092`

This slice does **not** reinterpret those annual performance deltas as a runtime rule.
It only decomposes where the fixed shared-shape family mass sits inside the exact annual surface.

## Honest synthesis

The smallest honest reading is now:

> mixed `2023` does show a real December-centered concentration on the exact annual shared-shape surface, but that concentration is only partial: December leads the combined ranking and the continuation side, while suppression peaks elsewhere, and the remembered fixed December anchor set mostly does not survive as a one-to-one annual overlap.

That is stronger than saying “December was just anecdotal.”
It is weaker than saying “mixed 2023 is basically one clean December pocket.”

## What this slice now supports

This slice now supports all of the following bounded statements:

1. mixed `2023` is not evenly distributed across months on the fixed annual shared-shape surface
2. December is the top **combined** month with exact count `38`
3. December is the top **continuation** month with exact count `22`
4. suppression does **not** peak in December; June is the top suppression month with exact count `19`
5. the annual December concentration therefore reflects a mixed composition rather than one pure suppression cluster
6. only one fixed remembered December anchor timestamp overlaps the annual counted family:
   - `2023-12-20T03:00:00+00:00`
7. the annual result remains observational only and non-authoritative

## What this slice does **not** support

This slice does **not** support any of the following:

- a claim that mixed `2023` reduces to one clean remembered December anchor set
- a claim that December alone explains the full annual sign
- a transport-clean or runtime-ready discriminator claim
- runtime/default/config/policy/family/champion/promotion authority
- reopening the spent D1 line by analogy

## Artifact retention and reproducibility

The helper emitted:

- `results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json`

Deterministic rerun hash on the same input/base SHA:

- SHA256 before rerun: `3B3C3993CE314377C44A9021851E3A7CA2FADC3D0567E72474FF3DBCB4BBD9C8`
- SHA256 after rerun: `3B3C3993CE314377C44A9021851E3A7CA2FADC3D0567E72474FF3DBCB4BBD9C8`

Git visibility check on this artifact returned:

- `!! results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json`
- ignore source: `.gitignore:232:results/`

So the correct retention posture remains:

- **regenerate on demand**, unless the ignore policy is intentionally repaired or the artifact is force-added under an explicitly governed evidence step.

## Re-anchor verdict

The correct current `2023` read is therefore:

- mixed-year decomposition complete on the exact annual surface
- December leads combined shared-shape mass
- December leads continuation displacement specifically
- suppression leadership sits outside December
- fixed remembered December anchors mostly do not survive as annual overlap
- category unchanged: observational only, non-authoritative

That makes this a useful bounded annual decomposition, not a runtime opening and not a proof that mixed `2023` is simply one December pocket wearing a fake moustache.
