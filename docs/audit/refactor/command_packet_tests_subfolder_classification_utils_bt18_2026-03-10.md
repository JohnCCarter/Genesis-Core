# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `LOW` — why: single-candidate test relocation av utility-test utan aktiva docs-referenser.
- **Required Path:** `Full`
- **Objective:** Relocate `test_logging_redaction.py` to `tests/utils/` with no behavior change.
- **Candidate:** `tests/test_logging_redaction.py -> tests/utils/test_logging_redaction.py`
- **Base SHA:** `a395e55b`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (enbart testflytt + planrad/paket; ingen runtime/API/env/config-semantik ändras).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: single-candidate utility move, 0 non-archive docs refs for old path
- **Required Path:** `Full`
- **Objective:** Continue utils-category migration with low-friction candidate.
- **Candidate:** `test_logging_redaction.py`
- **Base SHA:** `a395e55b`

### Scope

- **Scope IN:**
  - `tests/test_logging_redaction.py` (move source)
  - `tests/utils/test_logging_redaction.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (batch progress row)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt18_2026-03-10.md`
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
- `python -m pytest -q tests/utils/test_logging_redaction.py`
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

### Skill invocation evidence

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` -> **STOP/no_steps** (expected), exit code `1`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` -> **STOP/no_steps** (expected), exit code `1`

### Branch/mode evidence (pre-coding)

- `git status -sb` -> `## feature/tests-subfolder-classification...`

### Pre-coding verification evidence

- Branch/mode verified via `git status -sb` on `feature/tests-subfolder-classification`.
- Path-reference check i `docs/**` gav inga träffar utanför denna packet-fil; inga ytterligare icke-arkiv-referenser kräver uppdatering i BT18.
- `rg -n "tests/test_logging_redaction.py" docs --glob "!docs/archive/**" --glob "!docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt18_2026-03-10.md"` -> inga träffar (exit code `1`, expected for no matches).

### Review + verification evidence

- Opus pre-code review: **APPROVED**
- `python -m pre_commit run --all-files`: **PASS**
- `python -m ruff check .`: **PASS**
- `python -m pytest -q tests/utils/test_logging_redaction.py`: **PASS** (`3 passed`)
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`: **PASS**
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`: **PASS**
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**

### Implementation Report (BT18)

- **Scope summary (IN):** Flytt av `tests/test_logging_redaction.py` till `tests/utils/`, planuppdatering och BT18-packet.
- **Scope summary (OUT):** Inga ändringar i `src/**`, `config/**`, `scripts/**`, `mcp_server/**`, workflows eller övriga docs.
- **File-level change summary:** 1 path-only testflytt, 1 planrad, 1 command packet.
- **Gates:** pre-commit, ruff, targeted test, smoke, determinism, cache invariance, pipeline invariant: alla **PASS**.
- **Skill evidence:** `repo_clean_refactor` + `python_engineering` dry-run -> **STOP/no_steps** (förväntat policyutfall).
- **Residual risks:** Låg; begränsat till testfil-layout och spårbarhet.

### PR evidence template (BT18)

- **Mode/risk/path:** `RESEARCH` / `LOW` / `Full`
- **Scope IN/OUT:** Enligt packet (Scope-sektion)
- **Selectors + outcomes:** determinism/cache/pipeline -> **PASS**
- **Smoke + lint outcomes:** pre-commit/ruff/smoke -> **PASS**
- **Artifacts:** BT18 packet + flyttdiff + planuppdatering
