# REGIME INTELLIGENCE — Definition of Done (P1/P2)

Date: 2026-02-27
Category: `docs`
Status: **active reference**

## Purpose

This document defines what "klar" means for Regime Intelligence in two phases:

- **P1 (shadow/foundation)**: structural integration with no behavior change by default.
- **P2/v2 (behavior-change)**: explicit, flag-gated functional extension.

It exists to prevent interpretation drift between agents and reviews.

## "Klar" for P1 (shadow/foundation)

P1 is done when all items below are true:

1. Authority/SSOT switch is present with deterministic precedence and source attribution.
2. Shadow-regime and mismatch telemetry are present.
3. HTF regime helper is present (HTF fib context path).
4. Evaluate hook integration is present so regime usage is consistent in proba/pipeline path.
5. RegimeFilterComponent exists and can veto entry path.
6. Default mode preserves invariants (no behavior change unless explicitly enabled).
7. Determinism/invariance evidence is green on required baseline gates.

### P1 acceptance evidence (minimum)

- determinism replay test
- feature cache invariance test
- pipeline invariant hash test
- relevant evaluate/shadow contract tests
- golden window parity in OFF-mode versus baseline (identical actions/sizes/reasons)
- governance review confirms no runtime-default drift

### Frozen golden-window specification (P1 OFF parity)

For P1 evidence, the golden window is frozen as an immutable comparison spec:

- Window spec ID: `ri_p1_off_parity_v1`
- Comparison mode: OFF/default behavior only (no rollout behavior enabled).
- Baseline comparator: the latest approved P1 baseline artifact for the same window spec ID.
- Inputs that must be identical between baseline and candidate runs:
   - symbol set
   - timeframe set
   - start/end UTC range
   - runtime config source + commit SHA
   - canonical determinism flag: `GENESIS_FAST_HASH=0`
- Change control: any change to the golden window requires an explicit contract exception and a new window spec ID.

### P1 OFF-mode parity pass/fail contract

For the frozen golden window (`ri_p1_off_parity_v1`), parity is evaluated as follows:

- PASS requires all of the following:
   - identical action sequence versus baseline (same action labels per decision row)
   - identical reason payload versus baseline (same canonical reason strings)
   - identical size values versus baseline with strict tolerance: $|\Delta| \le 1\mathrm{e}{-12}$
   - no added/missing decision rows versus baseline
- FAIL is triggered by any single mismatch above.
- No manual override is allowed for P1 OFF-mode parity verdicts.

## "Klar" for P2/v2 (behavior-change)

P2/v2 is done only when all items below are true:

1. Clarity score (0–100) is fully specified and implemented with explicit:
   - feature inputs
   - normalization
   - clamps
   - rounding policy
2. Risk curve / policy mapping is implemented behind explicit version/flag.
3. DD override policy is implemented behind explicit version/flag.
4. Sizing breakdown logging is available for audit attribution.
5. Parity proof exists that **flag OFF yields identical output** versus P1 baseline.
6. Behavior-change exception is explicitly approved in governance contract.

### P2/v2 acceptance evidence (minimum)

- explicit OFF/ON parity test matrix
- decision parity in OFF mode
- reproducible logs showing sizing decomposition
- governance sign-off for behavior-change scope

## Explicit boundary between P1 and P2

- "Klar i kodbasen" can be true for P1 while P2 remains not started.
- "Klar enligt full v1 design" requires P2/v2 acceptance criteria to be satisfied.

## Non-goals in this document

- No runtime logic changes
- No config/champion edits
- No enforcement activation
- No skill activation side effects

## References

- `docs/ideas/REGIME_INTELLIGENCE_T8_CONTRACT_2026-02-26.md`
- `docs/ideas/REGIME_INTELLIGENCE_DESIGN_2026-02-23.md`
- `docs/ideas/REGIME_INTELLIGENCE_T0_CONTRACT_2026-02-26.md`
