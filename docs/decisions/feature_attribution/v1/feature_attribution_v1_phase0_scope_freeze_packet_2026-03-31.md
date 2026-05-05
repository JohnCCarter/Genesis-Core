# Feature Attribution v1 — Phase 0 scope-freeze packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase0-locked / docs-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet freezes the Feature Attribution v1 research lane before any implementation, execution, or infrastructure work can begin, while remaining narrower than authoring, narrower than execution, and narrower than runtime/config authority.
- **Required Path:** `Quick`
- **Objective:** Freeze the Phase 0 scope, baseline anchors, exclusions, feature-definition boundary, and exact next admissible step for Feature Attribution v1.
- **Candidate:** `future Feature Attribution v1 research lock`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** one docs-only RESEARCH governance lock; exact research question; exact exclusions; baseline citation anchors; reserved artifact namespace; v1 feature-definition boundary; explicit non-authorizations; exact next admissible step.
- **Scope OUT:** no source-code changes; no tests; no result generation; no execution; no Optuna; no parameter search; no feature invention; no redesign; no interaction testing; no pairwise ablation; no changes under `src/**`, `tests/**`, `config/**`, `results/research/feature_attribution_v1/**`, `config/strategy/champions/**`, or family/promotion/readiness surfaces.
- **Expected changed files:** `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only citation check against locked baseline anchors
- manual wording audit that the packet remains non-authorizing
- manual wording audit that no implementation, execution, or result-generation authority is created

For interpretation discipline inside this packet:

- the user-provided roadmap must be treated as background input only
- the baseline config anchor must be treated as config-source only
- the baseline metrics must be treated as citation-only evidence
- the artifact root must be treated as reserved namespace only
- the fib lane must remain economically closed and must not be reopened by implication

### Stop Conditions

- any wording that authorizes implementation, execution, result generation, or infrastructure work
- any wording that reopens fib research, Optuna, promotion, or redesign
- any wording that treats `config/strategy/champions/tBTCUSD_3h.json` as newly validated champion authority rather than config-source anchor
- any wording that makes `results/research/feature_attribution_v1/` an authorized output path in this packet
- any wording that defines composite, bundled, or strategy-wide features as valid v1 ablation units

### Output required

- one reviewable Phase 0 RESEARCH scope-freeze packet
- exact baseline anchor and locked baseline metrics
- exact v1 feature-definition boundary
- explicit exclusions and non-authorizations
- exact next admissible step only

## What this packet is

This document is a **Phase 0 RESEARCH governance lock** for Feature Attribution v1.

It freezes:

- scope
- research question
- exclusions
- baseline citations
- artifact namespace
- v1 feature-definition boundary
- the exact next admissible governance step

This packet does **not** authorize:

- implementation
- runtime changes
- research execution
- result generation
- toggle infrastructure
- ablation runs
- optimization
- promotion or launch

## Governing basis

This packet is grounded in the following locked repository context:

- `results/research/fib_baseline_backtest_v1/summary.md`
- `results/research/ri_fib_window_parity_fix_v1/summary.md`
- `results/research/fib_promotion_evaluation_v1/summary.md`
- `results/research/cursor_to_copilot_handoff_fib_closure_v1/handoff_summary.md`
- `results/research/cursor_to_copilot_handoff_fib_closure_v1/governance_packet_for_copilot.md`
- `src/core/strategy/decision.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/components/attribution.py`

The user-provided **“Roadmap for Feature Attribution v1”** is treated here as **background input only**.

This packet does **not** ratify that roadmap as:

- implementation authority
- execution authority
- delivery approval
- infrastructure authorization

## Locked current-state context

The current locked baseline state carried into this packet is:

- `admissible = true`
- `fib_status = admissible_but_not_useful`
- `optuna_allowed = false`
- `promotion_decision = reject`

The current locked baseline metrics cited from `results/research/fib_baseline_backtest_v1/summary.md` are:

- `profit_factor = 2.1454408663493494`
- `max_drawdown = 1.3087994631199655`
- `win_rate = 76.02739726027397`
- `trade_count = 146`
- `expectancy = 4.248030093487892`

These metrics are cited as **baseline evidence only**.

This packet does **not**:

- reopen the fib lane economically
- reinterpret fib admissibility as launch authority
- reinterpret the baseline as a fresh promotion request

## Locked research question

The only locked research question for Feature Attribution v1 is:

> Which existing features drive edge under one-feature-at-a-time deterministic ablation?

This packet locks that question only.

It does **not** answer the question.

## Canonical baseline anchor

The canonical configuration anchor for Feature Attribution v1 is:

- `config/strategy/champions/tBTCUSD_3h.json`

For this packet, that file is used as the cited **`merged_config` configuration-source anchor only**.

It is **not** treated here as:

- newly validated champion authority
- a new readiness claim
- a promotion claim
- a request to modify champion state

The canonical baseline observational context is locked to:

- symbol: `tBTCUSD`
- timeframe: `3h`
- period: `2023-01-01 -> 2024-12-31`

The canonical baseline execution route for future v1 work is defined only as:

- the same existing canonical backtest route that produced the locked baseline evidence under `results/research/fib_baseline_backtest_v1/`

This packet defines no new evaluation semantics, no alternative route, and no new execution authority.

## Reserved artifact namespace

The canonical artifact root for this research lane is reserved as:

- `results/research/feature_attribution_v1/`

This reservation exists for namespace discipline only.

This Phase 0 packet does **not** authorize:

- creating artifacts there
- backfilling artifacts there
- running experiments to populate it
- producing baseline or ablation outputs now

## v1 feature-definition boundary

For Feature Attribution v1 governance purposes, a **feature** means:

- one existing, individually isolable seam in the current canonical strategy route

Allowed v1 feature classes may include only existing single-seam contributors such as:

- score contribution
- gate/filter
- multiplier
- bonus/penalty
- participation suppressor

A valid v1 feature unit must be:

- already present in the current canonical route
- individually targetable without rewriting adjacent flow
- neutralizable by one deterministic toggle contract later
- auditable as one seam rather than as a bundle

The following are explicitly excluded as v1 feature units:

- “all LTF logic”
- “all filters”
- “whole strategy”
- composite bundles
- redesign surfaces
- newly invented abstractions
- interaction bundles

## Canonical-route boundary

`src/core/strategy/components/attribution.py` is treated here as a **composable-strategy POC** and remains out of scope for Feature Attribution v1 Phase 0.

This packet does **not**:

- adopt it as the canonical implementation route
- endorse it as the required v1 architecture
- reserve it as the future target route
- authorize any migration into that component framework

Feature Attribution v1 remains bound to the **current canonical strategy route** unless a later separate governance step says otherwise.

## Phase 0 exclusions

The following are locked out of scope for Feature Attribution v1 Phase 0:

- no interaction testing in v1
- no pairwise ablation
- no parameter search
- no Optuna
- no strategy redesign
- no feature invention
- no new predictive features
- no default behavior change
- no runtime mutation outside explicit future feature toggling

## No-default-behavior-change lock

Feature Attribution v1 is frozen here as:

- research-only
- additive-only
- no-default-behavior-change
- explicit invocation only

Nothing in this packet authorizes changing default behavior on the canonical route.

## Fib non-reopen boundary

The fib lane remains economically closed on the already locked basis that:

- fib is technically admissible
- fib is economically non-additive
- `WITH fib == WITHOUT fib` across the locked evidence package
- `optuna_allowed = false`
- `promotion_decision = reject`

Feature Attribution v1 must not be interpreted as a path to reopen fib discovery, fib optimization, fib promotion, or fib redesign.

## Exact next admissible step

The only next admissible step after this Phase 0 lock is:

- one separate RESEARCH governance packet that proposes a deterministic one-feature-at-a-time ablation procedure and names candidate seams under the locked v1 feature boundary

That later packet, if opened, must still remain separate from:

- implementation
- execution
- result generation
- optimization
- redesign

## Bottom line

Feature Attribution v1 is now Phase 0 locked as a **research-only, additive-only, no-default-behavior-change** lane with:

- one locked research question
- one locked baseline citation anchor
- one reserved artifact namespace
- one fail-closed feature-definition boundary
- fib explicitly kept closed
- no implementation or execution authority created

This packet freezes the lane.
It does not start the lane.
