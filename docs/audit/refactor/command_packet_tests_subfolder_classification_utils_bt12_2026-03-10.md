# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `LOW` — why: path-only relocation av en utility-test utan aktiva docs-referenser.
- **Required Path:** `Full`
- **Objective:** Relocate `test_backoff_util.py` to `tests/utils/` with no behavior change.
- **Candidate:** `tests/test_backoff_util.py -> tests/utils/test_backoff_util.py`
- **Base SHA:** `fd3a8ba5`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (enbart filflytt + planrad/paket; ingen runtime/API/env/config-semantik ändras).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: single-candidate move, 0 non-archive docs refs for old path
- **Required Path:** `Full`
- **Objective:** Start utils-category migration with lowest-friction candidate.
- **Candidate:** `test_backoff_util.py`
- **Base SHA:** `fd3a8ba5`

### Scope

- **Scope IN:**
  - `tests/test_backoff_util.py` (move source)
  - `tests/utils/test_backoff_util.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (batch progress row)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt12_2026-03-10.md`
- **Scope OUT:**
  - `src/**`, `mcp_server/**`, `scripts/**`, `config/**`
  - `.github/workflows/**`
  - All docs outside plan/paket-filen ovan
  - Any additional test-file moves
  - Generated metadata/cache paths (`.pytest_cache/**`, `**/*.egg-info/**`)
- **Expected changed files:** 3-4
- **Max files touched:** 4

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/utils/test_backoff_util.py`
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

### Pre-coding verification evidence

- Branch/mode verified via `git status -sb` on `feature/tests-subfolder-classification`.
- Path-reference check (`grep docs/**/*.md`): `tests/test_backoff_util.py` matches only this BT12 packet (0 non-archive docs refs outside packet).

### Review + verification evidence

- Opus pre-code review: **APPROVED_WITH_NOTES** -> fixes applied -> **APPROVED/GO**
- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`: **STOP/no_steps** (expected), exit code `1`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`: **STOP/no_steps** (expected), exit code `1`
- `python -m pre_commit run --all-files`: **PASS**
- `python -m ruff check .`: **PASS**
- `python -m pytest -q tests/utils/test_backoff_util.py`: **PASS**
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`: **PASS**
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`: **PASS**
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**
- Raw command outputs are available in this workspace terminal session (BT12 execution block).

### Implementation Report (BT12)

- **Scope summary (IN):** Flytt av `tests/test_backoff_util.py` till `tests/utils/`, planuppdatering och BT12-packet.
- **Scope summary (OUT):** Inga ändringar i `src/**`, `config/**`, `scripts/**`, `mcp_server/**`, workflows eller övriga docs.
- **File-level change summary:** 1 path-only testflytt, 1 planrad, 1 command packet.
- **Gates:** pre-commit, ruff, targeted test, smoke, determinism, cache invariance, pipeline invariant: alla **PASS**.
- **Skill evidence:** `repo_clean_refactor` + `python_engineering` dry-run -> **STOP/no_steps** (förväntat policyutfall).
- **Residual risks:** Låg; begränsat till testfil-layout och spårbarhet.

### PR evidence template (BT12)

- **Mode/risk/path:** `RESEARCH` / `LOW` / `Full`
- **Scope IN/OUT:** Enligt packet (Scope-sektion)
- **Selectors + outcomes:** determinism/cache/pipeline -> **PASS**
- **Smoke + lint outcomes:** pre-commit/ruff/smoke -> **PASS**
- **Artifacts:** BT12 packet + flyttdiff + planuppdatering
