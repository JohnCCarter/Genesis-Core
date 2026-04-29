# Feature Attribution — post-Phase-14 Phase 1 rebaseline reconciliation packet

Date: 2026-04-02
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase1-proposed / docs-plus-artifact / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this slice creates a new reconciliation memo that becomes the canonical restart bridge between historical FA-v1 evidence and current executable-route evidence; no runtime authority is created, but provenance drift would be harmful if phrased loosely.
- **Required Path:** `Quick`
- **Objective:** Produce one deterministic reconciliation memo that separates the frozen historical FA-v1 baseline from the current executable-route baseline and records the first replay-candidate ordering for future governed review.
- **Candidate:** `FA post-Phase-14 rebaseline reconciliation`
- **Base SHA:** `b7a6a7de`

### Scope

- **Scope IN:**
  - `docs/governance/feature_attribution_post_phase14_phase1_rebaseline_reconciliation_packet_2026-04-02.md`
  - `docs/analysis/feature_attribution_post_phase14_rebaseline_reconciliation_2026-04-02.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - any reruns, fresh probes, or regenerated experiment outputs
  - any edits to existing locked FA-v1 reports/manifests
  - any promotion/readiness/runtime-authority claims
  - any reopening of fib discovery, tuning, or promotion
- **Expected changed files:**
  - `docs/governance/feature_attribution_post_phase14_phase1_rebaseline_reconciliation_packet_2026-04-02.md`
  - `docs/analysis/feature_attribution_post_phase14_rebaseline_reconciliation_2026-04-02.md`
- **Max files touched:** `2`

### Constraints

- existing cited artifacts only; no new executions
- frozen historical baseline and current executable-route baseline must be named separately every time they are compared
- all metrics must reconcile exactly to the cited synthesis report/manifest
- the memo must remain observational and restart-oriented only
- the memo may record next-candidate ordering for future governed review only, but may not authorize replay execution by itself
- no new verdict stronger than the cited evidence

### Skill Usage

- Repo-local skill anchors used as read-only/checklist support only:
  - `.github/skills/ri_off_parity_artifact_check.json`
  - `.github/skills/feature_parity_check.json`
- These anchors do not replace gates for this slice and do not expand scope.

### Required memo structure

The reconciliation memo must contain exactly these sections:

1. purpose and boundary
2. frozen historical baseline
3. current executable-route baseline
4. baseline drift summary
5. current-route activity ranking
6. restart interpretation under Phase 14
7. locked next-candidate order
8. bottom line

### Gates required

For this slice:

- markdown/path sanity
- exact reconciliation check against cited metrics in the synthesis report/manifest
- manual wording audit that the memo is observational only
- manual wording audit that candidate ordering is presented as restart priority, not execution authority
- scope audit that only the packet and the new memo are changed

### Stop Conditions

- any wording that treats frozen and current-route baselines as the same surface
- any metric that does not reconcile exactly to the cited synthesis artifacts
- any wording that upgrades the memo into replay authority
- any wording that presents `emergent_system_behavior` as disproving all residual hypotheses
- any need for reruns or fresh artifacts to complete the memo

### Output required

- one reviewable Phase 1 packet
- one reviewable rebaseline reconciliation memo
- explicit recorded first-candidate ordering for future governed review
- explicit statement of how the memo relates to Phase 14 without overruling it

## What this packet does

This slice creates the missing bridge between:

- the existing FA-v1 governed synthesis
- the post-Phase-14 edge-origin conclusion
- the next restart candidate (`Volatility sizing cluster`)

It is the first real restart slice, but it remains documentation-plus-artifact only.

## Locked evidence basis

The packet-locked evidence basis is:

- frozen historical baseline metrics from the FA-v1 synthesis manifest
- current executable-route baseline metrics from the same synthesis surface
- current-route activity ranking from the FA-v1 synthesis/operator summary
- Phase 14 structural conclusion from `EDGE_ORIGIN_REPORT.md`

The following surfaces are **citation-only / read-only evidence** for this slice and are not in edit scope:

- `results/research/feature_attribution_v1/reports/fa_v1_full_admitted_units_synthesis_20260331_01.md`
- `results/research/feature_attribution_v1/reports/fa_v1_operator_summary_20260331_01.md`
- `results/research/feature_attribution_v1/manifests/fa_v1_full_admitted_units_synthesis_20260331_01.json`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`
- `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`

## Exact restart question

The only question this slice answers is:

> What from FA-v1 is historical-only, what remains portable to the current executable route, and which candidate should be replayed first under the post-Phase-14 frame?

This slice does not answer whether a replayed candidate should later be changed, removed, promoted, or tuned.

## Locked expected conclusion shape

The memo is allowed to conclude only along these lines:

- the frozen historical FA-v1 route and the current executable route are distinct
- the current executable-route ranking should drive restart priority
- `Volatility sizing cluster` is the first replay candidate
- `Signal-adaptation threshold cluster` is the second replay candidate
- Phase 14 remains the broader system-level interpretation frame

This memo records the first replay-candidate ordering for future governed review only. It does not authorize execution, reruns, promotion, readiness, or runtime changes.

## Bottom line

This packet opens the first admissible post-roadmap work product: a deterministic reconciliation memo that prevents restart work from mixing historical FA-v1 evidence with the current executable route.
