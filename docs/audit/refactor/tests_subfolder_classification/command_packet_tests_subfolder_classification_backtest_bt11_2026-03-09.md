# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `LOW` — why: path-only relocation av sista flat backtest-testet + uppdatering av aktiv docs-referens.
- **Required Path:** `Full`
- **Objective:** Relocate `test_backtest_engine.py` to `tests/backtest/` and update active non-archive docs reference.
- **Candidate:** `tests/test_backtest_engine.py -> tests/backtest/test_backtest_engine.py`
- **Base SHA:** `5751ad3f`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (enbart filflytt + pathreferenser i docs; ingen runtime/API/env/config-semantik ändras).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: single-candidate move, active docs refs limited to one non-archive location
- **Required Path:** `Full`
- **Objective:** Complete backtest flat-root cleanup by moving remaining backtest engine test.
- **Candidate:** `test_backtest_engine.py`
- **Base SHA:** `5751ad3f`

### Scope

- **Scope IN:**
  - `tests/test_backtest_engine.py` (move source)
  - `tests/backtest/test_backtest_engine.py` (move target)
  - `docs/OPUS_46_GOVERNANCE.md` (active docs path update)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (batch progress row)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_backtest_bt11_2026-03-09.md`
- **Scope OUT:**
  - `src/**`, `mcp_server/**`, `scripts/**`, `config/**`
  - `.github/workflows/**`
  - All docs outside `docs/OPUS_46_GOVERNANCE.md`, `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`, and this BT11 command packet
  - `docs/archive/**` historical references (deferred harmonization batch)
  - Any additional test-file moves
  - Generated metadata/cache paths (`.pytest_cache/**`, `**/*.egg-info/**`)
- **Expected changed files:** 4-5
- **Max files touched:** 5

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/backtest/test_backtest_engine.py`
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
- Selectors:
  - determinism replay: `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - feature cache invariance: `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
  - pipeline invariant: `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`

### Stop Conditions

- Scope drift outside Scope IN
- Behavior change utan explicit undantag
- Determinism/cache/pipeline selector regression
- Forbidden runtime/high-sensitivity paths touched

### Output required

- **Implementation Report**
- **PR evidence template**

### Skill Usage

- `repo_clean_refactor` (SPEC reference)
- `python_engineering` (SPEC reference)

### Skill invocation evidence (planned)

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` -> expected `STOP/no_steps`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` -> expected `STOP/no_steps`

### Branch/mode evidence (pre-coding)

- `git status -sb` -> `## feature/tests-subfolder-classification...`

### Context map evidence (pre-coding)

- Remaining flat backtest candidate inventory: `tests/test_backtest_engine.py` only.
- Active non-archive docs ref to old path: `docs/OPUS_46_GOVERNANCE.md`.
- Archive docs refs (`docs/archive/**`) deferred per scope discipline.

### Pre-coding verification evidence

- `git status -sb` -> `## feature/tests-subfolder-classification...`
- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` -> **STOP/no_steps** (expected), exit code `1`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` -> **STOP/no_steps** (expected), exit code `1`

### Review + verification evidence

- Opus pre-code review: **APPROVED_WITH_NOTES** -> fixes applied -> **APPROVED/GO**
- `python -m pre_commit run --all-files`: **PASS**
- `python -m ruff check .`: **PASS**
- `python -m pytest -q tests/backtest/test_backtest_engine.py`: **PASS** (`26 passed`)
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`: **PASS**
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`: **PASS**
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**
- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`: **STOP/no_steps** (expected), exit code `1`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`: **STOP/no_steps** (expected), exit code `1`

### Implementation Report (BT11)

- **Scope summary (IN):** Flytt av `tests/test_backtest_engine.py` till `tests/backtest/`, uppdatering av aktiv docs-referens i `docs/OPUS_46_GOVERNANCE.md`, planrad och BT11-packet.
- **Scope summary (OUT):** Inga ändringar i `src/**`, `config/**`, `scripts/**`, `mcp_server/**`, workflows eller `docs/archive/**`.
- **File-level change summary:** 1 path-only testflytt, 1 aktiv docs path update, 1 planrad, 1 command packet.
- **Gates:** pre-commit, ruff, targeted test, smoke, determinism, cache invariance, pipeline invariant: alla **PASS**.
- **Skill evidence:** `repo_clean_refactor` + `python_engineering` dry-run -> **STOP/no_steps** (förväntat policyutfall).
- **Residual risks:** Låg; begränsat till dokumenterad testpath/spårbarhet.

### PR evidence template (BT11)

- **Mode/risk/path:** `RESEARCH` / `LOW` / `Full`
- **Scope IN/OUT:** Enligt packet (Scope-sektion)
- **Selectors + outcomes:** determinism/cache/pipeline -> **PASS**
- **Smoke + lint outcomes:** pre-commit/ruff/smoke -> **PASS**
- **Artifacts:** BT11 packet + flyttdiff + OPUS path update + planuppdatering
