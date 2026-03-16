# Intelligence Parallel Development Rules

Status: ARCHITECTURE SPEC
Authority: Genesis-Core Intelligence Layer

## Purpose

Define ownership and merge sequencing for parallel editor work on the Genesis-Core Intelligence system.

## Ownership

### Editor 1

Branch:

- `feature/intelligence-pipeline-v1`

Owner of:

- event schema
- contracts
- pipeline structure

### Editor 2

Branch:

- `feature/research-ledger-integration-v1`

Owner of:

- ledger adapter implementation

### Editor 3

Branch:

- `feature/parameter-intelligence-analysis-v1`

Owner of:

- analysis logic and evaluation models

### Editor 4

Branch:

- `feature/research-orchestrator-v1`

Owner of:

- orchestrator architecture only (design first)

## Restrictions

- Editors may not modify the `IntelligenceEvent` schema.
- Editors must import shared contracts rather than redefine them.
- Editors must not refactor unrelated modules.
- If a contract gap is discovered, stop and report it rather than inventing a local solution.
- Runtime intelligence wiring changes require a separate approved slice.

## Merge order

The required merge order is:

1. `intelligence-pipeline-v1`
2. `research-ledger-integration-v1`
3. `parameter-intelligence-analysis-v1`
4. `research-orchestrator-v1`
