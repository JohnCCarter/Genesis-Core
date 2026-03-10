# COMMAND PACKET

- **Mode:** `RESEARCH` (edit-only)
- **Risk:** `LOW`
- **Required Path:** `Full`
- **Objective:** Relocate `test_champion_loader.py` to `tests/utils/` with no behavior change.
- **Candidate:** `tests/test_champion_loader.py -> tests/utils/test_champion_loader.py`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Status:** `READY_FOR_COORDINATOR_GATES`

## Scope

- **Scope IN:** moved candidate test file, classification plan update, this packet.
- **Scope OUT:** `src/**`, `scripts/**`, `config/**`, `.github/workflows/**`.

## Gates (coordinator run required)

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/utils/test_champion_loader.py`
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/utils/test_pipeline_fast_hash_guard.py`

## Evidence

- Edit-only execution: file move + docs update completed.
- No terminal commands executed in this step.
- Gate execution deferred to coordinator.
