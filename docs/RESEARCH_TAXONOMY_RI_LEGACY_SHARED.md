# Research Taxonomy — RI / Legacy / Shared

Date: 2026-05-26
Mode: `RESEARCH`
Status: `docs-only / non-authorizing / taxonomy aid / no behavior change`

## Purpose

This document proposes a practical reading and classification taxonomy for Genesis-Core research surfaces.

Goal:

- reduce semantic ambiguity
- improve human and AI-agent navigation
- clarify whether a research surface primarily belongs to RI, Legacy, or Shared topology
- reduce accidental cross-family interpretation drift

This file does not create runtime authority, family authority, or governance authority.

## Scope boundary

### Scope IN

- reading/navigation taxonomy
- research-surface classification
- folder-placement recommendations
- RI vs Legacy interpretation aid
- future rename-only candidate guidance

### Scope OUT

- runtime changes
- family merge proposals
- cross-family router approval
- promotion/readiness claims
- Canon changes
- deleting or archiving files
- mandatory folder migrations

## Working definitions

### RI

Research, routing, regime, or policy surfaces that are explicitly tied to Regime Intelligence family behavior.

Typical indicators:

- RI-only router semantics
- regime classification
- policy routing
- continuation / defensive-transition state logic
- RI-local attribution
- RI-specific admissibility or authority clustering

### Legacy

Baseline or control-family surfaces representing the canonical or comparison reference path.

Typical indicators:

- baseline champion references
- control setup
- canonical benchmark behavior
- stable comparison path
- legacy-specific policy routing
- frozen or reference execution semantics

### Shared

Infrastructure, orchestration, or analysis surfaces that serve both RI and Legacy without themselves defining family identity.

Typical indicators:

- execution backbone
- deterministic framework
- backtest engine
- replay system
- data contracts
- common evaluation infrastructure
- family-agnostic topology research

## Proposed classification guide

| Area | Suggested classification | Notes |
|---|---|---|
| `src/core/strategy/ri_policy_router.py` | RI | RI-family-local semantics even when called from shared orchestration |
| `src/core/strategy/family_registry.py` | Shared | shared family-validation infrastructure |
| `src/core/strategy/family_admission.py` | Shared | shared admission layer across families |
| `src/core/strategy/decision.py` | Shared | shared decision backbone |
| RI regime-state research | RI | family-local research semantics |
| RI policy attribution | RI | family-local attribution surfaces |
| Legacy policy-router packets | Legacy | baseline/control-family semantics |
| baseline champion evidence | Legacy | canonical benchmark/control role |
| edge-topology research | Shared | potentially family-agnostic unless explicitly RI-only |
| replay / deterministic evidence | Shared | cross-family infrastructure |
| feature attribution post-phase14 RI surfaces | RI | explicitly RI-first current framing |

## Suggested future logical layout

This is a navigation recommendation only.
No move is authorized by this document.

### Suggested docs structure

```text
/docs/analysis/ri/
/docs/analysis/legacy/
/docs/analysis/shared/
```

### Suggested research-results structure

```text
/results/research/ri/
/results/research/legacy/
/results/research/shared/
```

### Suggested scripts structure

```text
/scripts/analyze/ri/
/scripts/analyze/legacy/
/scripts/analyze/shared/
```

## Important reading rule

Shared placement does not imply shared family semantics.

Examples:

- RI router inside shared orchestration does not make the router cross-family.
- Shared execution backbone does not collapse RI and Legacy into one family.
- Shared evaluation infrastructure does not imply shared admissibility.

## Current risk areas

### Historical wording drift

Older overlay language may coexist with newer family-separated framing.
Interpret such documents through current authority and bounded scope notes.

### Naming ambiguity

The following terms are easy to mentally collapse into one concept:

- authority
- family identity
- admission
- routing
- runtime placement

Do not assume these terms are interchangeable.

### Research evidence over-authority

Large research packets or diagnostics can appear more authoritative than they are.
Always verify whether the surface is:

- observational
- bounded
- non-authorizing
- historical
- archived
- current runtime authority

## Rename-only candidate examples

These are examples only.
No move is approved by this document.

Possible future rename-only migrations:

```text
/docs/analysis/regime_intelligence/ -> /docs/analysis/ri/
/docs/decisions/legacy/ -> /docs/analysis/legacy/
/docs/analysis/edge_topology/ -> /docs/analysis/shared/edge_topology/
```

## Remaining open questions

This taxonomy does not yet prove:

- whether current RI/Legacy separation is the final ideal architecture
- whether some RI surfaces could later become more generic
- whether all current shared surfaces are optimally placed
- whether the repo needs a future physical split
- whether every existing document is correctly classified

## Summary

Current evidence suggests Genesis-Core already behaves more like:

- one shared deterministic backbone
- plus separate RI and Legacy family-conditioned surfaces

than either:

- two entirely separate engines
- or one family with small flags.

This taxonomy attempts to make that reading easier without changing runtime behavior or governance authority.
