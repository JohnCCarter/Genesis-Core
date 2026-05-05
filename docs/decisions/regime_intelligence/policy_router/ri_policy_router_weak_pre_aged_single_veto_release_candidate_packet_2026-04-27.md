# RI policy router weak pre-aged single-veto release candidate packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / candidate preservation / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice preserves one fresh seam-A-only follow-up candidate after the cooldown-displacement diagnosis, but does not modify runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the split-seam lock, fail-set result, and cooldown-displacement diagnosis already exist, and the next honest move is to preserve one bounded seam-A candidate that explicitly addresses the repeated re-block mechanism before any new runtime packet is attempted.
- **Objective:** preserve one continuation-local follow-up candidate that tries to remove repeated seam-A weak-release re-blocking without reopening seam-B / strong-continuation semantics, cooldown semantics, or broader router-state semantics.
- **Candidate:** `weak pre-aged single-veto release guard`
- **Base SHA:** `HEAD`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- review scope: docs-only candidate preservation plus working-anchor update
- review lock: the candidate remains admissible only if it is stated as one same-guard, same-pocket weak-release re-block suppression hypothesis rather than as a generic reinterpretation of `previous_policy = RI_no_trade_policy`

## Skill Usage

- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the candidate is derived from verified router-local switch/state evidence and exists to prevent blind retuning.
- **Conditional repo-local spec:** `python_engineering`
  - reason: any later runtime slice must still remain typed, small, and test-backed, but this packet is docs-only.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_continuation_split_seam_direction_packet_2026-04-24.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_release_failset_evidence_2026-04-24.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_release_cooldown_displacement_diagnosis_2026-04-24.md`
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_release_implementation_packet_2026-04-24.md`
- **Candidate / comparison surface:**
  - any future runtime slice must stay inside `src/core/strategy/ri_policy_router.py` plus focused tests
  - the candidate may use only the existing weak-continuation classification, the prior router-local policy/state already carried by the router, and additive enabled-only router-local state if needed to mark that the same seam-A guard already fired inside the current local pocket
- **Vad ska förbättras:**
  - avoid turning one intended seam-A veto into a repeated `RI_no_trade_policy` chain
  - reduce the diagnosed `blocked long -> two bars later replacement long` displacement loop on the fail-set windows
- **Vad får inte brytas / drifta:**
  - no default-path change
  - no seam-B / strong-continuation change
  - no generic reinterpretation of `previous_policy = RI_no_trade_policy`
  - no cooldown retuning or cooldown-meaning change
  - no widening into defensive routing, sizing, exits, family/default/champion/promotion/readiness semantics
- **Reproducerbar evidens som måste finnas:**
  - row-level proof that the same seam-A guard cannot recursively re-block later weak-continuation bars in the same local pocket
  - paired fail-set comparison on the December micro/local windows
  - explicit note showing whether any remaining release delay is bounded to at most one guard-induced hold rather than a repeated no-trade pocket

## Verified mechanism that motivates this candidate

The current weak pre-aged release guard is fail-set-negative for a specific, now-localized reason:

- it hits the intended seam-A target around `2023-12-22T15:00:00+00:00`
- but it keeps `selected_policy = RI_no_trade_policy` on that path
- that retained no-trade state allows the same weak-release condition to remain eligible again on subsequent bars
- the result is a repeated no-trade pocket followed by later continuation release into the baseline cooldown cadence

The diagnosis note already bounds the observed loss mechanism more precisely:

- `12` substitution episodes were observed on the full fail window
- every replacement continuation entry appeared exactly `2` bars after the blocked baseline long
- seam B at `2023-12-24T21:00:00+00:00` remains a separate strong-continuation question and is not the target of this packet

## Candidate hypothesis

### Candidate intent

When the router would otherwise re-block a weak pre-aged release from `RI_no_trade_policy`, the seam-A guard should be allowed to veto that weak release **at most once per local pocket**.

Once the immediately prior `RI_no_trade_policy` was itself emitted by this same seam-A guard inside that same local pocket, subsequent weak-continuation bars should no longer be re-blocked by the same guard and should instead fall back to the existing router-local weak-continuation path plus the unchanged switch controls.

### Explicit non-goals

This is a seam-A-only preserved candidate.
It targets only repeated weak-release re-blocking inside a contiguous weak-continuation-below-strong pocket and does not alter seam-B / strong-continuation admission, cooldown semantics, sizing, defensive routing, or any family/default/champion/promotion/readiness surface.

### Local-pocket definition

For this candidate, `local pocket` means a contiguous same-side weak-continuation run that remains below `stable_bars_strong` and continues to classify as:

- `raw_switch_reason = "continuation_state_supported"`
- `mandate_level = 2`

Once that condition breaks, or the path reaches strong continuation / stable continuation semantics, this candidate no longer applies.

### Admissible runtime shape for a future packet

Any later runtime packet for this candidate may only:

- remain inside `src/core/strategy/ri_policy_router.py` plus focused tests
- use the existing weak-continuation seam-A classification and current `bars_since_regime_change`
- use prior router-local state already present on the enabled path
- add one enabled-only additive router-local marker only if needed to distinguish whether the immediately prior no-trade state was emitted by this same seam-A guard

Any later runtime packet must not:

- interpret `previous_policy = RI_no_trade_policy` generically across unrelated no-trade origins
- alter `stable_continuation_state`
- alter strong continuation scoring or thresholds as its primary mechanism
- alter cooldown timing, cooldown expiry, or cooldown meaning
- widen into defensive routing, sizing, exits, or family/default authority
- represent itself as a solution for the `2023-12-24T21:00:00+00:00` seam

## Why this remains cheaper than reopening broader continuation semantics

This candidate still lives on the cheaper seam-A side because it treats the verified problem as **guard self-reapplication inside the same weak-release pocket**, not as a broader continuation rewrite.

It therefore remains smaller than:

- a generic previous-policy provenance layer
- a cooldown-aware continuation retune
- a strong-continuation / seam-B intervention

## Intended falsifier

Reject this candidate if any of the following turns out to be true:

- removing repeated same-guard re-blocking still leaves the same two-bar displacement pattern materially intact
- the candidate needs generic cooldown knowledge or cooldown retuning to behave acceptably
- the candidate changes rows outside the same local weak-continuation-below-strong pocket as its primary mechanism
- the candidate can only work by reopening seam-B / strong-continuation semantics
- the candidate requires a general no-trade origin-tracking layer instead of one same-guard, same-pocket distinction

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_candidate_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `registry/**`
  - seam B / the `2023-12-24 21:00` strong continuation case
  - cooldown semantics
  - defensive routing
  - sizing
  - exits
  - family/default/champion/promotion/readiness surfaces
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_candidate_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required

- minimal markdown/reference sanity on the changed files
- diff-scope check confirming only the two docs files changed

## Stop Conditions

- the packet starts sounding like a generic reinterpretation of router-state provenance
- the candidate needs to mention seam B / strong continuation as part of the same bounded mechanism
- the candidate requires generic cooldown semantics instead of one same-guard, same-pocket de-chaining hypothesis
- the next step drifts into runtime authority without a separate runtime packet and review

## Output required

- one repo-visible seam-A candidate anchor for the next follow-up after the cooldown-displacement diagnosis
- one updated working contract that marks this candidate as preserved / `föreslagen` only and non-authoritative until a separate runtime slice is packeted and reviewed
