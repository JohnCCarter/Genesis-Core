# Research code experiment lane v1

Date: 2026-03-27
Status: tracked / analysis-only / governance addition
Lane: `run_intent: research_code_experiment`

## Purpose

This lane adds a separate code-level research path for bounded hypothesis work that cannot proceed inside the current config/artifact-safe `research_experiment` lane.

This lane extends governance. It does not weaken or replace the existing `research_experiment` lane.

## Why the current lane blocks this slice

- The active `research_experiment` lane is config/artifact-safe.
- It does not allow changes under `src/core/**`.
- The blocked RI slice targets `src/core/strategy/prob_model.py`.
- The same slice also depends on regime-aware calibration data currently read from active model metadata under `config/models/**`.
- Continuing that slice inside the current lane would therefore require either:
  - code changes in `src/core/**`, or
  - writeback to active production model metadata paths
- Both are forbidden in the current lane.

## What this lane allows

- bounded research changes in explicitly packeted `src/core/**` surfaces
- matching bounded test changes in `tests/**` only when required to prove determinism, replay, and scope control for the exact slice
- research-only configs and research-only model metadata paths that are isolated from active production paths
- isolated research execution against research-only artifacts and result paths
- one hypothesis, one slice, one bounded surface at a time

## What this lane still forbids

- `src/core/strategy/family_registry.py`
- family rules or family-admission semantics
- `config/strategy/champions/**`
- runtime defaults, including `config/runtime.json`
- active production model metadata paths under `config/models/**`
- comparison, readiness, or promotion opening
- mixed family surfaces or cross-family internal merging
- production writeback
- implicit runtime activation

## Execution constraints

- every run must be explicitly tagged `run_intent: research_code_experiment`
- all artifacts must be isolated from active runtime and production paths
- research-only model metadata must live on separate non-production paths
- determinism and replay evidence remain required
- fail closed on ambiguity

## Smallest admissible next artifact

- one tracked Markdown file under `docs/governance/`
- purpose: open a single bounded code-level research packet for one exact slice
- that packet must name:
  - the exact hypothesis
  - the exact `src/core/**` surface
  - the isolated research-only metadata/config path
  - the minimum evidence package
  - the stop conditions
