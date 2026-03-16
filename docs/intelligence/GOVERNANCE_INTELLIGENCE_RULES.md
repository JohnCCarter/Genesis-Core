# Governance Intelligence Rules

Status: ARCHITECTURE SPEC
Authority: Genesis-Core Intelligence Layer

## Purpose

This document defines the governance rules for the Genesis-Core Intelligence preparation phase.
It establishes the contract boundaries that all future intelligence work must follow.

## Source of truth

The following files are the canonical intelligence preparation specifications:

- `docs/intelligence/GOVERNANCE_INTELLIGENCE_RULES.md`
- `docs/intelligence/INTELLIGENCE_ARCHITECTURE.md`
- `docs/intelligence/INTELLIGENCE_PIPELINE_SPEC.md`
- `docs/intelligence/INTELLIGENCE_EVENT_SCHEMA.md`
- `docs/intelligence/INTELLIGENCE_PARALLEL_DEVELOPMENT_RULES.md`

## Core rules

1. Intelligence work must remain deterministic.
2. Intelligence contracts must be audit-friendly and JSON-serializable.
3. No hidden side effects are allowed in contract or interface modules.
4. The preparation phase may define contracts, interfaces, package layout, and tests only.
5. The preparation phase must not add runtime intelligence processing logic.
6. The preparation phase must not add database complexity, orchestration logic, or intelligence analysis logic.
7. Shared contracts must be imported from canonical intelligence modules rather than redefined locally.
8. If a contract gap is discovered, stop and report it instead of inventing a local workaround.

## Architecture boundary

The intelligence layer is a structured analysis and governance layer that will integrate with the Research Ledger.
It must not become a detached autonomous tuner.

## Runtime authority boundary

These preparation documents do not alter or supersede the current runtime regime authority path or the existing `core.intelligence.regime` consumption pattern.
Any runtime wiring change requires a separate explicitly approved tranche.

## Ledger boundary

Future ledger integration must occur through the canonical intelligence ledger adapter boundary.
The preparation phase must not implement ledger persistence logic yet.

## Schema boundary

The canonical `IntelligenceEvent` schema defined in `INTELLIGENCE_EVENT_SCHEMA.md` is frozen for the parallel development phase.
Editors may not modify that schema without an explicit follow-up contract slice.
