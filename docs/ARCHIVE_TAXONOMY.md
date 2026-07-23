# Archive Taxonomy

Date: 2026-05-26
Mode: `RESEARCH`
Status: `docs-only / non-authorizing / archive taxonomy proposal / no behavior change`

## Purpose

This document defines the first Genesis-Core archive taxonomy for future physical archive moves.

The goal is to reduce active-surface clutter while preserving historical evidence, failed experiments, research outputs, diagnostics, and governance-relevant artifacts.

## Scope

### Scope IN

- archive category definitions
- physical archive-move rules
- high-caution archive categories
- future rename-only workflow guidance
- reference-check requirements

### Scope OUT

- moving existing files in this slice
- deleting files
- pointer-stub creation
- runtime behavior changes
- config behavior changes
- test behavior changes
- promotion/readiness claims
- changing governance authority

## Core archive rule

Archive means physically moved historical material.

Default rule:

```text
Move the file to the correct archive category.
Update old references in the same rename-only slice.
Do not leave pointer stubs by default.
If safe movement cannot be proven, keep the file in place.
```

## Archive is not authority

Archive content is retained evidence.
It is not current runtime authority, implementation authority, promotion authority, or readiness authority unless a current authority surface explicitly cites it for a bounded purpose.

## Proposed archive tree

```text
archive/
  README.md

  experiments/
  research/
  results/
  evaluation/
  backtests/
  optuna/

  artifacts/
  diagnostics/
  reports/

  tmp/
  logs/
  cache/

  config/
  data/
  deprecated_scripts/
  superseded_docs/
  historical_plans/
  audits/
  frozen_artifacts/
```

## Category definitions

### `archive/experiments/`

Historical experiment definitions, notes, exploratory prototypes, and experiment-specific materials that are no longer active work surfaces.

### `archive/research/`

Historical research notes, bounded research lanes, and non-authorizing research evidence that should no longer sit in active research locations.

### `archive/results/`

Historical `results/**` outputs retained for evidence, reproducibility, or lineage but no longer active result surfaces.

### `archive/evaluation/`

Historical evaluation outputs, evaluation summaries, and bounded evaluation artifacts that are retained as evidence but not current evaluation surfaces.

### `archive/backtests/`

Historical backtest outputs, old backtest reports, and retained comparison outputs that are no longer current evidence surfaces.

### `archive/optuna/`

Historical optimization studies, Optuna outputs, tuning artifacts, and superseded optimization evidence.

### `archive/artifacts/`

Generic historical artifacts that do not fit a narrower archive category.

### `archive/diagnostics/`

Historical diagnostics, diagnostic batches, evidence JSON, audit traces, and generated diagnostic outputs.

### `archive/reports/`

Historical generated reports and report snapshots that are no longer current reporting surfaces.

### `archive/tmp/`

Historical temporary material retained for evidence. High caution: temporary-looking files may still be referenced by scripts or research carriers.

### `archive/logs/`

Historical logs retained for audit or evidence purposes. Logs should not be treated as active execution inputs.

### `archive/cache/`

Historical cache material retained only when evidence-relevant. High caution: cache movement can affect determinism if any pipeline reads from it.

### `archive/config/`

Historical or superseded config snapshots. High caution: config movement can affect runtime/config authority, tests, and reproducibility.

### `archive/data/`

Historical or superseded data snapshots. High caution: data movement can affect reproducibility, backtest coverage, and source-policy semantics.

### `archive/deprecated_scripts/`

Historical scripts proven no longer active, no longer imported, and no longer referenced by current workflows.

### `archive/superseded_docs/`

Documents explicitly superseded by newer current-authority or current-routing surfaces.

### `archive/historical_plans/`

Old plans and roadmaps retained as historical planning evidence but not current work orders.

### `archive/audits/`

Historical audit reports, signoffs, and review artifacts retained as evidence but not current authority unless explicitly cited.

### `archive/frozen_artifacts/`

Frozen artifacts retained for reproducibility, baseline comparison, or provenance.

## High caution archive categories

The following archive categories require stricter preflight before any move:

```text
archive/config/
archive/data/
archive/cache/
archive/tmp/
```

Reason:

- `archive/config/` may affect runtime/config authority, tests, and reproducibility.
- `archive/data/` may affect backtest coverage, data-source policy, and reproducibility.
- `archive/cache/` may affect determinism if any pipeline reads from cache paths.
- `archive/tmp/` may contain evidence carriers, generated intermediates, or script-referenced temporary paths.

## Required preflight for every archive move

Before moving a file into `archive/**`, run a reference check for:

- exact path references
- filename references
- imports
- script invocations
- config references
- test references
- CI/workflow references
- documentation links
- generated artifact references

If references exist, update them in the same rename-only slice.

If references cannot be safely updated, do not move the file yet.

## Additional preflight for high-caution categories

For moves into `archive/config/`, `archive/data/`, `archive/cache/`, or `archive/tmp/`, also verify:

- no runtime code reads the old path as an input
- no config authority path depends on the old path
- no tests require the old path
- no deterministic replay/backtest/data-source policy depends on the old path
- no active script expects the old path
- the move is governance-approved for the touched surface class

## PR shape for future archive moves

Archive move PRs should be small and rename-only.

Allowed in archive-move PRs:

- physical file moves
- reference updates caused by the move
- category README updates when needed
- move manifest or audit note

Not allowed in archive-move PRs:

- runtime behavior changes
- strategy changes
- config semantic changes
- tuning changes
- opportunistic cleanup
- content rewrites beyond minimal status/path updates
- pointer stubs by default

## Move manifest recommendation

Each archive-move PR should include a small manifest in the PR body or a docs/audit note:

```text
Moved:
- old/path -> archive/category/path

Reference checks:
- exact path: pass/fail
- filename: pass/fail
- imports: pass/fail
- tests: pass/fail
- CI/workflows: pass/fail

High caution category: yes/no
Reason safe to move:
- ...
```

## Non-claims

This taxonomy does not claim:

- that any current file is safe to move
- that all archive categories are populated
- that all repo folders have been inventoried
- that current authority ambiguity is fully solved
- that archive movement is approved by this document alone

## Summary

Use this taxonomy to prepare controlled physical archive moves.
Do not use it as authority to move files without a separate governed slice and reference checks.
