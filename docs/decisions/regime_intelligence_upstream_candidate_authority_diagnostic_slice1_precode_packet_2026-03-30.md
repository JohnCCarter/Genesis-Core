# Regime Intelligence challenger family — upstream diagnostic slice1 pre-code packet

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code / observation-only / no implementation authorized`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet defines the first upstream diagnostic slice at strategy/runtime-near observation points, but does not authorize code change, config change, launch, implementation, comparison, readiness, promotion, or writeback.
- **Required Path:** `Full gated docs-only`
- **Objective:** Define one narrow diagnostic-before-change slice that tests whether the first meaningful RI-vs-upstream divergence is observable before fib/post-fib/sizing on one fixed tracked research surface.
- **Candidate:** `slice1 upstream observation-only diagnostic on fixed slice8 surface`
- **Base SHA:** `c27add49`

### Skill Usage

- **Verified repo-local skill:** none identified as directly applicable for this docs-only pre-code packet
- **Usage mode in this packet:** standard governance docs-only path; no skill-backed execution or launch authority is claimed by this packet

### Scope

- **Scope IN:** one docs-only pre-code packet; one exact upstream hypothesis; one fixed bounded diagnostic surface; explicit measurement boundary; explicit evidence unit; explicit measured chain stages; explicit upstream divergence criteria; explicit falsification condition; explicit non-authorization language.
- **Scope OUT:** no source-code changes; no config/YAML changes; no tmp/results/artifact rewrites; no implementation plan; no launch authorization; no runtime/default/family-rule/champion changes; no comparison/readiness/promotion/writeback; no downstream fib/post-fib/sizing/exit diagnostic scope.
- **Expected changed files:** `docs/decisions/regime_intelligence_upstream_candidate_authority_diagnostic_slice1_precode_packet_2026-03-30.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet remains observation-only and pre-code
- manual wording audit that no sentence implies implementation, dual-path runtime authorization, comparison, or launch readiness

For interpretation discipline inside this packet:

- exactly one upstream hypothesis must be defined
- exactly one bounded diagnostic surface must be defined
- the measurement boundary must end at `decision_gates.select_candidate(...)`
- downstream fib/post-fib/sizing/exit observations must remain explicitly out of scope for this slice
- divergence criteria must remain pre-fib and non-promotional

### Stop Conditions

- any wording that turns the packet into an implementation or instrumentation approval
- any wording that implies incumbent comparison, winner selection, readiness, or promotion
- any wording that treats non-authoritative observational metadata as an already approved dual-path runtime lane
- any wording that expands the slice beyond the bounded fixed surface or beyond the stated pre-fib chain boundary

### Output required

- reviewable pre-code packet
- one exact upstream hypothesis
- one exact bounded diagnostic surface
- one explicit measurement boundary and evidence unit
- one explicit divergence rule and falsification rule

## Purpose

This packet answers one narrow question only:

- what is the first admissible diagnostic-before-change slice for the already selected `UPSTREAM_CANDIDATE_FORMATION / CANDIDATE_AUTHORITY` direction?

This packet does **not**:

- authorize implementation
- authorize instrumentation code
- authorize validator/preflight/smoke execution
- open a launchable lane
- open comparison, readiness, promotion, or writeback
- change defaults, family rules, champion state, runtime authority, or config surfaces

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/decisions/regime_intelligence_upstream_candidate_authority_direction_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence_optuna_exit_override_plateau_closeout_2026-03-27.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`
- `docs/analysis/ri_legacy_role_map_slice3_fib_gate_1h_2026-03-30.md`
- `docs/analysis/ri_legacy_role_map_slice3_fib_gate_binding_1h_2026-03-30.md`
- `src/core/config/authority_mode_resolver.py`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/decision_gates.py`

Carried-forward meaning from those artifacts:

1. the exit/override-only lane remains closed in current tracked state
2. the fib lane is closed as structurally inactive in the current decision surface
3. the next admissible direction is upstream candidate formation / candidate authority
4. the lead tracked RI research tuple remains the already-governed slice8 surface
5. the first meaningful action surface is expected before fib, at or before candidate selection

## Exact upstream hypothesis

The exact hypothesis for this first slice is:

> On one fixed existing RI research surface, the first meaningful divergence is observable **before fib/post-fib/sizing**, inside the chain `authority_mode_resolver -> prob_model -> evaluate -> decision_gates.select_candidate(...)`, such that upstream authority/calibration state can be linked to different pre-fib threshold-pass or candidate-formation outcomes.

This is a **working hypothesis** only.

It is not a claim that the current runtime already exposes every required observation field, and it does not authorize any code change to do so.

## Bounded diagnostic surface

This packet defines exactly one bounded observational surface:

- symbol/timeframe: `tBTCUSD 3h`
- tracked RI surface: the already-governed slice8 full tuple
- fixed config selector: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- fixed tracked evidence selector: `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`

Interpretation boundary for this surface:

- this is a **fixed tracked research surface** only
- it is **not** a launchable canonical RI surface
- it is **not** an incumbent-comparison packet
- it is **not** a promotion or readiness surface

No second slice, no family mix, no new YAML, and no widened search surface are opened by this packet.

## Evidence unit

The evidence unit for this future diagnostic slice is:

- one bar-level or trace-row-level observation on the fixed slice8 surface

Each observation is intended to be read only across the bounded upstream chain named below.

## Measurement boundary

This slice begins at:

- `src/core/config/authority_mode_resolver.py`

and ends at:

- `src/core/strategy/decision_gates.py::select_candidate(...)`

This slice explicitly excludes:

- `decision_fib_gating.py`
- post-fib gates
- sizing
- exit behavior
- downstream trade outcome interpretation

Differences that appear only in those excluded downstream stages do **not** satisfy this slice.

## Measured chain stages

### 1. `authority_mode_resolver`

This slice will treat authority resolution as the first upstream observation point and will measure, at minimum:

- resolved authority mode
- resolution source
- the effective authoritative regime path chosen for the fixed observation row

### 2. `prob_model`

This slice will treat `prob_model` as the upstream probability/calibration observation point and will measure, at minimum:

- whether regime-aware calibration metadata is in play for the observation row
- the calibration metadata actually used for the fixed observation row
- the resulting probability-surface state relevant to later candidate formation

### 3. `evaluate`

This slice will treat `evaluate` only as an observation handoff where the upstream authoritative state is carried into decision input.

For this packet, `evaluate` may also reference any separately available non-authoritative observational metadata **only if such metadata is already present in the existing trace surface**.

This wording does **not** authorize or imply a launchable dual-path runtime implementation.

### 4. `decision_gates`

This slice will treat `decision_gates.select_candidate(...)` as the final observation boundary and will measure, at minimum:

- threshold-pass state
- candidate/no-candidate state
- direction/no-direction outcome
- any directly relevant pre-fib candidate metadata exposed at this boundary

## What counts as upstream divergence

For this slice, **upstream divergence** means a pre-fib difference observable at or before candidate formation within the bounded chain:

- `authority_mode_resolver -> prob_model -> evaluate -> decision_gates.select_candidate(...)`

A trace row counts as upstream divergence only if:

1. an upstream authority/calibration difference is observable for that row, and
2. that difference coincides with a different:
   - threshold-pass state, or
   - candidate/no-candidate state, or
   - direction/no-direction outcome

Differences that are only:

- metadata-only,
- fib-only,
- post-fib-only,
- sizing-only, or
- exit-only

do **not** satisfy this slice.

## What falsifies the hypothesis

This hypothesis is falsified for the bounded first slice if the fixed slice8 surface shows:

- no meaningful pre-fib candidate divergence attributable to upstream authority/calibration state, or
- observed differences that remain metadata-only or downstream-only without changing pre-fib threshold-pass or candidate-formation state

If the hypothesis is falsified at this bounded slice, this packet authorizes **no** implementation response by itself.

## Interpretation guardrails

This packet does **not** support any of the following claims:

- incumbent superiority
- uplift
- readiness
- promotion fitness
- family-rule change necessity
- default/runtime/champion change necessity

This is a diagnostic-before-change packet only.

## Explicit non-authorization boundary

This document is a pre-code governance artifact.

It does **not**:

- authorize code instrumentation
- authorize code implementation
- authorize config/YAML edits
- authorize runtime materialization of a dual-path observer
- authorize validator/preflight/smoke execution
- authorize comparison, readiness, promotion, or writeback

Any future instrumentation or implementation step requires a **separate governed opening / command packet**.

## Bottom line

The first admissible upstream slice is a **single-surface, observation-only, pre-fib diagnostic** on the fixed tracked slice8 RI surface.

Its only job is to test one bounded hypothesis:

- whether meaningful divergence appears upstream in `authority_mode_resolver -> prob_model -> evaluate -> decision_gates.select_candidate(...)` before fib, post-fib, sizing, or exit behavior enter the picture.

Nothing in this packet authorizes implementation, comparison, or launch.
