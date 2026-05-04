# RI policy router structural research roadmap

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Status: `reference / partially superseded / non-executable / no authorization`

> Current status note:
>
> - This roadmap still governs source precedence between `Genesis-Core router research — codebase-aware re-evaluation.md` and `genesis_core_router_research.md`.
> - Its follow-up sequencing is partially superseded wherever later anchored evidence or `GENESIS_WORKING_CONTRACT.md` differs.
> - Keep it as a reference planning note, not as the current execution order for the active `continuation_release_hysteresis` lane.

This document is a planning artifact in `RESEARCH` and grants no implementation, runtime, readiness, launch, paper-trading, cutover, or promotion authority.
It exists to answer one narrow question only:

- which research note should drive the next RI policy-router line, and in what exact order should follow-up work proceed?

## COMMAND PACKET (planning-only, non-executable)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: single-file docs-only sequencing artifact; the main risk is wording drift that could be misread as runtime authority or as reopening already-closed evidence loops
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the user asked for a clear planning map across two existing research notes, not for a fresh evidence run or runtime packet
- **Objective:** define source precedence and a fail-closed roadmap for future RI policy-router research follow-up after the 2026-04-30 evidence chain
- **Candidate:** `RI policy-router structural follow-up roadmap`
- **Base SHA:** `9ae9451d9d4d063db874ce14498a756209a2dd07`

### Concept lane

- **Hypotes / idé:** the codebase-aware re-evaluation note should become the primary planning driver, while the generic structural research note should remain a background idea bank only
- **Varför det kan vara bättre:** the second note is already grounded in Genesis-Core architecture and RI lane choices, but it needs to be interpreted through the latest anchored 2026-04-30 evidence notes rather than treated as a self-sufficient next-step authority
- **Vad skulle falsifiera idén:** if the latest anchored evidence actually re-opened the generic note as the more truthful execution driver, or if the codebase-aware note proved materially inconsistent with the current validated lane
- **Billigaste tillåtna ytor:** `docs/analysis/regime_intelligence/policy_router/**`, `docs/decisions/regime_intelligence/policy_router/**`, `GENESIS_WORKING_CONTRACT.md`, existing read-only evidence anchors
- **Nästa bounded evidence-steg:** one new bounded `insufficient_evidence` counterfactual-screen packet on a genuinely new surface, not a reopen of the closed March 2021 / March 2025 discriminator loop

### Scope

- **Scope IN:** this roadmap only; source-precedence decision; explicit sequencing; stop conditions; explicit non-goals; explicit mapping from the two research notes onto the current validated repo state
- **Scope OUT:** all code/config/test/runtime changes; all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**`; all new evidence execution; all runtime packet authority; all readiness/promotion/cutover claims
- **Expected changed files:** `docs/analysis/regime_intelligence/policy_router/ri_policy_router_structural_research_roadmap_2026-04-30.md`
- **Max files touched:** `1`

### Gates required

- `pre-commit run --files docs/analysis/regime_intelligence/policy_router/ri_policy_router_structural_research_roadmap_2026-04-30.md`
- basic file diagnostics

### Stop Conditions

- any wording that treats this roadmap as implementation authority
- any wording that reopens already-closed evidence loops by implication
- any wording that presents a runtime packet as the default next step
- any wording that treats the generic research note as a codebase-current execution contract
- any wording that blurs RI-vs-Legacy surface separation

## Bottom-line source decision

For future planning on this branch, use the two notes with **asymmetric authority**:

1. **Primary planning note:** `Genesis-Core router research — codebase-aware re-evaluation.md`
2. **Background structural note only:** `genesis_core_router_research.md`

This is the correct ordering because:

- the second note is already translated into Genesis-Core terms
- it keeps RI as the implementation surface and payoff-state as research truth only
- it understands the bounded router seam already implemented on this branch
- the first note is still valuable, but mainly as a structural hypothesis bank and terminology source

The first note must therefore be used as:

- architectural vocabulary
- candidate-pattern inventory
- background justification for why payoff-shape / hybrid-control framing matters

It must **not** be used as:

- the direct execution roadmap
- the current next-step selector
- runtime authority
- proof that any specific missing brick is still actually missing in this repository

## Current repo-truth overrides that outrank both notes

Before either note is used for next-step planning, the following current anchors remain authoritative:

- `GENESIS_WORKING_CONTRACT.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_payoff_state_translation_precode_packet_2026-04-30.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_runtime_packet_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`

These anchors already establish four important planning facts:

1. RI remains the chosen implementation surface; Legacy remains control/comparison only
2. the bounded runtime seam already implemented is `continuation_release_hysteresis`, not a broader router rewrite
3. the generic March 2021 / March 2025 discriminator loop is already closed with a bounded null on the current repo-visible surface
4. the clearest currently materialized local weakness is on the `insufficient_evidence` subset, while `AGED_WEAK_CONTINUATION_GUARD` remains mixed on the exact 2024 pocket reread

## What from the second note should be kept

The following ideas from `Genesis-Core router research — codebase-aware re-evaluation.md` should be kept as active planning truth:

- the main open structural gap is **conditional suppression discrimination**, not more naive activation/release tuning
- RI is the right runtime family-local lane
- payoff-state remains research/evaluation truth, not runtime input
- cross-family routing, exit-side rewrites, and bumpless-transfer-style widening remain deferred
- detector-state vs policy-state separation remains a strong design principle
- single-veto / one-shot suppressor primitives remain reusable future building blocks

## What from the second note must be softened or corrected

The following parts of the codebase-aware note must not be treated as current execution truth without adjustment:

### A. The implied next step is too early-staged

The note recommends a D1-style discriminator search inside the shared pocket as if that is still the clean next move.

That is no longer fully current.
The latest anchored evidence already ran the bounded March 2021 / March 2025 target contrast, the displacement crosscheck, and the displacement-normalized residual reread.
On that exact repo-visible surface, no clean sign-changing runtime-rule candidate survived.

Therefore:

- the **question** remains valuable,
- but the old D1 framing must not be reopened on the same already-exhausted surface.

### B. Aged-weak must not be overstated as the current leading explanation

The note presents aged-weak as if it is still the dominant suppressive explanation in the negative-year regression pocket.
The latest fixed 2024 pocket reason split is more precise:

- `insufficient_evidence` is the clearer local weak subset
- `AGED_WEAK_CONTINUATION_GUARD` is mixed rather than cleanly weak

Therefore any future roadmap must treat `insufficient_evidence` as the cleaner immediate research surface.

### C. The note is a synthesis note, not a command surface

Even when corrected, the second note is best treated as:

- a synthesis / interpretation artifact
- a framing document
- a source of ranked candidate lanes

It is **not** by itself a packet, a run plan, or a proof that a new runtime slice is ready.

## Roadmap phases

### Phase 0 — Lock source precedence and stale-line discipline

Goal:

- use the second note as the primary synthesis note
- keep the first note as background only
- prevent reopened use of already-closed evidence loops

Required outcome:

- all follow-up planning must explicitly say that the generic research note is a background idea bank
- all follow-up planning must explicitly say that the codebase-aware note is valid only where not superseded by later anchored evidence

Stop if:

- any later note starts citing the first note as if it were the execution contract
- any later note restarts the old D1 loop on the already-closed March 2021 / March 2025 surface

### Phase 1 — Normalize the synthesis note as a truthful repo-facing reference

Goal:

- if the second note is to be retained, make it repo-truthful and layout-clean before using it as a future reference anchor

Required future actions (docs-only, separately scoped if opened):

- move the second note out of its ad hoc location into an appropriate `docs/analysis/regime_intelligence/policy_router/` home
- soften the aged-weak-overstatement
- update the D1 wording so it no longer reads as if the old discriminator loop is still untested
- align any `risk_state.py` path references to the actual file location under `src/core/intelligence/regime/`

Important boundary:

- this roadmap does not perform that normalization
- this roadmap only records that such cleanup should happen before the note is treated as a stable long-lived repo anchor

### Phase 2 — Open one genuinely new bounded evidence slice

Goal:

- test whether the missing ingredient is actually a decision-time discriminator, but do so on a **new** bounded surface rather than reopening the exhausted March 2021 / March 2025 loop

Required shape of the future slice:

- RI-only
- read-only
- `insufficient_evidence`-first
- fixed row-membership surface
- explicit counterfactual question
- no runtime authority

Preferred future question:

> On a new bounded `insufficient_evidence` surface, is there any simple admissible decision-time split that selectively distinguishes rows where suppression was payoff-harmful from rows where suppression was payoff-correct?

Preferred future comparison structure:

- one fixed negative-year `insufficient_evidence` pocket already not exhausted by the current loop (for example the 2024 local pocket surface)
- one fresh positive-year control pocket on the same suppressor shape
- optional second negative holdout only if needed for sanity-checking

Required stop condition:

- if no simple single-field or shallow ordered split survives the new bounded surface, the discriminator line should be parked rather than widened by intuition alone

### Phase 3 — Require a counterfactual unlock check, not just correlation

Goal:

- prevent the next evidence slice from mistaking descriptive separation for a usable policy discriminator

Required question in the future slice:

> If the candidate split had been used only to exempt certain blocked rows from suppression, would it have improved the harmful pocket without simultaneously breaking the helpful pocket?

This means the future slice must not stop at:

- mean-gap contrast
- descriptive feature ranking
- visual separation

It must ask whether the candidate actually behaves like a **counterfactual unlock screen**.

Important boundary:

- this is still research-evidence only
- this is not runtime authorization

Stop if:

- the future slice shows only the same generic target-vs-displacement pattern again
- the candidate survives only as a magnitude skew and not as a selective counterfactual screen

### Phase 4 — Decide between park vs concept-packet

Goal:

- end the next research loop with a crisp fork instead of a fuzzy “maybe later” note

If the future evidence slice fails:

- park the discriminator line on the current repo-visible surface
- do not open a runtime packet
- do not reopen broad threshold tuning

If the future evidence slice succeeds:

- open one separate **concept-only** packet for the smallest admissible runtime form
- that packet may discuss a static per-state gate or lookup form
- that packet must keep payoff-state out of runtime and maintain deterministic replayability

Important boundary:

- no runtime packet is admissible directly from this roadmap
- a successful future evidence slice still only earns a concept packet, not implementation authority

### Phase 5 — Keep all other widening lines deferred

The following lines remain explicitly deferred unless separately reopened:

- broad threshold retuning in `_CONTINUATION_DEFAULTS`, `_NO_TRADE_DEFAULTS`, or `_SWITCH_DEFAULTS`
- new runtime widening beyond the already-implemented `continuation_release_hysteresis` seam
- reopening aged-weak as the first active follow-up carrier
- new Legacy implementation work beyond already-defined control/setup questions
- cross-family routing
- exit-side rewrite
- bumpless-transfer implementation
- defensive-probe runtime/config/default follow-up

## Practical execution order

If the user wants to “go through the roadmap” in order, the planning sequence should be:

1. **Accept source precedence**
   - second note = primary synthesis note
   - first note = background structural note only
2. **Do not reopen old D1 on the exhausted March 2021 / March 2025 surface**
3. **Optionally normalize the second note** as a repo-facing docs artifact
4. **Open one new bounded `insufficient_evidence` counterfactual-screen packet**
5. **End with a hard fork:**
   - no clean selector -> park the line
   - clean selector on new surface -> concept-only packet for smallest deterministic runtime form

## What this roadmap explicitly does not authorize

This roadmap does **not** authorize:

- any code changes
- any config/schema changes
- any new tests
- any evidence execution
- any runtime packet
- any replay/backtest run
- any readiness/cutover/promotion claim
- any claim that the generic note has become repo-truth on its own

## Bottom line

The correct way forward is:

- **drive planning from the second, codebase-aware note**,
- **keep the first note as structural background only**,
- **treat the already-closed March 2021 / March 2025 discriminator loop as closed**, and
- **make the next real step one new bounded `insufficient_evidence` counterfactual-screen packet on a genuinely new surface**.

That is the clearest fail-closed roadmap available now.
