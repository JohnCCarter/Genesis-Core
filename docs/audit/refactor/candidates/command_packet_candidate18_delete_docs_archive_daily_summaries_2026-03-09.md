# Command Packet — Candidate 18 Delete `docs/archive/.../daily_summaries` subset (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — archive deletion can hide stale path dependencies if scope drifts
- **Required Path:** `Full`
- **Objective:** Execute safe, traceable deletion of deprecated `daily_summaries` archive snapshots after exact-path reference verification.
- **Candidate:** `delete_docs_archive_daily_summaries_candidate18`
- **Base SHA:** `386a71b5`

### Scope

- **Scope IN:**
  - delete targets listed in `docs/audit/refactor/evidence/candidate18_daily_summaries_delete_manifest_2026-03-09.tsv` (34 files)
  - `docs/audit/refactor/command_packet_candidate18_delete_docs_archive_daily_summaries_2026-03-09.md`
  - `docs/audit/refactor/evidence/candidate18_daily_summaries_delete_manifest_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
  - `docs/audit/refactor/evidence/docs_archive_triage_daily_summaries_decision_2026-03-09.md`
  - `docs/audit/refactor/evidence/candidate18_daily_summaries_path_refcheck_2026-03-09.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate18_post_delete_scope_drift_2026-03-09.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate18_gate_transcript_2026-03-09.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate18_daily_summaries_implementation_report_2026-03-09.md` (to be generated)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - non-candidate paths under `docs/archive/**`
- **Expected changed files:** `43` (34 deletes + up to 9 governance/evidence files)
- **Max files touched:** `46`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Change is limited to docs/audit evidence updates + deletion of deprecated archive daily summaries under:
`docs/archive/deprecated_2026-02-24/docs/daily_summaries/`.
No changes in runtime/config/test logic files.

### Evidence for candidate safety

- Manifest: `docs/audit/refactor/evidence/candidate18_daily_summaries_delete_manifest_2026-03-09.tsv`
- Triage matrix: `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- Triage summary: `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
- Batch decision: `docs/audit/refactor/evidence/docs_archive_triage_daily_summaries_decision_2026-03-09.md`
- Path refcheck (to generate): `docs/audit/refactor/evidence/candidate18_daily_summaries_path_refcheck_2026-03-09.txt`
- Scope-drift proof (to generate): `docs/audit/refactor/evidence/candidate18_post_delete_scope_drift_2026-03-09.txt`
- Gate transcript (to generate): `docs/audit/refactor/evidence/candidate18_gate_transcript_2026-03-09.md`

### Skill usage (explicit)

- Repo-local skills invoked: `repo_clean_refactor`, `python_engineering` (governance SPEC evidence).
- Optional supplemental planning aids: `context-map`, `refactor-plan`.
- Invocation evidence recorded in `docs/audit/refactor/evidence/candidate18_gate_transcript_2026-03-09.md`.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** candidate18 deletion.

### Stop Conditions

- Scope drift outside manifest-listed delete targets.
- Any active external reference found outside `docs/archive/**` and `docs/audit/**`.
- Behavior change without explicit exception.
- Determinism/cache/pipeline invariant regression.
- Forbidden paths touched.

### Output required

- **Implementation Report**
- **PR evidence template**
