# Regime Intelligence challenger family — upstream diagnostic slice2 pre-code packet

Date: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code / observation-only / no implementation authorized`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet narrows the already-opened upstream research direction to one causal-localization slice inside the authority/calibration handoff, but does not authorize code change, config change, launch, implementation, comparison, readiness, promotion, or writeback.
- **Required Path:** `Full gated docs-only`
- **Objective:** Define one narrow diagnostic-before-change slice that localizes the earliest observed divergence candidate inside the authority/calibration handoff on the same fixed slice8 research surface used in slice 1.
- **Candidate:** `slice2 authority/calibration handoff localization on fixed slice8 surface`
- **Base SHA:** `c27add49`

### Skill Usage

- **Verified repo-local skill:** none identified as directly applicable for this docs-only pre-code packet
- **Usage mode in this packet:** standard governance docs-only path; no skill-backed execution or launch authority is claimed by this packet

### Scope

- **Scope IN:** one docs-only pre-code packet; one exact bounded hypothesis; one fixed bounded diagnostic surface; one ordered divergence-class model inside the authority/calibration handoff; one exact comparison-field inventory; one explicit earliest-divergence evidence rule; one explicit falsification rule; explicit non-authorization language.
- **Scope OUT:** no source-code changes; no `src/core/**` mutation; no config/YAML/default/champion/family-rule changes; no tmp/results/artifact rewrites; no implementation plan; no launch authorization; no runtime-semantics reopening; no downstream fib/post-fib/sizing/exit analysis; no comparison/readiness/promotion/writeback.
- **Expected changed files:** `docs/governance/regime_intelligence_upstream_candidate_authority_diagnostic_slice2_precode_packet_2026-03-30.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the packet remains pre-code and diagnostic-only
- manual wording audit that the packet does not claim root cause, runtime defect, correctness judgment, readiness, or promotion relevance
- manual wording audit that `authority_mode` is treated only as a pre-established branch selector from slice 1

For interpretation discipline inside this packet:

- exactly one bounded hypothesis must be defined
- exactly one fixed observational surface must be defined
- the ordered divergence classes must remain limited to:
  1. regime label divergence
  2. normalized authority-state divergence
  3. probability/calibration divergence
  4. threshold interpretation divergence
- earliest-divergence adjudication must require same-row comparability and earlier-class equality
- downstream fib/post-fib/sizing/exit interpretation must remain explicitly out of scope

### Stop Conditions

- any wording that turns the packet into an implementation or instrumentation approval
- any wording that reopens the semantics, correctness, or desirability of the known `authority_mode` split
- any wording that treats observational divergence as launch, promotion, or readiness evidence
- any wording that expands the slice beyond the fixed slice8 surface or beyond the authority/calibration handoff
- any wording that claims root cause or runtime defect rather than diagnostic localization

### Output required

- reviewable pre-code packet
- one exact bounded hypothesis
- one exact fixed observational surface
- one ordered divergence-class inventory with exact comparison fields
- one explicit earliest-divergence evidence rule
- one explicit falsification rule

## Purpose

This packet answers one narrow question only:

- on the already-fixed slice8 research surface, what is the earliest **observed divergence candidate** inside the authority/calibration handoff once the already-known branch split from slice 1 is treated as given?

This packet does **not**:

- authorize implementation
- authorize instrumentation code
- authorize validator/preflight/smoke execution
- reopen `authority_mode` semantics
- open a launchable lane
- open comparison, readiness, promotion, or writeback
- change defaults, family rules, champion state, runtime authority, or config surfaces

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/governance/regime_intelligence_upstream_candidate_authority_direction_packet_2026-03-30.md`
- `docs/governance/regime_intelligence_upstream_candidate_authority_diagnostic_slice1_precode_packet_2026-03-30.md`
- `docs/analysis/ri_upstream_candidate_authority_slice1_2026-03-30.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`
- `src/core/config/authority_mode_resolver.py`
- `src/core/intelligence/regime/authority.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/decision_gates.py`

Carried-forward meaning from those artifacts:

1. slice 1 already established the branch split at `authority_mode_resolver` on the fixed slice8 surface
2. slice 1 also established that divergence propagates through `evaluate` and `prob_model`, and reaches pre-fib candidate formation on a meaningful minority of rows
3. slice 2 therefore does **not** ask whether the branches differ at `authority_mode`; that is already known observational context
4. slice 2 asks only where the earliest downstream divergence candidate first becomes observable **inside** the authority/calibration handoff after that known selector step

## Known precondition from slice 1

The known `authority_mode` split established in slice 1 is treated here **only as a pre-established branch selector**.

Slice 2 does **not** reopen the semantics, correctness, or desirability of that selector. It only localizes the earliest downstream divergence after that selector on the same fixed surface.

## Exact bounded hypothesis

The exact hypothesis for slice 2 is:

> On the fixed slice8 research surface, conditioned on the already-known branch split at `authority_mode`, the earliest observed divergence candidate inside the authority/calibration handoff appears first in the **normalized authority-state handed off from `evaluate` into `predict_proba_for`**, not in the raw regime label alone, not first in calibration/probability outputs alone, and not first in threshold interpretation alone.

In this packet, **“earliest observed divergence candidate”** means the earliest observed divergence in the ordered authority/calibration handoff chain on the fixed slice8 surface, conditioned on all earlier-class fields matching for the same row. It is a **diagnostic localization term only** and does not, by itself, assert normative correctness, runtime defect, or production impact.

## Fixed diagnostic surface

This packet defines exactly one bounded observational surface:

- symbol/timeframe: `tBTCUSD 3h`
- tracked RI surface: the already-governed slice8 full tuple
- fixed config selector: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- fixed tracked evidence selector from slice 1: `artifacts/diagnostics/ri_upstream_candidate_authority_slice1_trace_20260330.json`
- supporting slice 1 summary: `docs/analysis/ri_upstream_candidate_authority_slice1_2026-03-30.md`

Interpretation boundary for this surface:

- this is a **fixed tracked research surface** only
- it is **not** a launchable canonical RI surface
- it is **not** an incumbent-comparison surface
- it is **not** a promotion or readiness surface

No second symbol, no second timeframe, no new YAML, and no widened search surface are opened by this packet.

## Measurement boundary

This slice begins **after** the already-known branch selector at `authority_mode_resolver` and follows the handoff chain through:

- raw regime label emitted by the branch-specific regime detector
- normalized authority-state assembled in `evaluate`
- probability/calibration application in `predict_proba_for`
- threshold interpretation in `decision_gates.select_candidate(...)`

This slice explicitly excludes:

- fib
- post-fib gates
- sizing
- exit behavior
- downstream trade outcome interpretation
- comparison/readiness/promotion framing

Differences that appear only in those excluded downstream stages do **not** satisfy this slice.

## Ordered divergence classes

The ordered divergence classes for slice 2 are exactly:

1. **regime label divergence**
2. **normalized authority-state divergence**
3. **probability/calibration divergence**
4. **threshold interpretation divergence**

The class order is part of the hypothesis and must not be widened in this packet.

## Exact comparison fields

The future diagnostic slice must compare control vs RI on the same row using the following exact field groups.

These are **diagnostic field labels only** for the future slice. They do not define a runtime API contract and do not authorize any implementation in this packet.

### Class 1 — regime label divergence

Compare the branch-local raw detector outputs **before normalization**:

- `raw_regime_label`
- `raw_regime_source`
- `raw_regime_precomputed_path_used`

Interpretation rule:

- this class is satisfied only if the raw branch-local regime label or its immediate detector-source state differs before normalized authority-state is assembled

### Class 2 — normalized authority-state divergence

Compare the normalized state handed off from `evaluate` into `predict_proba_for`:

- `normalized_authoritative_regime`
- `authoritative_source`
- `authority_mode_source`
- `normalization_fallback_applied`

Interpretation rule:

- this class is satisfied only if class-1 fields match on the same row, but the normalized regime state actually handed into probability selection differs

### Class 3 — probability/calibration divergence

Compare the regime-conditioned calibration and resulting probability state:

- `calibration_used.regime`
- `calibration_used.buy_calib.a`
- `calibration_used.buy_calib.b`
- `calibration_used.sell_calib.a`
- `calibration_used.sell_calib.b`
- `regime_aware_calibration`
- `probas.buy`
- `probas.sell`
- `probas.hold`

Interpretation rule:

- this class is satisfied only if classes 1 and 2 match on the same row, but regime-conditioned calibration or the resulting probability surface differs

### Class 4 — threshold interpretation divergence

Compare the pre-fib threshold interpretation state inside `decision_gates.select_candidate(...)`:

- `selected_regime`
- `default_thr`
- `applied_threshold`
- `threshold_zone`
- `threshold_source`
- `threshold_pass.buy`
- `threshold_pass.sell`

Interpretation rule:

- this class is satisfied only if classes 1 through 3 match on the same row, but the threshold selection or threshold-pass interpretation differs before any fib/post-fib logic

## Evidence rule for earliest observed divergence candidate

A row may establish class $N$ as the earliest observed divergence candidate **only if all earlier-class comparison fields are present and match on that same row in both branches**.

If earlier-class fields are unavailable, missing, or not comparable for that row, the row is **ineligible** for earliest-divergence adjudication.

Applied to the four classes above:

- class 1 is earliest if raw regime-label fields differ
- class 2 is earliest only if class 1 fields match and class 2 fields differ
- class 3 is earliest only if classes 1 and 2 match and class 3 fields differ
- class 4 is earliest only if classes 1 through 3 match and class 4 fields differ

This is a localization rule only. It does **not** claim proof of root cause, runtime defect, or behavioral superiority.

## What evidence would identify the first divergence

The first divergence candidate for slice 2 is identified by the earliest eligible class above on the fixed slice8 surface.

Evidence signatures by class:

- **regime label divergence**
  - raw detector label or raw detector-source state differs before normalization
- **normalized authority-state divergence**
  - raw detector fields match, but the normalized regime handed into `predict_proba_for` differs
- **probability/calibration divergence**
  - raw and normalized authority-state fields match, but `calibration_used` or `probas` differ
- **threshold interpretation divergence**
  - raw, normalized, and probability/calibration fields match, but `applied_threshold`, threshold source/zone, or threshold-pass state differs

## What falsifies the hypothesis

The slice-2 hypothesis is falsified on the bounded slice8 surface if the earliest eligible divergence candidate is **not** class 2.

That includes any of the following:

- class 1 is earliest because raw regime-label fields already diverge before normalized authority-state is assembled
- class 3 is earliest because normalized authority-state matches while calibration/probability fields diverge first
- class 4 is earliest because regime label, normalized authority-state, and calibration/probability fields match while threshold interpretation diverges first
- no eligible earliest divergence candidate is found because all four class-field groups match on comparable rows

If the hypothesis is falsified at this bounded slice, this packet authorizes **no** implementation response by itself.

## Non-goals and exclusions

This slice is **diagnostic-only**.

It does not perform:

- downstream fib analysis
- post-fib analysis
- sizing analysis
- exit analysis
- incumbent comparison
- readiness assessment
- promotion analysis
- any proposal for runtime/config/default/family-rule change

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

Slice 2 is a **single-surface, observation-only, diagnostic-before-change packet** whose only job is to localize the earliest eligible divergence candidate **inside** the authority/calibration handoff after the already-known branch selector from slice 1.

Its exact hypothesis is that the first such divergence will appear at the **normalized authority-state handoff** into `predict_proba_for`, rather than first at raw regime label, calibration/probability output, or threshold interpretation.

Nothing in this packet authorizes implementation, comparison, or launch.
