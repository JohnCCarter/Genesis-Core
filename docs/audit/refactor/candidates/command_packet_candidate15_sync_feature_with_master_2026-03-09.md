# Command Packet — Candidate 15 Sync feature with master (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/refactor-scripts-structure-a`)
- **Risk:** `MED` — integration of `origin/master` history into active feature branch
- **Required Path:** `Full`
- **Objective:** Sync `feature/refactor-scripts-structure-a` with `origin/master`, run full gates, and prepare merge-readiness evidence.
- **Candidate:** `sync_feature_with_master_candidate15`
- **Base SHA:** `c31bc3d9`

### Scope

- **Scope IN:**
  - Merge commit from `origin/master` into `feature/refactor-scripts-structure-a`
  - `docs/audit/refactor/command_packet_candidate15_sync_feature_with_master_2026-03-09.md`
  - Optional evidence artifact(s) for gate transcript / merge readiness under `docs/audit/refactor/evidence/`
- **Scope OUT:**
  - No direct manual edits under `src/**`, `config/**`, `mcp_server/**`, `.github/workflows/**`
  - No behavior-change edits; only integration from `origin/master`
- **Expected changed files:** `integration-dependent (from origin/master merge)`
- **Max files touched:** `integration-dependent + <=3 evidence files`

### Constraints

- **NO BEHAVIOR CHANGE** by manual edits.
- Resolve merge conflicts minimally; prefer upstream/master truth unless governance constraints require alternative.
- Keep changes scoped to sync + evidence only.

### Skill usage evidence

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`

### Gates required (pre + post)

- `pre-commit run --all-files`
- `pytest -q tests/test_import_smoke_backtest_optuna.py`
- `pytest -q tests/test_backtest_determinism_smoke.py`
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Post-merge mode resolver check (fail-closed): if touched paths trigger freeze escalation, STOP and reclassify to `STRICT`

### Stop Conditions

- Scope drift outside sync/evidence intent
- Behavior change by manual edits without explicit exception
- Determinism/cache/pipeline invariant regressions
- Forbidden paths touched by manual patching
- If merge introduces touches under `config/strategy/champions/**` or `.github/workflows/champion-freeze-guard.yml` => STOP, reclassify to `STRICT`, and rerun pre-code review

### Output required

- **Implementation Report**
- **PR evidence template (merge-readiness evidence summary + gate outcomes/selectors)**

### Candidate boundary

- Branch creation for next workstream (`feature/archive-mixed-assets-curation`) is explicitly out of Candidate15 and must be handled in a separate candidate packet.
