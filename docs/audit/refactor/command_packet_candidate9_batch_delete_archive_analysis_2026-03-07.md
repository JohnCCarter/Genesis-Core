# Command Packet (v1.1)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — archive/tooling cleanup only; no runtime path changes.
- **Required Path:** `Full`
- **Objective:** Delete obsolete archive analysis scripts in batch, clean stale archive-doc references, preserve runtime behavior.
- **Candidate:** `candidate9_batch_delete_archive_analysis`
- **Base SHA:** `17c938e7e8d2e43f2446ce50581f20d81b88b952`

### Scope

- **Scope IN:**
  - Delete all Python files under `scripts/archive/analysis/` (12 files):
    - `analyze_feature_importance.py`
    - `analyze_feature_synergy.py`
    - `analyze_permutation_importance.py`
    - `benchmark_optimizations.py`
    - `calculate_ic_metrics.py`
    - `calculate_partial_ic.py`
    - `compare_htf_exits.py`
    - `compare_modes.py`
    - `compare_swing_strategies.py`
    - `fdr_correction.py`
    - `feature_ic_v18.py`
    - `monitor_feature_drift.py`
  - Remove stale archive references in:
    - `docs/archive/deprecated_2026-02-24/docs/validation/VALIDATION_CHECKLIST.md`
    - `docs/archive/deprecated_2026-02-24/docs/validation/ADVANCED_VALIDATION_PRODUCTION.md`
    - `docs/archive/deprecated_2026-02-24/docs/features/INDICATORS_REFERENCE.md`
  - Candidate contract artifact:
    - `docs/audit/refactor/command_packet_candidate9_batch_delete_archive_analysis_2026-03-07.md`
  - Candidate evidence artifacts:
    - `docs/audit/refactor/evidence/candidate9_archive_analysis_manifest_2026-03-07.txt`
    - `docs/audit/refactor/evidence/candidate9_archive_analysis_refcheck_2026-03-07.txt`
  - Candidate signoff artifact:
    - `docs/audit/refactor/candidate9_archive_analysis_delete_signoff_2026-03-07.md`
- **Scope OUT:**
  - `src/**`, `tests/**`, `config/**`, `mcp_server/**`
  - `docs/audit/**` historical evidence artifacts (kept for traceability), except this candidate's contract/evidence/signoff artifacts
  - runtime/config authority paths and all high-sensitivity zones
- **Expected changed files:** `19` (12 deletions + 3 doc edits + 1 contract artifact + 2 evidence artifacts + 1 signoff artifact)
- **Max files touched:** `20`

### Skill Usage

- `repo_clean_refactor` — körs för governance-evidence (SPEC skill; förväntat utfall kan vara `STOP/no_steps`)
- `python_engineering` — körs för governance-evidence (SPEC skill; förväntat utfall kan vara `STOP/no_steps`)

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_htf_exit_atr_no_lookahead.py` # no-lookahead selector
- `python -m pytest -q tests/test_features_asof_cache_key_deterministic.py` # feature cache invariance selector
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` # pipeline hash guard selector
- `python -m pytest -q tests/test_backtest_hook_invariants.py` # pipeline invariant selector
- Smoke: verify zero non-audit/non-archive references to deleted `scripts/archive/analysis/*.py` paths

### Stop Conditions

- Scope drift outside listed files
- Any behavior change in runtime paths
- Determinism/invariant selector regression
- Forbidden/high-sensitivity paths touched

### Output required

- **Implementation Report** (scope summary, file-level changes, gates + outcomes)
- **PR evidence template** with selector outputs and grep/refscan proof
