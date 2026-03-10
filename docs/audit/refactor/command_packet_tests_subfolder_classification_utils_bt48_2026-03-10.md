# COMMAND PACKET

- **Mode:** `RESEARCH`
- **Risk:** `LOW` — single test-file relocation only.
- **Objective:** Relocate `test_optimizer_cli.py` to `tests/utils/` with no behavior change.
- **Candidate:** `tests/test_optimizer_cli.py -> tests/utils/test_optimizer_cli.py`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE`

### Scope IN

- `tests/test_optimizer_cli.py`
- `tests/utils/test_optimizer_cli.py`
- `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
- `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt48_2026-03-10.md`

### Scope OUT

- `src/**`, `scripts/**`, `config/**`, `.github/workflows/**`

### Gate status

- `NOT RUN (edit-only mode by coordinator instruction)`

`READY_FOR_COORDINATOR_GATES`

---

# COMMAND PACKET (bt36 agent - champion_loader)

- **Mode:** `RESEARCH` (edit-only)
- **Risk:** `LOW`
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

## Evidence

- Edit-only execution: file move + docs update completed.
- Gate execution deferred to coordinator.
