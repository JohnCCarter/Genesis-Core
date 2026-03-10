# REGIME INTELLIGENCE — Definition of Done (P1/P2)

Date: 2026-02-27
Category: `docs`
Status: **active reference**

## Purpose

This document defines what "klar" means for Regime Intelligence in two phases:

- **P1 (shadow/foundation)**: structural integration with no behavior change by default.
- **P2/v2 (behavior-change)**: explicit, flag-gated functional extension.

It exists to prevent interpretation drift between agents and reviews.

## Repository status snapshot (NON-NORMATIVE)

As of 2026-03-03:

- P1 implementation (shadow/foundation) is merged on `master`.
- P1 formal sign-off evidence remains pending until a valid OFF-mode parity artifact
  (`ri_p1_off_parity_v1`) is produced with `parity_verdict=PASS` against an approved
  baseline reference and required gate evidence is attached.
- P2/v2 is not started in production mode; any behavior change remains flag/version-gated.

This snapshot is informational only. Normative pass/fail criteria remain the sections below.

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

### P1 evidence artifact format (locked minimum)

P1 OFF-mode parity evidence must be recorded in a machine-readable artifact:

- Artifact location: `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- Required fields:
  - `window_spec_id` (must equal `ri_p1_off_parity_v1`)
  - `run_id`
  - `git_sha`
  - `mode` (must be OFF/default)
  - `symbols`
  - `timeframes`
  - `start_utc`
  - `end_utc`
  - `baseline_artifact_ref`
  - `parity_verdict` (`PASS` or `FAIL`)
  - `action_mismatch_count`
  - `reason_mismatch_count`
  - `size_mismatch_count`
  - `size_tolerance` (must be `1e-12`)
- Optional human summary pointer: `docs/daily_summaries/*` with `run_id` and `git_sha`.

### P1 sign-off checklist (required)

P1 may be marked "klar" only when all checklist items are true:

- golden-window spec ID and inputs match the frozen definition
- OFF-mode parity verdict is `PASS` under the pass/fail contract above
- required PRE/POST gates are green for the tranche
- evidence artifact exists and includes all required fields
- governance review confirms no runtime-default behavior drift

### P1 evidence test/skill IDs (minimum map)

Minimum executable evidence set for P1 sign-off:

- `tests/test_import_smoke_backtest_optuna.py`
- `tests/backtest/test_backtest_determinism_smoke.py`
- `tests/test_features_asof_cache_key_deterministic.py`
- `tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `tests/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract`
- `tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
- `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run`
- `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run`

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

## Appendix: Quick sign-off example (NON-NORMATIVE / EXAMPLE ONLY)

This appendix is NON-NORMATIVE / EXAMPLE ONLY. The contract sections above are normative.
If example conflicts with contract, contract wins.

Mini example evidence artifact row (single-line):

```json
{
  "window_spec_id": "ri_p1_off_parity_v1",
  "run_id": "ri-20260227-001",
  "git_sha": "334fb0e6",
  "mode": "OFF",
  "symbols": ["tTESTBTC:TESTUSD"],
  "timeframes": ["1h"],
  "start_utc": "2025-01-01T00:00:00Z",
  "end_utc": "2025-01-31T23:59:59Z",
  "baseline_artifact_ref": "results/evaluation/ri_p1_off_parity_v1_baseline.json",
  "parity_verdict": "PASS",
  "action_mismatch_count": 0,
  "reason_mismatch_count": 0,
  "size_mismatch_count": 0,
  "size_tolerance": "1e-12"
}
```
