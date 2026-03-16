# Intelligence Architecture

Status: ARCHITECTURE SPEC
Authority: Genesis-Core Intelligence Layer

## Preparation-only authority statement

These documents define preparation-only intelligence contracts and package boundaries for future work.
They do not alter or supersede the current runtime regime authority path or existing `core.intelligence.regime` consumption.
Runtime wiring changes require a separate explicitly approved tranche.

## Purpose

Prepare a safe, deterministic workspace for parallel development of the Genesis-Core Intelligence system.
This slice defines structure and interfaces only.

## Canonical package layout

The canonical package root is:

- `src/core/intelligence/`

The preparation-phase subpackages are:

- `events/`
- `collection/`
- `normalization/`
- `features/`
- `evaluation/`
- `ledger_adapter/`
- existing `regime/` package remains unchanged

## Architectural flow

The intended intelligence flow is:

1. collection
2. normalization
3. features
4. evaluation
5. ledger_adapter

This slice establishes the package boundaries for that flow without implementing the flow itself.

## Boundary rules

- `events/` owns canonical event contracts and event validation.
- `collection/` owns the interface for event production.
- `normalization/` owns the interface for deterministic event validation output.
- `features/` owns the interface for feature-set contracts.
- `evaluation/` owns the interface for evaluation output contracts.
- `ledger_adapter/` owns the interface for Research Ledger persistence boundaries.
- `regime/` remains the existing runtime intelligence domain and is out of scope for this prep slice.

## Design constraints

- deterministic only
- strongly typed Python contracts
- stable JSON serialization
- no orchestration logic in this phase
- no runtime processing logic in this phase
- no database complexity in this phase

## Integration intent

Future intelligence work should consume shared contracts from this package layout.
No downstream branch should invent parallel event schemas or local interface definitions.
