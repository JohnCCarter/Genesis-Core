# RI policy router weak pre-aged release candidate packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / candidate preservation / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice preserves the next cheapest continuation-local candidate after the first fail-set veto, but does not modify runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the split seam has already been verified, and the next honest move is to freeze one bounded seam-A candidate before any new runtime packet is considered.
- **Objective:** preserve one continuation-local follow-up candidate that targets the verified `weak but not aged` seam without pretending to solve the separate `already strong continuation` seam.
- **Candidate:** `weak pre-aged continuation release guard`
- **Base SHA:** `HEAD`

## Skill Usage

- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the candidate is derived from verified router-local state and exists to avoid blind threshold retuning.
- **Conditional repo-local spec:** `python_engineering`
  - reason: any later runtime slice must still remain small and test-backed, but this packet is docs-only.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/analysis/ri_policy_router_aged_weak_continuation_guard_failset_evidence_2026-04-24.md`
  - `docs/decisions/ri_policy_router_continuation_split_seam_direction_packet_2026-04-24.md`
  - `results/backtests/policy_router_split_20260424/2023_Dec/router_enabled_decision_rows.ndjson`
  - `results/backtests/ri_policy_router_aged_weak_continuation_guard_20260424/fail_b_2023_dec_candidate_decision_rows.ndjson`
- **Candidate / comparison surface:**
  - any future runtime slice must stay inside `src/core/strategy/ri_policy_router.py`
  - the intended target seam is weak continuation release before the current age gate, not strong continuation semantics
- **Vad ska förbättras:**
  - prevent the specific weak continuation release around `2023-12-22T15:00:00+00:00`
  - avoid replacing an earlier suppressed/no-trade pocket with a low-maturity weak continuation entry
- **Vad får inte brytas / drifta:**
  - no default-path change
  - no strong continuation change
  - no defensive routing change
  - no sizing, exits, cooldown, or switch-control retuning as primary mechanism
  - no claim that this candidate solves the `2023-12-24T21:00:00+00:00` strong seam
- **Reproducerbar evidens som måste finnas:**
  - row-level proof on `2023-12-22T15:00:00+00:00`
  - paired fail-set comparison on the December micro/local windows
  - explicit note showing whether any observed improvement comes from release suppression rather than broad trade churn

## Verified target seam

The motivating row is `2023-12-22T15:00:00+00:00` with verified router-local state:

- `bars_since_regime_change = 7`
- `switch_reason = continuation_state_supported`
- `mandate_level = 2`
- `previous_policy = RI_no_trade_policy`

This means the row is:

- weak continuation,
- not yet aged enough for the previous guard,
- and released from a prior router-local no-trade state.

## Candidate hypothesis

### Candidate intent

When the router would otherwise release from `RI_no_trade_policy` into a weak continuation state at still-young regime age, that release should require tighter maturity/evidence than generic weak continuation.

The candidate is intentionally narrow:

- continuation-local only
- targets seam A only (`weak but not aged`)
- does not claim to solve seam B (`already strong continuation`)
- should remain below strong-continuation semantics unless later evidence proves that is impossible

### Admissible runtime shape for a future packet

Any later runtime packet for this candidate may only:

- use the already available router-local classification of weak continuation
- use existing router state already available inside `ri_policy_router.py`
- target release from a previous router-local no-trade state and/or insufficient regime maturity

Any later runtime packet must not:

- alter `stable_continuation_state`
- alter strong continuation scoring or thresholds as its primary mechanism
- widen into `DEFENSIVE`, sizing, exits, or family/default authority
- represent itself as a solution for the `2023-12-24T21:00:00+00:00` seam

## Why this is cheaper than a strong-continuation candidate

This candidate remains aligned with the cheaper seam class identified in the split-seam direction packet:

- it keeps the work on the weak continuation side,
- it can still be described as a continuation-admission question,
- and it does not require the next packet to honestly claim strong continuation intervention.

## Intended falsifier

Reject this candidate if any of the following turns out to be true:

- the target `2023-12-22T15:00:00+00:00` row cannot be addressed without changing strong continuation semantics
- the candidate only works by broadly lowering trade count across December
- the candidate removes the target row only by collapsing back into generic evidence-floor no-trade behavior elsewhere
- the candidate silently depends on seams outside `ri_policy_router.py`

## Scope

- **Scope IN:**
  - `docs/decisions/ri_policy_router_weak_pre_aged_release_candidate_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `registry/**`
  - any runtime/default/champion/promotion/family-rule surface
- **Expected changed files:**
  - `docs/decisions/ri_policy_router_weak_pre_aged_release_candidate_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required

- minimal docs validation on the changed files

## Stop Conditions

- the next runtime idea needs to change strong continuation semantics to hit the target row
- the next packet starts claiming this candidate also covers `2023-12-24T21:00:00+00:00`
- the next step drifts into `DEFENSIVE`, sizing, exits, family-rule, or authority surfaces

## Output required

- one repo-visible seam-A candidate anchor
- one updated working contract that identifies this as the cheapest next candidate if work stays below strong-continuation semantics
