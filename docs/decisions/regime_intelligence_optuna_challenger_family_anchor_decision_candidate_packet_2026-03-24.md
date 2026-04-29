# Regime Intelligence challenger family — anchor decision candidate packet

Date: 2026-03-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `prep-only / ready_for_governance_review / no anchor approved by this packet`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `MED` — why: RI research-anchor selection influences the next governed search baseline, but this packet makes no runtime/default/champion change
- **Required Path:** `Quick`
- **Objective:** Prepare a reviewable decision packet for whether the current RI challenger-family local geometry should become the next research anchor after slice8, or whether one more falsification slice is required before any anchor choice.
- **Candidate:** `entry_conf_overall=0.27`, `regime_proba.balanced=0.36`, `hysteresis_steps=4`, `cooldown_bars=1`
- **Base SHA:** `9c1f9d3b76f19194217bdab629a30f3f62bf107a`

### Scope

- **Scope IN:** This packet only defines the anchor-decision question, the reviewed evidence inputs, the acceptance criteria for anchor adoption, and the stop conditions for deferring the decision.
- **Scope OUT:** No optimizer rerun, no runtime/default changes, no champion promotion, no config edits, no source-code edits, no retroactive reinterpretation of earlier slice artifacts.
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_challenger_family_anchor_decision_candidate_packet_2026-03-24.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For any future anchor adoption that relies on this packet:

- exact pinned evidence references for slice7 and slice8
- explicit comparison versus incumbent same-head control
- explicit duplicate-ratio interpretation
- explicit statement that anchor adoption is research-local only unless a later packet broadens scope
- clean working tree at time of any later anchor enactment

### Stop Conditions

- Scope drift into promotion/default/champion/runtime behavior
- Any attempt to treat slice8 evidence packaging as automatic anchor approval
- Missing or ambiguous reference to the tracked slice7 or slice8 summary artifacts
- Any proposal that changes optimizer defaults or search-space semantics without a separate governed packet

### Output required

- Reviewable anchor decision candidate packet
- Explicit recommendation branch: `adopt-slice8-as-research-anchor` or `require-one-more-falsification-slice`

## Purpose

This document prepares the next governance decision after slice8 execution packaging.

The question is deliberately narrow:

> Should the RI challenger-family research workflow adopt the slice8 local geometry as the next research anchor, or should governance require one more falsification slice before any anchor is chosen?

This packet is intentionally decision-preparatory only.

It does **not** approve anchor adoption.
It does **not** approve promotion.
It does **not** approve champion cutover.
It does **not** modify any runtime/default behavior.

## Reviewed evidence inputs

The following tracked artifacts are the evidence basis for this decision packet:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice7_20260324.json`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice7_execution_outcome_signoff_summary_2026-03-24.md`
- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_execution_outcome_signoff_summary_2026-03-24.md`

The decision packet treats those artifacts as authoritative for the currently reviewed March 24 RI challenger-family evidence line.

## Candidate local geometry under review

Candidate anchor geometry derived from slice8 tracked evidence:

- `thresholds.entry_conf_overall=0.27`
- `thresholds.regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`

Known governed interpretation:

- slice8 best-train neighborhood centered on this geometry (see `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `best_train.params`)
- slice8 validation winner also resolved to this geometry (see `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `validation_winner.params`)
- validation winner score: `0.26974911658712664`

## Why this decision is open

Slice8 improved search quality materially but did not create a new validation-score high-water mark.

Observed facts from tracked evidence:

- slice7 validation winner score: `0.26974911658712664`
- slice8 validation winner score: `0.26974911658712664`
- slice7 duplicate ratio: `0.90625`
- slice8 duplicate ratio: `0.2604166666666667`
- slice8 still beat:
  - slice6 plateau `0.23646934335498004`
  - slice4 plateau `0.22516209452403432`
  - slice3 plateau `0.22289051935876203`
  - incumbent same-head control `0.2616884080730424`

Therefore the open governance question is not "did slice8 win on raw score?".

The real question is:

> Is equal score with dramatically better search-quality evidence sufficient to adopt the slice8 geometry as the next research anchor?

## Decision options under governance review

### Option A — adopt slice8 as research anchor

Governance may choose this option if it accepts the following reasoning:

- the validation winner remained at the best currently reproduced level
- the same winning geometry survived a meaningfully broader, lower-duplicate search
- the duplicate-ratio improvement is strong enough to treat the geometry as more robust, not just lucky
- anchor adoption remains research-local only and does not imply promotion/default/champion approval

If Option A is later approved, the approved meaning must be limited to:

- this geometry becomes the next RI challenger-family research anchor for future slices
- future challenger/falsification slices may branch from this anchor under separate governed packets
- runtime/default behavior remains unchanged

### Option B — require one more falsification slice before anchor choice

Governance may choose this option if it concludes that:

- matching slice7 is still too weak without a fresh score improvement, or
- the duplicate-ratio improvement alone is insufficient to justify anchor adoption, or
- the remaining metadata quirk (`merged_config.strategy_family=legacy`) should be audited first, or
- the evidence should be stress-tested by one more intentionally adversarial slice before freezing a research anchor

If Option B is chosen, the next slice should be explicitly framed as:

- a falsification attempt against the `0.27 / 0.36 / 4 / 1` local geometry
- still no promotion/default/champion scope
- success defined either by disproving this geometry or by strengthening the case that it deserves anchor status

## Acceptance criteria for future anchor adoption

Anchor adoption should only be considered eligible if governance can affirm all of the following:

1. The tracked slice7 and slice8 artifacts are sufficient and mutually consistent.
2. The slice8 duplicate-ratio improvement is interpreted as meaningful robustness evidence, not measurement noise.
3. The anchor meaning is explicitly limited to research-anchor status only.
4. No runtime/default/champion/config change is smuggled in through the anchor wording.
5. Any remaining metadata quirk or artifact-label ambiguity is either documented as non-blocking or separately escalated.

## Current recommendation

Current packet-level recommendation from the evidence assembled so far:

- `adopt-slice8-as-research-anchor`, with the scope explicitly limited to RI research anchoring only and subject to separate governance approval

Reasoning:

- slice8 reproduced the slice7-level governed winner
- slice8 did so with dramatically less duplicate collapse
- slice8 continues to outperform slice6, slice4, slice3, and the incumbent same-head control on validation score
- treating slice8 as the research anchor best fits the current evidence while still keeping promotion/default questions strictly out of scope

## Residual risks

### 1. No fresh score breakout

The recommendation relies on search-quality improvement rather than a higher validation score.

Implication:

- governance must explicitly accept robustness evidence as sufficient for research-anchor selection
- otherwise the correct outcome is Option B

### 2. Metadata quirk remains open

Tracked run artifacts still show `merged_config.strategy_family=legacy`.

Implication:

- this packet does not reinterpret that field
- this packet only records that the quirk appears pre-existing and non-blocking for slice8 execution packaging only
- a later promotion-grade packet should not ignore it

### 3. Anchor scope could be over-read

There is a risk that "anchor" gets interpreted as approval for promotion or runtime use.

Implication:

- any governance decision on this packet must restate that anchor approval is research-local only
- any broader interpretation requires a separate packet

## Requested governance response shape

A governance response to this packet should choose exactly one of the following:

- `APPROVE_OPTION_A` — adopt slice8 geometry as research anchor only
- `APPROVE_OPTION_B` — require one more falsification slice before anchor choice
- `BLOCKED` — evidence or framing is insufficient; specify the minimal missing inputs

## Next step after review

If governance returns `APPROVE_OPTION_A`:

- open the next RI slice from the slice8 research anchor with explicit no-promotion/no-runtime-change constraints

If governance returns `APPROVE_OPTION_B`:

- prepare one more governed falsification slice against the same local geometry

If governance returns `BLOCKED`:

- resolve only the named evidence gap and re-submit the packet
