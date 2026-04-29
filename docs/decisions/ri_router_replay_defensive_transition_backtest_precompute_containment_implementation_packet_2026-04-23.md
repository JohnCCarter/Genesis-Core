# RI router replay defensive-transition backtest precompute containment implementation packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `implementation contract proposed / default path unchanged intended`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice touches `src/core/backtest/engine.py`, which is a high-sensitivity runtime surface. The intended change is tightly bounded and default-preserving, but it still alters runtime write behavior when one new env flag is explicitly set.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the blocker is no longer conceptual or docs-only; the repo-visible paired launch surface is blocked by a real runtime write path inside canonical precompute, so the smallest honest next step is one bounded runtime containment fix rather than another purely descriptive packet.
- **Objective:** introduce one explicit opt-in containment mechanism that suppresses out-of-bound `cache/precomputed/*.npz` writes for the exact paired defensive-transition backtest surface while preserving default canonical behavior, in-memory precompute behavior, and existing cache-read behavior.
- **Candidate:** `defensive-transition paired backtest precompute containment fix`
- **Base SHA:** `de2b14b9`

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/backtest/engine.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - the blocker is localized to `BacktestEngine.load_data()` rather than to a docs-only ambiguity,
  - the current paired launch packets already documented the blocker honestly,
  - launch cannot move forward unless the runtime write path is either suppressed or separately widened,
  - widening writable surfaces is explicitly non-preferred for this lane.
- **Default-path stance:** `unchanged / explicit exception required`
- **Required packet / review:**
  - Opus pre-code review required before implementation
  - Opus post-diff audit required after implementation

### Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when GENESIS_PRECOMPUTE_CACHE_WRITE=0 is explicitly set`
- `High-sensitivity zone`
- `No CLI flag changes`
- `No cache-key logic changes`
- `No lookup-order changes`
- `No in-memory precompute disablement`
- `No launch authorization refresh in this slice`
- `No writable-surface expansion approval`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
- **Reason:** this is a Python runtime slice that must remain typed, narrowly scoped, test-backed, and verification-first.
- **Applied repo-local spec:** `genesis_backtest_verify`
- **Reason:** even though no backtest is executed here, the slice must preserve deterministic comparison discipline and avoid hidden artifact drift on default paths.
- **Deferred:** `backtest_run`
- **Reason:** this slice does not execute a runnable paired backtest and therefore does not claim run-surface coverage.

### Narrow contract exception

Exception to the default `NO BEHAVIOR CHANGE` rule for this slice only:

- **opt-in behavior change candidate limited to `GENESIS_PRECOMPUTE_CACHE_WRITE=0`**, which suppresses `cache/precomputed/` directory creation and `.npz` writes on cache miss while preserving existing-cache reads and in-memory precompute; default behavior remains unchanged when the variable is absent.

### Scope

- **Scope IN:**
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_precompute_containment_implementation_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/backtest/engine.py`
  - `tests/backtest/test_backtest_engine.py`
  - one minimal stale-claim correction in `docs/decisions/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md`
- **Scope OUT:**
  - `scripts/run/run_backtest.py`
  - all other `src/**`
  - all other `tests/**`
  - all `config/**`
  - launch authorization refresh
  - actual baseline/candidate execution
  - any writable-surface expansion beyond the env-gated suppression mechanism
- **Expected changed files:**
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_precompute_containment_implementation_packet_2026-04-23.md`
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/backtest/engine.py`
  - `tests/backtest/test_backtest_engine.py`
- **Max files touched:** `5`

### Hypothesis under implementation

The bounded implementation hypothesis is:

- canonical paired execution does not need on-disk precompute writes in order to keep precomputed features available for the run itself
- the write blocker can be localized to the cache-write-prep and cache-write branch in `BacktestEngine.load_data()`
- a new explicit env flag can suppress only `mkdir` plus `_np.savez_compressed(...)` on cache miss while leaving cache reads, cache keys, lookup order, and in-memory precompute intact
- this containment capability can be introduced without widening CLI surfaces or mutating default canonical behavior

If any of the above proves false, the slice must stop and re-packet rather than broaden in place.

### Gates required

#### Targeted local proof

1. pre-commit on touched files:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pre_commit run --files docs/decisions/ri_router_replay_defensive_transition_backtest_precompute_containment_implementation_packet_2026-04-23.md docs/decisions/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md GENESIS_WORKING_CONTRACT.md src/core/backtest/engine.py tests/backtest/test_backtest_engine.py`
2. focused engine proof:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_engine.py`
   - this proof set must include explicit cache-miss parity for env-absent versus `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
3. smoke selector:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`

#### Required governance gates for high-sensitivity slice

4. determinism replay:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
5. feature cache invariance:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_features_asof_cache_isolation.py::test_feature_cache_key_separates_precompute_and_runtime_modes`
6. pipeline invariant check:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
7. security hygiene for touched runtime surface:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -r src/core/backtest -c bandit.yaml`

### Stop Conditions

- any change in `scripts/run/run_backtest.py` becomes necessary
- any change outside `src/core/backtest/engine.py` becomes necessary to make the env flag work
- cache-key material or lookup order must change
- in-memory precompute must be disabled or altered to make suppression work
- default behavior changes when `GENESIS_PRECOMPUTE_CACHE_WRITE` is absent
- the stale boundary-packet correction requires more than a minimal wording fix

### Output required

- one bounded runtime diff rooted only in `src/core/backtest/engine.py`
- proof that `GENESIS_PRECOMPUTE_CACHE_WRITE=0` suppresses `cache/precomputed/` write prep/write on cache miss
- proof that existing cache reads still work when suppression is enabled
- proof that cache-miss runtime results remain parity-stable between env-absent and `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- proof that default behavior remains unchanged when the env flag is absent
- exact commands run and pass/fail outcomes
- explicit note that launch authorization is still a separate later packet

## Bottom line

This packet proposes one exact next runtime containment slice only:

- keep canonical default behavior unchanged
- add one explicit env-gated suppression path for precompute disk writes
- keep CLI unchanged
- keep the launch/authorization packet chain separate

No execution or launch authorization is granted by this packet alone.
