# Regime Intelligence challenger family — SIGNAL lane launch admissibility packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `admissibility-defined / research-level only / no comparison readiness or promotion scope`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet defines the admissible conditions for launching a SIGNAL-level RI research lane, but does not modify runtime/config rules, does not create a launch subject, and does not authorize comparison, readiness, promotion, or writeback
- **Required Path:** `Quick`
- **Objective:** Define the admissible conditions for a research-level SIGNAL lane launch so legitimate SIGNAL research execution can proceed under current guardrails without weakening governance guarantees.
- **Candidate:** `future RI SIGNAL research lane launch admissibility`
- **Base SHA:** `d227be7e`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Usage mode in this packet:** guardrail/reference only; no Optuna run, validator run, preflight run, smoke run, or launch authorization is performed by this packet

### Scope

- **Scope IN:** one docs-only packet defining what a valid SIGNAL hypothesis is, which artifacts are minimally required before launch, what SIGNAL-specific preflight must prove, how research/runtime/promotion authority differ, and when a SIGNAL lane is admissible for research-level launch.
- **Scope OUT:** no source-code changes, no config changes, no YAML creation, no validator/preflight execution, no smoke run, no launch authorization, no comparison opening, no readiness opening, no promotion opening, no writeback, no family-registry change, no family-admission change.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_signal_lane_launch_admissibility_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that research-level admissibility is not described as runtime-validity or promotion authority

For interpretation discipline inside this packet:

- no sentence may modify or reinterpret existing family registry rules
- no sentence may equate `research_slice` admission with runtime-valid RI conformity
- no sentence may authorize comparison, readiness, promotion, or writeback
- no sentence may make a specific future SIGNAL lane authorized now

### Stop Conditions

- any wording that changes family-registry or family-admission rules by implication
- any wording that equates research-level admissibility with runtime authority
- any wording that opens comparison, readiness, promotion, or writeback
- any wording that makes admissibility equal to authorization

### Output required

- reviewable SIGNAL launch admissibility packet
- explicit definition of valid SIGNAL hypothesis class
- explicit minimum artifact list
- explicit SIGNAL-specific preflight definition
- explicit authority-tier distinction
- explicit launch admissibility rule

## Purpose

This packet answers one narrow question only:

- under what conditions is a SIGNAL-level RI research lane admissible for launch at **research authority**?

This document is authoritative only for **research-level launch admissibility** for future SIGNAL lanes.
It does not constitute launch authorization, runtime-validity, comparison approval, readiness approval, promotion approval, or champion writeback authority.

This packet does **not**:

- create a launch subject YAML
- authorize any specific launch now
- change family-registry rules
- change family-admission rules
- reopen comparison, readiness, promotion, or champion writeback

## Governing basis

This packet is downstream of the current tracked RI plateau and direction packets, and references the current guardrail surface at minimum:

- `docs/analysis/regime_intelligence_plateau_evidence_slice7_slice10_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_exit_override_plateau_closeout_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md`
- `.github/skills/optuna_run_guardrails.json`
- `scripts/validate/validate_optimizer_config.py`
- `scripts/preflight/preflight_optuna_check.py`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`

Carried-forward meaning from those artifacts:

1. the slice7–slice10 exit/override-only lane is closed
2. the next chosen hypothesis class is `SIGNAL`
3. phases 3–8 were deferred because SIGNAL-lane authority conditions were not yet defined explicitly
4. validator/preflight and family guardrails remain in force unless separately governed later

Nothing in this document changes, reinterprets, or creates exceptions to existing `family_registry` or `family_admission` rules.
`research_slice` admission may not be cited as proof of runtime-valid RI conformity.

## 1) Valid SIGNAL hypothesis

A valid SIGNAL hypothesis changes **signal/regime-definition surface only**.

### Allowed change types inside a SIGNAL hypothesis

A future SIGNAL lane may tune or vary only surfaces that remain inside the signal/regime-definition class, such as:

1. existing signal parameter surfaces already consumed by the runtime/config path
2. existing regime-definition parameter surfaces already consumed by the runtime/config path
3. existing feature-selection or feature-availability surfaces, but only where the relevant implementation already exists on the pinned launch SHA

Examples of admissible SIGNAL-class surfaces include:

- `thresholds.signal_adaptation.*`
- `thresholds.signal_adaptation.atr_period`
- other already-implemented signal/regime-definition parameters explicitly cited in the future launch subject

### Non-admissible change types for a SIGNAL hypothesis

The following are **not** part of the SIGNAL class and must remain out of scope unless separately governed:

- decision / EV / candidate-selection logic
- confidence logic
- gating semantics
- exit logic
- objective / scoring logic
- family-registry rules
- family-admission rules
- execution-edge behavior

In particular:

- changes to decision logic are **not** allowed in a SIGNAL hypothesis packet
- they belong to a separate `DECISION` hypothesis class

### What must remain fixed

For a research-level SIGNAL lane to remain valid as a SIGNAL lane, the following must remain fixed unless separately governed later:

- existing family-registry rules
- existing family-admission rules
- objective/scoring class
- comparison closed
- readiness closed
- promotion closed
- champion/runtime defaults unchanged

## 2) Minimal required artifacts before launch

A future SIGNAL lane is not launch-admissible unless the following minimum artifact set exists.

### A. Exact launch subject

There must be one exact optimizer YAML that defines the future launch subject, including at minimum:

- declared `strategy_family`
- explicit `run_intent`
- explicit train/validation windows
- explicit fixed versus tunable dimensions
- explicit storage path
- explicit `resume=false` or equivalent unique-storage protection
- explicit promotion disabled

This packet does **not** create that YAML.
It defines it as a future required artifact.

### B. Feature-availability proof

Every tunable SIGNAL dimension in the future launch subject must have explicit feature-availability proof via one of the following:

1. citation to already merged implementation in the runtime/config path, or
2. citation to already existing runtime/config-authority surface that already consumes that dimension

If a proposed tunable SIGNAL dimension lacks such merged path/citation, the future SIGNAL lane is **inadmissible** until that implementation has been governed and merged separately.

This requirement does **not** create a new evidence class.
It may be satisfied by citations inside the future launch packet or by references to already merged implementation.

### C. Deterministic envelope proof

Before launch, the future SIGNAL lane must also have deterministic-envelope proof consisting of:

- pinned launch SHA
- canonical flags for research comparability
- unique storage path
- `resume=false` or equivalent storage non-reuse protection
- clean working tree at launch time
- bounded smoke artifact proving the launch subject runs under the pinned envelope

## 3) SIGNAL-specific preflight requirements

A future SIGNAL lane must satisfy all ordinary Optuna guardrails plus the following SIGNAL-specific requirements.

### What must be validated

Before a future SIGNAL lane may be considered launch-admissible, all of the following must be green on the exact launch subject:

1. optimizer config completeness
2. family identity / admission for `run_intent=research_slice`
3. feature-availability / path-existence proof for each tuned SIGNAL dimension
4. deterministic envelope completeness
5. bounded smoke success

The exact validator/preflight rule is:

- the launch subject must pass the current optimizer validator and the current preflight checks under canonical flags

That pass establishes **research-level admissibility only**.
It must **not** be described as runtime-valid RI conformity, canonical runtime-cluster compliance, or promotion authority.

### What can remain experimental

The following may remain experimental inside a future SIGNAL lane without blocking research-level admissibility:

- the exact search ranges for tunable SIGNAL dimensions
- the exact values reached by search
- the uplift hypothesis itself
- research-only interpretation of resulting artifacts

These may remain experimental because they are the substance of the research lane.
What may **not** remain experimental is feature existence, validator/preflight pass, or deterministic envelope integrity.

## 4) Authority tiers

This packet distinguishes three different authority levels.

### Research-level authority

Research-level authority means only the following:

- a future lane may be launched as `research_slice`
- the lane may emit research artifacts only
- the lane does not need comparison, readiness, or promotion context to run

Research-level authority is sufficient for:

- research Optuna execution
- research-only validation artifacts
- research-only analysis

Research-level authority is **not** equivalent to runtime authority or promotion authority.

### Runtime-level authority

Runtime-level authority is narrower and separate.

It concerns whether a configuration is valid as a runtime-facing RI subject under the current runtime/family authority contract.

A future SIGNAL lane passing `research_slice` admission does **not** automatically receive runtime-level authority.

### Promotion-level authority

Promotion-level authority is the narrowest and most restrictive tier.

It remains explicitly out of scope here.
It requires separate comparison/readiness/promotion lanes and is not opened by research-level launch admissibility.

## 5) Launch admissibility

This section defines when a future SIGNAL lane is admissible for research-level launch.

### Necessary conditions

A future SIGNAL lane is research-launch-admissible only when all of the following are true:

1. exactly one hypothesis class is selected: `SIGNAL`
2. all non-SIGNAL surfaces are fixed or separately governed
3. one exact launch-subject optimizer YAML exists
4. every tuned SIGNAL dimension has merged feature-availability proof
5. validator pass is green on the exact launch subject
6. preflight pass is green on the exact launch subject under canonical flags
7. deterministic envelope proof is complete
8. bounded smoke run is green
9. outputs are explicitly bounded to research-only use

### Authority boundary

If the criteria above are satisfied, that establishes **research-level launch admissibility only**.

It does **not** by itself establish:

- launch authorization
- comparison authority
- readiness authority
- promotion authority
- runtime authority
- champion writeback authority

A separate future launch-authorization packet is still required before any specific SIGNAL lane is actually run.

### No comparison/readiness/promotion dependency

A future SIGNAL lane does **not** need comparison, readiness, or promotion context to become research-launch-admissible.

That is the specific governance boundary defined by this packet.

The lane may therefore be admissible for research execution without:

- incumbent comparison
- readiness framing
- promotion framing

## What this packet unblocks

This packet unblocks the following narrow next step only:

- a future docs/config setup packet may define a specific SIGNAL launch subject and seek research-level admissibility under the conditions above

## What this packet does not unblock

This packet does **not** unblock:

- automatic launch of any SIGNAL lane now
- comparison lane opening
- readiness lane opening
- promotion lane opening
- family-registry change
- family-admission change
- runtime-authority reinterpretation

## Bottom line

A SIGNAL-level RI research lane is admissible for **research-level launch** when it:

- changes only the SIGNAL-class surface,
- keeps all non-SIGNAL surfaces fixed or separately governed,
- has one complete launch subject,
- proves feature availability for every tuned SIGNAL dimension,
- passes current validator and preflight under canonical flags,
- proves deterministic envelope integrity, and
- remains explicitly research-only in authority and output.

That is sufficient to unblock legitimate SIGNAL-level research execution **without** requiring comparison, readiness, or promotion context.

It is **not** sufficient to claim runtime authority, promotion authority, or automatic launch authorization.
