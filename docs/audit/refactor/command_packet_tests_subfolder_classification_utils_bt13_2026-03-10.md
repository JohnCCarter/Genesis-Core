# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `LOW` — why: test-only relocation av en utility-test + minimal detect-secrets-remediation, utan aktiva docs-referenser.
- **Required Path:** `Full`
- **Objective:** Relocate `test_build_auth_headers.py` to `tests/utils/` med no-behavior-change och minimal secrets-hook-remediation i testfilen.
- **Candidate:** `tests/test_build_auth_headers.py -> tests/utils/test_build_auth_headers.py`
- **Base SHA:** `25d643e8`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (testflytt + minimal test-only remediation + packet; ingen runtime/API/env/config-semantik ändras).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: single-candidate test move + minimal secrets-hook remediation, 0 non-archive docs refs for old path
- **Required Path:** `Full`
- **Objective:** Continue utils-category migration with low-friction candidate.
- **Candidate:** `test_build_auth_headers.py`
- **Base SHA:** `25d643e8`

### Scope

- **Scope IN:**
  - `tests/test_build_auth_headers.py` (move source)
  - `tests/utils/test_build_auth_headers.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (batch progress row)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt13_2026-03-10.md`
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
- `python -m pytest -q tests/utils/test_build_auth_headers.py`
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
- Path-reference check (`grep docs/**/*.md`): `tests/test_build_auth_headers.py` has 0 non-archive docs references outside this BT13 packet.
- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` -> **STOP/no_steps** (expected), exit code `1`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` -> **STOP/no_steps** (expected), exit code `1`

### Review + verification evidence

- Opus pre-code review: **APPROVED_WITH_NOTES** -> fixes applied -> **APPROVED/GO**
- `python -m pre_commit run --all-files`: **PASS**
- `python -m ruff check .`: **PASS**
- `python -m pytest -q tests/utils/test_build_auth_headers.py`: **PASS** (`10 passed`)
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`: **PASS**
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`: **PASS**
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**
- Commit-hook incident: initial `detect-secrets` flagged mock literals in moved test file; remediated with non-secret-like mock constants + inline allowlist on credential assignment lines.
- Post-remediation rerun: `python -m pre_commit run --all-files`, `python -m ruff check .`, targeted test, smoke, determinism, cache invariance, pipeline invariant -> **PASS**.

### Implementation Report (BT13)

- **Scope summary (IN):** Flytt av `tests/test_build_auth_headers.py` till `tests/utils/`, planuppdatering och BT13-packet.
- **Scope summary (OUT):** Inga ändringar i `src/**`, `config/**`, `scripts/**`, `mcp_server/**`, workflows eller övriga docs.
- **File-level change summary:** 1 path-only testflytt, 1 planrad, 1 command packet.
- **Gates:** pre-commit, ruff, targeted test, smoke, determinism, cache invariance, pipeline invariant: alla **PASS** (inklusive post-remediation rerun efter detect-secrets-hook).
- **Skill evidence:** `repo_clean_refactor` + `python_engineering` dry-run -> **STOP/no_steps** (förväntat policyutfall).
- **Residual risks:** Låg; begränsat till testfil-layout och spårbarhet.

### PR evidence template (BT13)

- **Mode/risk/path:** `RESEARCH` / `LOW` / `Full`
- **Scope IN/OUT:** Enligt packet (Scope-sektion)
- **Selectors + outcomes:** determinism/cache/pipeline -> **PASS**
- **Smoke + lint outcomes:** pre-commit/ruff/smoke -> **PASS**
- **Artifacts:** BT13 packet + flyttdiff + planuppdatering
