# Regime Intelligence challenger family — anchor decision candidate packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical decision-prep snapshot / consumed by later governance review summary / no active review authority`

> Current status note:
>
> - [HISTORICAL 2026-05-05] This file records an earlier anchor-decision prep surface on `feature/ri-role-map-implementation-2026-03-24`, not an active review authority on `feature/next-slice-2026-05-05`.
> - Its review role was later consumed by `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_anchor_decision_governance_review_summary_2026-03-26.md`.
> - Preserve this file as historical decision-prep provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: RI research-anchor selection influences the next governed search baseline, but this packet makes no runtime/default/champion change
- **Required Path:** `Quick`
- **Objective:** Refresh the RI challenger-family anchor-decision packet after slice9 so governance can decide whether the current RI local geometry should become the next research anchor, or whether one more falsification slice is still required.
- **Candidate:** `entry_conf_overall=0.27`, `regime_proba.balanced=0.36`, `hysteresis_steps=4`, `cooldown_bars=1`
- **Base SHA:** `4d545f82`

### Scope

- **Scope IN:** This packet only refreshes the anchor-decision question, the reviewed evidence inputs, the acceptance criteria for research-anchor adoption, and the stop conditions for deferring the decision after slice9.
- **Scope OUT:** No optimizer rerun, no runtime/default changes, no champion promotion, no config edits, no source-code edits, no retroactive reinterpretation of earlier slice artifacts into canonical approval.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_anchor_decision_candidate_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For any future anchor adoption that relies on this packet:

- exact pinned evidence references for slice7, slice8, and slice9
- explicit comparison versus incumbent same-head control
- explicit duplicate-ratio interpretation for both slice8 and slice9
- explicit statement that anchor adoption is research-local only unless a later packet broadens scope
- clean working tree at time of any later anchor enactment

### Stop Conditions

- Scope drift into promotion/default/champion/runtime behavior
- Any attempt to treat slice8 or slice9 evidence packaging as automatic canonical-anchor approval
- Missing or ambiguous reference to the tracked slice7, slice8, or slice9 summary artifacts
- Any proposal that changes optimizer defaults or search-space semantics without a separate governed packet

### Output required

- Reviewable refreshed anchor decision candidate packet
- Explicit recommendation branch: `adopt-slice8-backbone-as-research-anchor` or `require-one-more-falsification-slice`

## Purpose

This document refreshes the RI challenger-family anchor-decision question after slice9 execution packaging.

The question remains deliberately narrow:

> Should the RI challenger-family research workflow adopt the current slice8-backed local geometry as the next research anchor, or should governance require one more falsification slice before any anchor is chosen?

This packet is intentionally decision-preparatory only.

It does **not** approve canonical anchor adoption.
It does **not** approve promotion.
It does **not** approve champion cutover.
It does **not** modify any runtime/default behavior.

## Reviewed evidence inputs

The following tracked artifacts are the evidence basis for this refreshed decision packet:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice7_20260324.json`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice7_execution_outcome_signoff_summary_2026-03-24.md`
- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_execution_outcome_signoff_summary_2026-03-24.md`
- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice9_execution_outcome_signoff_summary_2026-03-26.md`

This refreshed packet treats those artifacts as authoritative for the currently reviewed March 24–26 RI challenger-family evidence line.

## Candidate local geometry under review

Candidate research-anchor geometry still centered on the slice8 local backbone:

- `thresholds.entry_conf_overall=0.27`
- `thresholds.regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`

Known governed interpretation:

- slice8 best-train neighborhood centered on this geometry (see `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `best_train.params`)
- slice8 validation winner also resolved to this geometry (see `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `validation_winner.params`)
- slice9 kept this same entry/gating backbone while reopening only a nearby management surface (see `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json` → `validation_winner.params`)
- slice9 preserved the RI high-water validation line on a nearby management tuple; it did **not** reproduce the slice8 management tuple and it did **not** canonically validate the anchor

## Why this decision is still open

Slice8 and slice9 strengthened the RI local winner in different ways, but neither created a new validation-score high-water mark.

Observed facts from tracked evidence:

- slice7 validation winner score: `0.26974911658712664`
- slice8 validation winner score: `0.26974911658712664`
- slice9 validation winner score: `0.26974911658712664`
- slice7 duplicate ratio: `0.90625`
- slice8 duplicate ratio: `0.2604166666666667`
- slice9 duplicate ratio: `0.3466666666666667`
- slice9 differed from the slice8 management tuple while staying at the same validation line
- slice8 and slice9 both remained above:
  - slice6 plateau `0.23646934335498004`
  - incumbent same-head control `0.2616884080730424`

Therefore the open governance question is still not "did the line print a new raw score high?".

The real question is now:

> Is repeated preservation of the RI high-water validation line across both a bounded widen-search and a nearby management-surface falsification sufficient to adopt the current backbone as the next research anchor?

## Decision options under governance review

### Option A — adopt the slice8 backbone as research anchor

Governance may choose this option if it accepts the following reasoning:

- the validation winner remained at the best currently reproduced RI level across slice7, slice8, and slice9
- slice8 showed that the local winner survived a meaningfully broader, lower-duplicate nearby search
- slice9 showed that the same entry/gating backbone also survived a nearby management-surface probe on a **non-slice8 management tuple** (`8 / 0.40 / 0.38` rather than `8 / 0.42 / 0.40` on the reopened axes)
- anchor adoption remains research-local only and does not imply promotion/default/champion approval

If Option A is later approved, the approved meaning must be limited to:

- this backbone becomes the next RI challenger-family research anchor for future slices
- future challenger/falsification slices may branch from this anchor under separate governed packets
- runtime/default behavior remains unchanged

### Option B — require one more falsification slice before anchor choice

Governance may choose this option if it concludes that:

- repeated equal-score runs are still too weak without a fresh score improvement, or
- slice9 duplicate behavior degrading versus slice8 weakens the case for adopting the current backbone now, or
- the remaining metadata quirk (`merged_config.strategy_family=legacy`) should be audited first, or
- governance wants one more intentionally adversarial falsification slice before freezing any research anchor

If Option B is chosen, the next slice should be explicitly framed as:

- a falsification attempt against the current `0.27 / 0.36 / 4 / 1` entry/gating backbone
- still no promotion/default/champion scope
- success defined either by disproving this backbone or by strengthening the case that it deserves research-anchor status

## Acceptance criteria for future research-anchor adoption

Research-anchor adoption should only be considered eligible if governance can affirm all of the following:

1. The tracked slice7, slice8, and slice9 artifacts are sufficient and mutually consistent.
2. Slice8 duplicate-ratio improvement is interpreted as meaningful local robustness evidence, not measurement noise.
3. Slice9 is interpreted correctly as preserving the RI high-water validation line on a nearby management tuple, not as reproducing the slice8 management tuple and not as canonical validation.
4. The anchor meaning is explicitly limited to research-anchor status only.
5. No runtime/default/champion/config change is smuggled in through the anchor wording.
6. Any remaining metadata quirk or artifact-label ambiguity is either documented as non-blocking or separately escalated.

## Current recommendation

Current packet-level recommendation from the presently pinned slice7–slice9 evidence is `adopt-slice8-backbone-as-research-anchor`; this is a decision recommendation only and does not itself enact anchor adoption.

Reasoning:

- slice8 reproduced the slice7-level governed winner while materially reducing duplicate collapse
- slice9 preserved that same RI high-water validation line on a nearby management tuple rather than only on the slice8 management settings
- slice8 and slice9 both continue to outperform slice6 and the incumbent same-head control on validation score
- treating the current backbone as the research anchor best fits the present evidence while still keeping canonical anchor / promotion / default questions strictly out of scope

## Residual risks

### 1. No fresh score breakout

The recommendation still relies on robustness evidence rather than a higher validation score.

Implication:

- governance must explicitly accept repeated equal-score robustness evidence as sufficient for research-anchor selection
- otherwise the correct outcome remains Option B

### 2. Slice9 duplicate ratio degraded versus slice8

Slice9 broadened robustness evidence on the management surface, but it did not improve search cleanliness versus slice8.

Implication:

- slice9 is better read as falsification evidence than as a cleaner next anchor packet by itself
- governance may still reasonably ask for one more falsification slice if lower-duplicate robustness remains a priority

### 3. Metadata quirk remains open

Tracked run artifacts still show `merged_config.strategy_family=legacy`.

Implication:

- this packet does not reinterpret that field
- this packet only records that the quirk appears pre-existing and non-blocking for slice8/slice9 execution packaging only
- a later promotion-grade packet should not ignore it

### 4. Anchor scope could be over-read

There is a risk that "anchor" gets interpreted as approval for promotion or runtime use.

Implication:

- any governance decision on this packet must restate that anchor approval is research-local only
- any broader interpretation requires a separate packet

## Requested governance response shape

A governance response to this packet should choose exactly one of the following:

- `APPROVE_OPTION_A` — adopt the current slice8-backed backbone as research anchor only
- `APPROVE_OPTION_B` — require one more falsification slice before anchor choice
- `BLOCKED` — evidence or framing is insufficient; specify the minimal missing inputs

## Next step after review

If governance returns `APPROVE_OPTION_A`:

- open the next RI slice from the refreshed research anchor with explicit no-promotion/no-runtime-change constraints

If governance returns `APPROVE_OPTION_B`:

- prepare one more governed falsification slice against the same entry/gating backbone

If governance returns `BLOCKED`:

- resolve only the named evidence gap and re-submit the packet
