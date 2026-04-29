# SCPE RI V1 shadow-backtest bridge slice1 containment-fix implementation packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `implementation contract proposed / no behavior change intended`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `tooling`
- **Risk:** `MED` — why: this packet proposes a non-trivial single-file Python script change in import-time bootstrap behavior; intent is no behavior change, but proof is required.
- **Required Path:** `Full`
- **Objective:** remove the out-of-bound filesystem-touch side effect from `scripts/run/run_backtest.py` while preserving canonical CLI behavior, config-package resolution, bounded decision-row outputs, `--no-save` semantics, and intelligence-shadow summary / ledger-root behavior.
- **Candidate:** `shadow bridge containment fix implementation`
- **Base SHA:** `749315ea`

### Constraints

- `NO BEHAVIOR CHANGE`
- `Single-file scope`
- `No writable-surface expansion`
- `No CLI flag changes`
- `No intelligence-shadow logic changes`
- `Stop if second file becomes necessary`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
- **Applied repo-local spec:** `repo_clean_refactor`
- **Reason:** the slice is a small Python no-behavior-change containment fix and must stay tightly scoped, reversible, and fully verified.

### Scope

- **Scope IN:**
  - `scripts/run/run_backtest.py`
  - exact removal hypothesis limited to:
    - `CONFIG_DIR = ROOT_DIR / "config"`
    - `CONFIG_DIR.mkdir(exist_ok=True)`
    - `(CONFIG_DIR / "__init__.py").touch(exist_ok=True)`
- **Scope OUT:**
  - all `src/**`
  - all `tests/**` edits
  - all config/result/artifact changes
  - writable-surface expansion
  - CLI semantics changes
  - intelligence-shadow derivation changes
  - runtime integration/paper/readiness/cutover/promotion widening
- **Expected changed files:** `scripts/run/run_backtest.py`
- **Max files touched:** `1`

### Gates required

#### Supplemental containment proof

1. canonical smoke:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --help`
2. targeted config-package proof:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -c "import sys; from pathlib import Path; root=Path(r'C:/Users/fa06662/Projects/Genesis-Core'); sys.path.insert(0,str(root)); sys.path.insert(0,str(root/'src')); import config; print(config.__all__)"`
3. lint:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/run/run_backtest.py`

#### Targeted existing script behavior selectors

4. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_run_backtest_decision_rows.py tests/backtest/test_run_backtest_intelligence_shadow.py tests/backtest/test_run_backtest_mode_flags.py`

#### Required governance gates for non-trivial slice

5. determinism replay:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
6. feature cache invariance:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_features_asof_cache_isolation.py::test_feature_cache_key_separates_precompute_and_runtime_modes`
7. pipeline invariant check:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- config-package resolution proof fails
- canonical `--help` smoke fails
- any targeted selector fails due to unexpected behavior drift
- any second file becomes necessary
- any suggestion appears that writable-surface expansion is needed

### Output required

- one minimal code diff in `scripts/run/run_backtest.py`
- exact commands run and pass/fail outcomes
- proof that containment blocker is removed without widening behavior
- explicit residual-risk note if any remains
