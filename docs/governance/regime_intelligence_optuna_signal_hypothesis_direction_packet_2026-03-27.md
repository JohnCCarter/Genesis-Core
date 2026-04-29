# Regime Intelligence challenger family — SIGNAL hypothesis direction packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `direction-selected / SIGNAL only / phases 3–8 deferred pending authority resolution`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet selects exactly one next research direction after the exit/override plateau closeout, but does not create a launchable lane, YAML, smoke, authorization, or Optuna run
- **Required Path:** `Full gated docs-only`
- **Objective:** Select exactly one next hypothesis class after the slice7–slice10 plateau, define the future research direction, and explicitly defer phases 3–8 until a separate authority-resolution pre-code packet exists.
- **Candidate:** `future RI signal/regime-definition research lane`
- **Base SHA:** `d227be7e`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Usage mode in this packet:** guardrail/reference only; no Optuna execution is authorized by this direction packet

### Scope

- **Scope IN:** docs-only next-direction decision; exact selection of one hypothesis class; explicit non-selection of the other hypothesis classes; explicit future change surface; explicit fixed surface; explicit expected improvement signature; explicit falsification condition; explicit blocker that defers phases 3–8.
- **Scope OUT:** no source-code changes, no config changes, no tmp artifacts, no validator/preflight/smoke execution, no launch authorization, no outcome-analysis packet for a new run, no decision-gate packet for a new run, no comparison opening, no readiness opening, no promotion opening, no writeback.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that exactly one hypothesis class is selected

For interpretation discipline inside this packet:

- exactly one hypothesis class must be selected
- the rejected hypothesis classes must remain explicitly not chosen now
- no sentence may imply that the future SIGNAL lane is already launch-authoritative
- no sentence may reopen comparison, readiness, promotion, or champion writeback
- the defer-blocker for phases 3–8 must remain explicit

### Stop Conditions

- any wording that selects more than one hypothesis class
- any wording that treats the future SIGNAL lane as already launchable
- any wording that reopens comparison, readiness, promotion, or writeback
- any wording that omits the authority-resolution blocker for phases 3–8

### Output required

- reviewable direction packet
- explicit chosen hypothesis label
- explicit rejected hypothesis labels
- explicit future change surface
- explicit fixed surface
- explicit expected improvement signature
- explicit falsification condition
- explicit deferred blocker for phases 3–8

## Purpose

This packet answers one narrow question only:

- what is the next admissible RI research direction after the exit/override plateau was closed?

This packet does **not**:

- create a launchable optimizer lane
- create a YAML or smoke config
- authorize launch now
- reopen comparison, readiness, or promotion

## Governing basis

This packet is downstream of the following current tracked artifacts and guardrails:

- `docs/analysis/regime_intelligence_plateau_evidence_slice7_slice10_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_exit_override_plateau_closeout_2026-03-27.md`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `scripts/validate/validate_optimizer_config.py`
- `scripts/preflight/preflight_optuna_check.py`

Carried-forward meaning from those artifacts:

1. the slice7–slice10 exit/override-only lane is closed
2. no further local optimization in that surface is admissible
3. any future progress must come from new information, new decision structure, or new objective definition rather than repeated local exit/override tuning
4. any future launchable lane must still satisfy the current validator/preflight authority contract or resolve that contract explicitly through separate governance

## Hypothesis classes under decision

### Option 1 — SIGNAL hypothesis

Meaning:

- future research changes the RI signal/regime-definition surface only
- future research does **not** change the objective class
- future research does **not** change the decision/EV/confidence logic class

Operational definition in this work:

- future tuning is limited to `thresholds.signal_adaptation.*`
- plus `thresholds.signal_adaptation.atr_period`

Current suitability:

- **selected by this packet**

Why it is selected now:

- the closed plateau was established inside an exit/override-only lane while core signal/regime/gating structure remained fixed
- the next admissible hypothesis should therefore change the information/regime-definition surface rather than continue local management tuning

### Option 2 — DECISION hypothesis

Meaning:

- future research would change EV, gating, or confidence logic

Current suitability:

- **not selected now**

### Option 3 — OBJECTIVE hypothesis

Meaning:

- future research would change scoring or optimization target

Current suitability:

- **not selected now**

## Decision

### Chosen hypothesis label

- `CHOSEN — SIGNAL hypothesis`

### Rejected hypothesis labels

- `NOT CHOSEN NOW — DECISION hypothesis`
- `NOT CHOSEN NOW — OBJECTIVE hypothesis`

## Meaning of the decision

This packet selects exactly one next admissible research direction:

- **SIGNAL hypothesis**

This means the next legitimate RI continuation, if separately governed later, must investigate a **signal/regime-definition** surface rather than:

- a continued exit/override-only lane
- a decision-logic lane
- an objective/scoring lane

This decision does **not** mean:

- a launchable signal lane is already authorized
- a specific future YAML is already approved
- phases 3–8 are authorized now

## What changes in the future SIGNAL lane

If a separately governed future SIGNAL lane is opened later, the intended change surface is:

- `thresholds.signal_adaptation.*`
- `thresholds.signal_adaptation.atr_period`

That future lane is expected to test whether a different RI signal/regime-definition surface can break the current plateau signature without reopening exit/override-only local optimization.

## What remains fixed in the future SIGNAL lane

If a separately governed future SIGNAL lane is opened later, the following remain fixed unless separately re-governed:

- decision / EV / confidence logic class remains fixed
- objective class remains fixed
- the closed exit/override-only lane remains closed
- comparison, readiness, promotion, and champion writeback remain out of scope

## Expected improvement signature

A future SIGNAL lane would count as an improvement only if at least one validated artifact:

1. has validation score strictly greater than `0.26974911658712664`, and
2. does **not** match the exact plateau signature tuple below:
   - validation score: `0.26974911658712664`
   - profit factor: `1.8845797002042906`
   - max drawdown: `0.027808774550017137`
   - trades: `63`
   - sharpe: `0.20047738907046656`

## Falsification condition

A future SIGNAL lane would be falsified if either:

1. no validated artifact exceeds validation score `0.26974911658712664`, or
2. the top validated artifact matches the exact plateau signature tuple above

## Explicit blocker for phases 3–8

Phases 3–8 are **deferred** by this packet.

Reason:

- the current tracked plateau anchor is research evidence only
- it is **not** yet established as launch-authoritative under the current RI validator / family-admission / preflight contract
- therefore no future SIGNAL YAML, smoke run, launch authorization, full Optuna run, outcome packet, or decision-gate packet may be opened from this packet alone

This packet selects only **SIGNAL**. **DECISION** and **OBJECTIVE** are expressly deferred, and no phase 3–8 work, validator change, or gate-range / authority-lane opening is authorized without a separate authority-resolution pre-code packet.

A separate pre-code authority-resolution packet is required before phases 3–8 may begin.

That separate packet must explicitly resolve:

- what validator/preflight authority governs a future launchable SIGNAL lane
- what fixed backdrop is admissible under that authority
- whether any non-canonical research-slice surface requires explicit governance exception

## Next allowed step

The next allowed step after this packet is:

- a separate pre-code authority-resolution packet for any future launchable SIGNAL lane

That later packet must remain outside comparison, readiness, promotion, and champion writeback unless a separate governance opening says otherwise.

## Bottom line

After the slice7–slice10 plateau closeout, the next admissible RI direction is now explicitly selected as:

- **SIGNAL hypothesis**

The DECISION and OBJECTIVE hypothesis classes are **not chosen now**.

This packet defines the future change surface, the fixed surface, the expected improvement signature, and the falsification condition.

It does **not** authorize phases 3–8.

Those phases remain explicitly deferred until a separate authority-resolution pre-code packet exists.
