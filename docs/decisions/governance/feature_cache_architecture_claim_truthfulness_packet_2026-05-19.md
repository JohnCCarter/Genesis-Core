# Feature-cache architecture claim truthfulness packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `implemented / docs-only / truthfulness-correction`

This packet records one bounded docs-only truthfulness correction for an over-strong architecture claim. It does not change runtime behavior, approve a writer/schema-owner claim, create a new feature-cache authority contract, or reopen runtime work.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice corrects wording only and does not touch runtime or test surfaces
- **Required Path:** `Quick` — why: two files only, no runtime behavior change, no dependency/schema/env/default changes
- **Lane:** `Research-evidence` — why: this slice narrows a stale architecture claim to current tracked evidence
- **Skill usage:** `none required` — bounded docs-only truthfulness correction
- **Objective:** replace the stale `Feature-cache` claim in `CLAUDE.md` with wording grounded in the currently tracked read-side feature artifact path
- **Related artifacts:** `docs/decisions/governance/feature_cache_carrier_trace_packet_2026-05-19.md`, `CLAUDE.md`, `data/DATA_FORMAT.md`, `src/core/utils/data_loader.py`

### Scope

- **Scope IN:** this packet; one wording correction in `CLAUDE.md` limited to the feature-artifact/storage line
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `artifacts/**`, and `results/**`; any writer/schema-owner claim; any schema-version claim; any runtime-readiness or promotion claim
- **Expected changed files:** `docs/decisions/governance/feature_cache_architecture_claim_truthfulness_packet_2026-05-19.md`, `CLAUDE.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the correction stays read-side only
- manual wording audit that no writer/schema-owner/schema-version claim is reintroduced
- self-review for hidden behavior impact

## Purpose

This packet answers one narrow question only:

- what wording in `CLAUDE.md` is supported by current tracked evidence for on-disk feature artifacts?

## What changed in this slice

- one new docs-only truthfulness packet records the evidence boundary
- `CLAUDE.md` no longer describes the seam as a disk-backed `Feature-cache` with `schema_version=1`
- `CLAUDE.md` now describes the grounded read-side shape only: `.feather` / `.parquet` feature artifacts under `data/curated/v1/features`, `data/archive/features`, and `data/features`

## What did not change

- no runtime feature/cache behavior changed
- no feature writer/schema-owner was introduced or asserted
- no data format/schema contract changed
- no tests changed
- no training, backtest, or pipeline code changed

## Governing basis

### Observed

1. `CLAUDE.md` previously claimed: `Feature-cache: PyArrow-columnar data på disk (schema_version=1)`.
2. `src/core/utils/data_loader.py::load_features(...)` currently reads feature artifacts from `data/curated/v1/features`, `data/archive/features`, and `data/features`.
3. The same reader currently prefers `.feather` first and then `.parquet`.
4. `data/DATA_FORMAT.md` currently says `data/features/` is empty/reserved and that older features live in `data/archive/features/`.
5. `docs/decisions/governance/feature_cache_carrier_trace_packet_2026-05-19.md` already concluded that the read-side carrier is grounded, while a current tracked writer/schema-owner is not grounded in this branch review.

### Inferred

- the current tracked evidence supports a read-side feature-artifact description
- the previous `Feature-cache` + `schema_version=1` wording was stronger than the current branch evidence supports
- the smallest honest correction is therefore to describe the read-side directories and file formats only

### Unverified

- a current tracked writer/schema-owner for these feature artifacts
- a current branch-wide schema-version authority for the read-side feature files
- whether any future runtime or training slice should standardize a stronger storage contract

## Applied correction

`CLAUDE.md` now says:

- `Feature artifacts (training/read-side): .feather / .parquet-filer under data/curated/v1/features, data/archive/features och data/features`

This keeps the instruction file useful while removing the over-strong cache/schema claim.

## Bottom line

The current branch review grounds a read-side feature-artifact seam, not a tracked disk-cache/schema-owner contract. This slice therefore corrects `CLAUDE.md` to the smaller truthful statement and leaves any stronger storage-contract claim explicitly unverified.
