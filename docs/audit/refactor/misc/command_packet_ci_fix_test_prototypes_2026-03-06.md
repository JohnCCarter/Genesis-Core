# Command Packet — CI Fix + test_prototypes Review (2026-03-06)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Category:** `docs`
- **Risk:** `LOW` — docs/evidence-only; no runtime paths
- **Required Path:** `Full` (non-trivial low-risk), with reduced docs-only gates per repo policy
- **Objective:** Resolve CI pre-commit EOF failure in evidence JSON files and continue work by adding focused `test_prototypes` review evidence.
- **Base SHA:** `b2981a75`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/evidence/jscpd_scripts_2026-03-06/jscpd-report.json`
  - `docs/audit/refactor/evidence/jscpd_scripts_final_2026-03-06/jscpd-report.json`
  - `docs/audit/refactor/evidence/jscpd_scripts_final_summary_2026-03-06.json`
  - `docs/audit/refactor/evidence/jscpd_scripts_summary_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_archive_external_refscan_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_archive_external_refscan_final_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_archive_external_refscan_final_summary_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_archive_external_refscan_summary_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_breadth_grouping_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_breadth_grouping_final_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_breadth_inventory_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_breadth_inventory_final_2026-03-06.json`
  - `docs/audit/refactor/evidence/shard_a_git_history_families_2026-03-06.json`
  - `docs/audit/refactor/evidence/test_prototypes_reference_scan_2026-03-06.json`
  - `docs/audit/refactor/evidence/test_prototypes_review_snapshot_2026-03-06.json`
  - `docs/audit/refactor/test_prototypes_review_2026-03-06.md`
  - `docs/audit/refactor/command_packet_ci_fix_test_prototypes_2026-03-06.md`
- **Scope OUT:**
  - `src/**`
  - `scripts/**` (runtime/tools)
  - `tests/**`
  - `config/**`
  - `.github/workflows/**`
- **Expected changed files:** `17`
- **Max files touched:** `17`

### Gates required (docs-only reduced set)

- `pre-commit run --all-files`
- JSON syntax validation for new evidence files:
  - `docs/audit/refactor/evidence/test_prototypes_review_snapshot_2026-03-06.json`
  - `docs/audit/refactor/evidence/test_prototypes_reference_scan_2026-03-06.json`
- Scope allowlist check: `git diff --name-only` must stay within `docs/audit/refactor/**`

### Default parity constraints (mandatory)

- No behavior change.
- No runtime/config/API/env interpretation changes.
- Existing evidence JSON files may only receive EOF/format hygiene edits.

### Stop Conditions

- Any scope drift outside `docs/audit/refactor/**`.
- Any semantic mutation in existing evidence payloads beyond EOF/format hygiene.
- Any gate failure.
- If scope drift occurs: escalate to full RESEARCH selector-gates (determinism replay + pipeline invariant).

### Output required

- **Implementation Report**
- **PR evidence template**
