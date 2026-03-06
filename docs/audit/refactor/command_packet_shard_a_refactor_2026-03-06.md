# Command Packet — Shard A Refactor (2026-03-06)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/*`)
- **Category:** `refactor(server)`
- **Risk:** `MED` — structural refactor in script entrypoints with broad test coupling
- **Required Path:** `Full`
- **Objective:** Continue Shard A refactor with no production behavior change using a second small, atomic structural batch.
- **Candidate:** Batch 2 — `scripts/train/train_model.py` (internal helper dedupe/readability only)
- **Base SHA:** `0cb3bff9b70c3301c5464be05674231116b96797`
- **Working branch:** `feature/refactor-scripts-structure-a`

### Scope

- **Scope IN:**
  - `scripts/**`
  - `scripts/archive/**`
  - `docs/audit/refactor/**` (governance evidence only)
- **Scope OUT:**
  - `src/core/**`
  - `mcp_server/**`
  - `tests/**` (read/verify allowed; edit only if parity proof requires and explicitly approved)
  - cleanup historical docs under `docs/audit/cleanup/**`
- **Expected changed files (Batch 2):**
  - `scripts/train/train_model.py`
  - `docs/audit/refactor/command_packet_shard_a_refactor_2026-03-06.md`
  - `docs/audit/refactor/context_map_shard_a_refactor_2026-03-06.md`
- **Max files touched:** `3`
- **Batch 2 hard lock (exact):**
  - Only the three files above may be edited in Batch 2.
  - Any additional file requires new pre-code approval.

### Gates required

- `pre-commit run --all-files`
- `ruff check .`
- `pytest -q`
- smoke selector: `pytest -q tests/test_import_smoke_backtest_optuna.py`
- Focused selector(s) for Batch 2:
  - `tests/test_train_model.py -q`
- Required in RESEARCH mode:
  - determinism replay selector: `pytest -q tests/test_backtest_determinism_smoke.py`
  - feature cache invariance selector: `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
  - pipeline invariant/hash guard selector: `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Optional situational selectors:
  - freeze guard checks

### Default parity constraints (mandatory)

- No change in default CLI behavior in `scripts/train/train_model.py`.
- No change in env/config interpretation.
- No change in exit codes.
- No change in output payload/file contract.

### Skill Usage

- Invoked (SPEC): `repo_clean_refactor`, `python_engineering`
- Validation support (Batch 2): determinism, feature-cache invariance, and pipeline hash guard selectors
- `feature_parity_check` is not required in Batch 2 because no feature computation logic changed.

### Stop Conditions

- Scope drift outside Shard A
- Behavior change without explicit exception
- Failing parity checks in `test_train_model.py`
- Any forbidden path touched

### Output required

- **Implementation Report**
- **PR evidence template**
