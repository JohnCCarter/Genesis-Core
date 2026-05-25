# Batch 006 config classification audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only config-docs classification audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded classification audit for config-adjacent documentation surfaces.
> It does **not** change runtime config semantics, live-write authority, whitelist behavior, API
> interpretation, or governance precedence.
>
> Batch controller for this slice: `docs/system/GENESIS_TOPOLOGY_WORK_QUEUE.md`
> (`Batch 006 — config classification`).
>
> Governance note: this RED-adjacent slice was pre-reviewed as a minimal docs-only packet. The
> approved patch boundary is audit-first, with at most a header-only framing block in
> `docs/config/CHAMPION_REPRODUCIBILITY.md`.

## Scope boundary

Primary surfaces reviewed in this slice:

- `config/README.md`
- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`
- `docs/audit/CONFIG_GOVERNANCE_AUDIT.md`
- `docs/config/CHAMPION_REPRODUCIBILITY.md`

Scope OUT in this slice:

- all runtime/config code and config files with executable semantics
- `docs/CURRENT_AUTHORITY_INDEX.md`
- `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- queue/controller bookkeeping edits
- any body rewrite of `docs/config/CHAMPION_REPRODUCIBILITY.md`
- any change to whitelist meaning, live-update policy, or config-authority semantics

## Skill / guard coverage

Repo-local routing/classification guard consulted:

- `.github/skills/docs_classification_taxonomy_routing.json`

Observed reading:

- it is suitable as a citation-bound classification/routing guard
- it must **not** be used to create new config authority, new runtime conclusions, or silent status
  inheritance

## Method

Checked in this slice:

- full read of the four scoped config-adjacent documentation surfaces
- top-framing/status-note presence near the file top
- stale-example signals inside `docs/config/CHAMPION_REPRODUCIBILITY.md`
- current support from repo-local routing/classification guardrails

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch006_config_classification_evidence.json`

## Observed

### `config/README.md`

Observed role:

- current boundary guide for what is actually used in today's config/runtime paths
- explicitly distinguishes runtime SSOT, guarded propose path, and retained legacy/reference files

Observed reading:

- this file already behaves like a current, bounded config-orientation surface
- it already routes readers to `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`
  for the exact live-update matrix

### `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`

Observed role:

- complementary current-boundary reference note for schema-valid vs live-writable runtime config

Observed reading:

- explicit `Status:` line and current status note already prevent authority drift
- the document clearly says it is not SSOT, not fresh approval, and not authority to expand the
  live-write surface

### `docs/audit/CONFIG_GOVERNANCE_AUDIT.md`

Observed role:

- retained historical config/governance audit evidence from an older branch context

Observed reading:

- explicit `Status:` line and current status note already route readers away from treating it as
  current policy or approval
- it still remains useful provenance for the already-documented B1/B2/B3 framing

### `docs/config/CHAMPION_REPRODUCIBILITY.md`

Observed role:

- active-looking config note about merged-config champion storage and reproducibility

Observed drift signals:

- no `Status:` line or current-use note near the top
- stale-looking import example:
  - `from core.config.config_authority import ConfigAuthority`
- stale-looking CLI path examples:
  - `python scripts/run_backtest.py --config-file ...`
- the body reads procedurally and present-tense enough that readers could over-credit it as current
  operational config guidance if they skim the title and first sections only

Observed boundary note:

- this drift does **not** by itself prove the underlying conclusion is false
- it does prove that the document currently needs top-framing so it is not misread as a standalone
  current config-authority instruction surface

## Inferred

- `config/README.md` should be kept as the current quick boundary guide for config usage and runtime
  write semantics
- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md` should be kept as a bounded
  complementary reference note
- `docs/audit/CONFIG_GOVERNANCE_AUDIT.md` should be kept as retained historical provenance
- `docs/config/CHAMPION_REPRODUCIBILITY.md` is the only patch-safe candidate in this slice, and the
  safe change is **header-only framing** that:
  - marks the file as reproducibility/reference context
  - points readers to `config/README.md` and the live-update matrix for current operational
    boundary guidance
  - warns that examples below may reflect historical import paths or CLI entrypoints

## UNRESOLVED

- `UNRESOLVED:` whether the body of `docs/config/CHAMPION_REPRODUCIBILITY.md` should later be
  updated line-by-line, archived, or split into historical-vs-current sections in a separate slice
- `UNRESOLVED:` whether adjacent config docs outside this scope still carry stale direct CLI/import
  examples that deserve a later bounded cleanup batch
- `UNRESOLVED:` whether any future current-authority index update should explicitly classify
  `docs/config/**` surfaces once the user-modified top-level authority maps are out of the way

## Batch result summary

- Candidates reviewed: `4`
- `KEEP_CURRENT_BOUNDARY`: `2`
- `KEEP_PROVENANCE`: `1`
- `READY_STATUS_HEADER`: `1`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                         | Observed role                                           | Current reading                                                                  | Classification          | Safe batch action      |
| ----------------------------------------------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------- | ---------------------- |
| `config/README.md`                                                | current config/runtime boundary guide                   | already current and bounded                                                      | `KEEP_CURRENT_BOUNDARY` | no change              |
| `docs/governance/runtime_config_live_update_matrix_2026-05-15.md` | complementary live-update boundary reference            | already framed as complementary / non-authorizing                                | `KEEP_CURRENT_BOUNDARY` | no change              |
| `docs/audit/CONFIG_GOVERNANCE_AUDIT.md`                           | historical config/governance audit evidence             | already historical/provenance-framed                                             | `KEEP_PROVENANCE`       | no change              |
| `docs/config/CHAMPION_REPRODUCIBILITY.md`                         | active-looking reproducibility note with stale examples | lacks top framing and may be skim-misread as current operational config guidance | `READY_STATUS_HEADER`   | add intro framing only |

## What changed vs. what did not change

This audit supports changing:

- only the intro framing of `docs/config/CHAMPION_REPRODUCIBILITY.md`

This audit does **not** support changing:

- example code blocks inside `docs/config/CHAMPION_REPRODUCIBILITY.md`
- command examples inside `docs/config/CHAMPION_REPRODUCIBILITY.md`
- `config/README.md`
- the live-update matrix
- the historical config audit
- runtime/config semantics or policy

## Bottom line

Batch 006 does not need a broad config-doc rewrite.

It needs a **classification-first reading**:

- keep the current config boundary guide current
- keep the live-update matrix complementary
- keep the older audit as provenance
- add only a narrow top-framing block to `docs/config/CHAMPION_REPRODUCIBILITY.md` so it reads as
  reproducibility/reference material rather than a standalone current authority surface
