# Experimental research lane guardrail v1

Date: 2026-03-27
Status: tracked / governance reference
Lane: `run_intent: research_experiment`

## Purpose

Introduce a controlled research lane that allows exploration of new hypothesis classes, including coordination, router logic, and cross-family interaction, without violating existing governance constraints.

This lane exists to enable research flexibility while preserving:

- determinism
- auditability
- strict separation between research and runtime authority

## Lane definition

New run intent:

- `run_intent: research_experiment`

This intent is strictly research-only and does not imply:

- runtime validity
- comparison eligibility
- readiness eligibility
- promotion eligibility

## Current ground truth

- Legacy and RI are separate strategy families.
- Mixed family surfaces must not be reintroduced.
- RI has reached a reproducible plateau within the currently tested local research surfaces.
- Further progress requires new hypotheses, not more local tuning of already exhausted RI surfaces.

## Admissible scope

The `research_experiment` lane may:

- introduce coordination logic between strategy families
- introduce router logic above the families
- define new hypothesis classes outside existing RI and Legacy local tuning
- create new research-only configs and artifacts
- operate on multiple families as inputs without merging their internal structures

## Explicitly allowed

- config-only changes as the primary path
- creation of new research configs in JSON or YAML
- creation of coordination or router specifications
- creation of research-only summaries and signoff artifacts
- use of validator and preflight checks
- execution of research runs under isolated configs

## Explicitly forbidden

The `research_experiment` lane must not:

- modify `src/core/**`
- modify family registry or family admission semantics
- modify runtime defaults
- modify or overwrite champion artifacts
- open the comparison lane
- open the readiness lane
- open the promotion lane
- perform writeback to production paths
- treat research results as production-valid signals

## Family separation constraint

All strategy families must remain internally isolated.

The lane may:

- read outputs from multiple families
- coordinate between them externally

The lane must not:

- merge family parameter surfaces
- share thresholds or internal state across families
- reinterpret one family as another

## Execution constraints

All executions within this lane must:

- be explicitly tagged `run_intent: research_experiment`
- use isolated configs and result paths
- be reproducible and deterministic
- pass validator and preflight unless explicitly documented otherwise
- fail closed on ambiguity

## Artifact classification

All outputs from this lane are classified as:

- research-only artifacts
- non-runtime-valid
- non-comparison-eligible unless separately authorized
- non-readiness-eligible
- non-promotion-eligible

## Authority boundary

This lane does not grant authority to:

- change system behavior in runtime
- alter production strategy selection
- update champion configurations
- influence live or paper trading execution

All transitions out of this lane require separate, explicit governance packets.

## Relationship to existing governance

This lane extends governance. It does not weaken it.

- Existing strict lanes remain unchanged.
- This lane only adds controlled flexibility for research.
- Existing safety and validation mechanisms remain active.

## Exit condition

Any artifact or hypothesis produced in this lane must:

- undergo separate evaluation before comparison is allowed
- explicitly pass admissibility for any higher lane
- never bypass governance through implicit assumptions

## Primary rule

This lane enables exploration, not deployment.

If any ambiguity arises:

- fail closed
