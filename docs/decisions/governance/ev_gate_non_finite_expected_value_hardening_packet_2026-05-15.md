# EV gate non-finite expected-value hardening packet

Date: 2026-05-15
Branch: `feature/editor-worker-orchestrator`
Status: `packet-defined / docs-only / non-authorizing`

This document is a planning/decision artifact in `RESEARCH` and grants no implementation, runtime, strategy, config-authority, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin source, test, config, or API behavior changes.

> Current implementation-status note:
>
> - The candidate framed by this packet has since been landed in a separate bounded runtime slice limited to `src/core/strategy/components/ev_gate.py` and `tests/core/strategy/components/test_ev_gate_integration.py`.
> - Verification on that later slice was green on touched-file `black --check` / `ruff check`, focused EVGate tests, combined EVGate + context-builder component smoke, and the same determinism/parity/pipeline/feature-cache checks used for earlier strategy-adjacent slices.
> - Executed selectors / outcomes for that later slice:
>   - `pytest tests/core/strategy/components/test_ev_gate_integration.py -v --tb=short` → `20 passed`
>   - `black --check src/core/strategy/components/ev_gate.py tests/core/strategy/components/test_ev_gate_integration.py` → `pass`
>   - `ruff check src/core/strategy/components/ev_gate.py tests/core/strategy/components/test_ev_gate_integration.py` → `pass`
>   - `pytest tests/core/strategy/components/test_ev_gate_integration.py tests/core/strategy/components/test_context_builder_key_mapping.py -v --tb=short` → `33 passed`
>   - `pytest tests/backtest/test_backtest_determinism_smoke.py tests/governance/test_regime_intelligence_cutover_parity.py tests/governance/test_pipeline_fast_hash_guard.py tests/integration/test_precompute_vs_runtime.py tests/utils/test_feature_parity.py tests/utils/test_features_asof_cache_isolation.py` → `24 passed`
> - This packet remains the historical pre-code framing artifact and does not retroactively authorize wider component or pipeline work.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/editor-worker-orchestrator`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice only defines the next bounded pre-code candidate near a runtime strategy component seam; the main risk is wording drift that could be mistaken for approval to widen component semantics or to reopen EV formula/policy questions
- **Required Path:** `Quick`
- **Lane:** `Concept` — why: this slice selects and bounds the next candidate without entering runtime implementation
- **Objective:** define a narrow next pre-code candidate that hardens EV gate handling for non-finite expected values without changing valid finite EV behavior or entry policy semantics
- **Candidate:** `fail-closed handling for non-finite expected_value in EVGateComponent`
- **Base SHA:** `66f97acc`
- **Skill Usage:** no matching repository skill identified for this narrow `ev_gate` hardening slice; no skill coverage claim is made in this packet

### Scope

- **Scope IN:** one docs-only packet; explicit statement of the observed EVGate seam in `src/core/strategy/components/ev_gate.py`; exact likely source/test scope for one bounded future implementation slice only; explicit done criteria and stop conditions for that later slice
- **Scope OUT:** all code/test edits in this slice; all EV formula changes; all threshold calibration changes; all context-builder semantics changes; all decision/size/router/fib/config/schema changes; all paper/live, readiness, promotion, or shared-truth claims; all claims that implementation is already approved
- **Expected changed files:** `docs/decisions/governance/ev_gate_non_finite_expected_value_hardening_packet_2026-05-15.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual wording audit that this packet remains docs-only and non-authorizing
- manual wording audit that the candidate stays narrower than a general EV/component refactor
- manual wording audit that valid finite-input behavior is described as unchanged unless a later code packet proves otherwise

### Stop Conditions

- any wording that treats this packet as implementation approval
- any wording that broadens the candidate from non-finite EV hardening into EV formula, threshold, or component-design redesign
- any wording that silently absorbs `ComponentContextBuilder`, decision pipeline, sizing, router, or config/schema surfaces into the same future slice
- any wording that implies this packet has already validated runtime correctness without a separate implementation-bearing slice

## Purpose

This packet answers one narrow question only:

- what is the next smallest component-level hardening slice worth opening after the first `decision_gates.py` finite-numeric slice has already landed?

## Governing basis

### Observed

1. `src/core/strategy/components/ev_gate.py` currently treats `expected_value is None` and non-convertible values as defensive vetoes with `EV_MISSING`
2. the same component currently does `ev_float = float(ev)` and then compares `ev_float < self.min_ev`
3. for non-finite but convertible values such as `NaN`, `+inf`, and `-inf`, the conversion succeeds
4. for `NaN` and plausibly `+inf`, the comparison `ev_float < self.min_ev` is not a fail-closed veto, which means the current implementation can plausibly return `allowed=True` for an invalid EV payload
5. `-inf` already produces a non-allow path through the existing threshold comparison and is therefore not the primary fail-open problem in this seam
6. current tests in `tests/core/strategy/components/test_ev_gate_integration.py` cover normal allow/veto paths and missing EV, but do not anchor `NaN` / `+inf` / `-inf` behavior

### Inferred

- this seam is narrower than a general component-pipeline redesign because the likely first-touch file is `src/core/strategy/components/ev_gate.py`
- the likely first proof surface is the EVGate integration test file already present in `tests/core/strategy/components/test_ev_gate_integration.py`
- the correct hardening target is fail-closed handling for non-finite expected values, not a rewrite of how expected value is computed upstream
- the narrowest behavior-change exception is likely to be: `NaN` and `+inf` stop following the current fail-open path and instead reuse the existing defensive invalid/missing-input style path, while `-inf` remains on its current non-allow path unless separately reopened

### Unverified in this packet

- whether a later implementation slice can remain fully contained to `ev_gate.py` and one existing test file without any helper extraction
- whether the preferred fail-closed outcome should reuse `EV_MISSING` exactly or another already-existing defensive reason path, so long as permission does not widen

## Boundary decision

### Current standing conclusion

The next bounded component-level hardening candidate should be framed as:

- **fail-closed handling for non-finite `expected_value` in `src/core/strategy/components/ev_gate.py`**

This is a candidate-selection conclusion only. It is **not** approval to edit the runtime component yet.

### Likely future implementation scope

If this candidate is reopened as a real pre-code implementation packet, the smallest honest starting scope is likely:

- `src/core/strategy/components/ev_gate.py`
- `tests/core/strategy/components/test_ev_gate_integration.py`

`src/core/strategy/components/context_builder.py` remains **OUT** for the initial slice. If later inspection shows that upstream context emission must change, the work must stop, amend the packet/contract, and obtain fresh pre-code review before editing it.

### Likely future implementation scope OUT

A future packet for this candidate should keep the following out of scope unless separately reopened:

- `src/core/strategy/components/context_builder.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/ri_policy_router.py`
- EV formula or calibration semantics
- config/schema files or runtime live-update surfaces
- paper/live, promotion, champion, or readiness implications

## What that future pre-code packet must define

A future implementation-bearing packet for this candidate must define at minimum:

- the exact non-finite EV inputs being hardened
- whether the change is contained to one comparison seam or needs a tiny private helper in `ev_gate.py`
- the exact fail-closed fallback rule for non-finite values
- whether `-inf` stays on the current threshold-veto path or is deliberately normalized into the invalid/missing-input path
- what must remain unchanged for already-valid finite EV inputs
- the smallest focused tests needed to prove no fail-open behavior and no finite-input drift
- what code paths remain explicitly out of scope

## Expected verification stack for the implementation slice

If the future implementation slice is opened, the expected minimum verification stack should be:

- touched-file `black --check`
- touched-file `ruff check`
- focused `pytest` for `tests/core/strategy/components/test_ev_gate_integration.py`
- affected-flow component smoke using the EVGate integration test together with `tests/core/strategy/components/test_context_builder_key_mapping.py`
- determinism/parity check set already used for strategy-adjacent runtime slices
- feature-cache invariance check set already used for strategy-adjacent runtime slices
- pipeline invariant / hash-guard checks already used for strategy-adjacent runtime slices

## Future done criteria for the implementation slice

If the future implementation slice is opened, it should be considered done only if all of the following are true:

- `NaN`, `+inf`, and `-inf` expected values do not produce `allowed=True`
- `NaN` and `+inf` follow the same defensive invalid/missing-input style path already used today and do not widen permission
- `-inf` either remains on the current non-allow threshold-veto path or is explicitly and separately approved for reason-path normalization before implementation
- representative valid finite EV inputs remain unchanged across the targeted EVGate tests
- focused tests cover at least one finite control case plus representative `NaN` / `+inf` / `-inf` cases
- if implementation requires changing upstream context emission or broader component-pipeline semantics, the slice stops and reopens as a new packet

## Hard stop and reopen rule

If the future slice needs to change any of the following, it must stop and reopen as a separate bounded packet:

- EV formula or threshold semantics
- `ComponentContextBuilder` emission rules
- decision-pipeline or sizing behavior
- router/fib behavior
- config/schema authority or live-update semantics
- broad component-framework refactors

## Bottom line

After the first `decision_gates.py` finite-numeric slice, the next smallest risk-reducing move is not a broader component refactor. It is a separate bounded pre-code packet for **fail-closed handling of non-finite `expected_value` in `src/core/strategy/components/ev_gate.py`**, with focused tests and explicit guarantees that valid finite EV behavior stays unchanged.
