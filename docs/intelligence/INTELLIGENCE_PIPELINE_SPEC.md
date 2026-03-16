# Intelligence Pipeline Specification

Status: ARCHITECTURE SPEC
Authority: Genesis-Core Intelligence Layer

## Preparation-only authority statement

This document defines preparation-only intelligence pipeline contracts and package boundaries.
It does not alter the current runtime regime authority path or existing `core.intelligence.regime` runtime consumption.
Runtime wiring changes require a separate explicitly approved tranche.

## Purpose

Define the canonical pipeline contract so multiple editors can work in parallel against shared interfaces.
No processing logic is implemented in this preparation slice.

## Pipeline stages

### Stage 1 — Collection

Input:

- source-specific collection request

Output:

- `IntelligenceEvent`
- canonical output shape: `tuple[IntelligenceEvent, ...]`

### Stage 2 — Normalization

Input:

- `tuple[IntelligenceEvent, ...]`

Output:

- `tuple[ValidatedIntelligenceEvent, ...]`

### Stage 3 — Features

Input:

- `tuple[ValidatedIntelligenceEvent, ...]`

Output:

- `tuple[IntelligenceFeatureSet, ...]`

### Stage 4 — Evaluation

Input:

- `tuple[IntelligenceFeatureSet, ...]`

Output:

- `tuple[IntelligenceEvaluation, ...]`

### Stage 5 — Ledger Adapter

Input:

- canonical intelligence event contracts
- canonical intelligence evaluation contracts when relevant in later slices

Output:

- ledger persistence request/result contracts only in this phase

## Determinism rules

- repeated serialization of the same event must be byte-for-byte identical
- event references must preserve a stable explicit order
- validation must not depend on external systems
- pipeline contracts must remain pure and side-effect free

## Out of scope

This preparation slice does not implement:

- event collection logic
- normalization algorithms
- feature extraction logic
- evaluation logic
- Research Ledger write logic
- orchestration or scheduling logic
