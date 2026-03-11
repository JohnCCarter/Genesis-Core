# Focused review — `scripts/archive/test_prototypes` (2026-03-06)

Mode: RESEARCH (source=branch mapping `feature/*`)

## Scope

Targeted review of `scripts/archive/test_prototypes/**` to determine whether this group should be removed, moved, or intentionally preserved.

## Evidence used

- `docs/audit/refactor/evidence/test_prototypes_review_snapshot_2026-03-06.json`
- `docs/audit/refactor/evidence/test_prototypes_reference_scan_2026-03-06.json`
- `docs/audit/refactor/shard_a_breadth_audit_report_2026-03-06.md`

## Findings

From `test_prototypes_review_snapshot_2026-03-06.json`:

- `file_count`: **36**
- `uses_sys_path_hack`: **23**
- `uses_core_imports`: **32**
- `has_main_block`: **35**
- `writes_output_files`: **6**
- `mentions_backtest`: **21**

Interpretation: the folder is predominantly script-style historical experiments/prototypes (manual entrypoints, path hacks, ad-hoc output writes), not production/runtime entrypoints.

From `test_prototypes_reference_scan_2026-03-06.json`:

- `total_hit_files`: **12**
- top-level hits: `docs` = **11**, `src` = **1**
- Runtime references in active `scripts/**`/`src/**` logic were **not** found as dependencies; the `src` hit is metadata listing in `src/genesis_core.egg-info/SOURCES.txt`.

Interpretation: references are documentation/evidence-oriented rather than active execution contracts.

## Classification decision

- Group: `archive/test_prototypes`
- Classification: **ALLOWLIST / KEEP ARCHIVED**
- Rationale:
  1. Historical reproducibility and forensic value.
  2. Low runtime benefit from migration/removal.
  3. No material active-surface dependency signal.

## Recommended action (this pass)

- Keep folder archived and excluded from active runtime surface.
- Do not promote these scripts to canonical `scripts/**` without explicit follow-up contract.
- Record this focused verdict as supporting evidence for Shard A breadth audit closure.
