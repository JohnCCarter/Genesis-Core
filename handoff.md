# Handoff — Cleanup Core Audit (Shard C)

## Snapshot

- **Datum:** 2026-03-06
- **Branch:** `feature/cleanup-core-audit`
- **HEAD:** `a664ed7d`
- **Mode:** RESEARCH (`feature/*`)
- **Repo state vid överlämning:** ren working tree (inga staged/unstaged ändringar)

## Vad som nyligen levererats

Senaste commits (nyast först):

1. `a664ed7d` — `refactor(cleanup): inline git status path filtering`
2. `3992a117` — `refactor(cleanup): inline preflight print helper in main`
3. `0c9122aa` — `refactor: inline git owner anomaly helper`
4. `1e7187c7` — `refactor: inline proc environ reader helper`
5. `930aff2e` — `refactor: inline git repo state helper`
6. `7b16435b` — `refactor: inline git environment helper`
7. `59978886` — `refactor: inline task branch normalization helper`

Alla batches kördes med:

- Opus pre-code review
- pre-gates
- minimal diff (no behavior change)
- post-gates
- Opus post-diff review
- commit/push

## Viktiga verifierade facts för nästa agent

1. **Skill-invocation i detta cleanup-spår**
   - `repo_clean_refactor` och `python_engineering` ger `STOP: no executable steps` (förväntat SPEC-beteende).
   - Ska ändå dokumenteras som evidens i command packet.

2. **Korrekt smoke-selector för preflight-filen**
   - `tests/test_mcp_session_preflight.py` finns inte.
   - Använd istället `tests/test_mcp_server.py` med filter för `mcp_session_preflight` när relevant.

3. **Återkommande hygien-fallgrop**
   - `scripts/build/__pycache__/...pyc` dyker upp återkommande efter test/lint-körningar.
   - Rensa innan post-audit/commit för att undvika scope-drift.

## Kvarvarande arbete (praktiskt)

### A) Snäv wrapper-cleanup i aktivt spår

Kvarvarande privata helper-kandidater i `mcp_server/tools.py`:

- `_is_within` (nested i `get_project_structure`) — **lägst risk** för nästa batch
- `_run_git_command`
- `_run_git_command_async`
- `_build_compare_url` _(obs: har direkt internhelper-test i `tests/test_mcp_git_workflow_tools.py`)_

Rekommenderad nästa batch: `_is_within`.

### B) Bredare shard-C cleanup (verktygsfynd)

- Senaste JSCPD-report visar **6 klonfynd / 100 duplicerade rader** (~0.58%).
- Vulture gav **0 rader** i senaste mätningen.
- Radon visar många komplexitetsfynd, men dessa är inte per automatik no-behavior-change-kandidater.

## Standard-gates som använts i cleanup-batcher

Minst detta set (anpassa målfil + relevanta tests):

1. `black --check <target_file>`
2. `ruff check <target_file>`
3. `bandit -q -c bandit.yaml <target_file>`
4. Relevanta måltester (t.ex. `tests/test_mcp_git_status_remote_filters.py`, `tests/test_mcp_server.py`)
5. `tests/backtest/test_backtest_determinism_smoke.py`
6. `tests/test_feature_cache.py`
7. `tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

## Arbetsmönster som ska fortsätta (governance)

1. Lås command packet (mode/risk/path/scope/base SHA)
2. Kör skill-evidens (STOP/no_steps är OK för SPEC-skills)
3. Opus pre-code verdict
4. Pre-gates
5. Minimal diff (1 kandidat per batch)
6. Post-gates
7. Opus post-diff verdict
8. Commit/push

## Förslag på omedelbar start för nästa agent

1. Välj kandidat: `_is_within` i `mcp_server/tools.py`.
2. Lås Batch 22 command packet (LOW risk, no behavior change, scope IN = endast `mcp_server/tools.py`).
3. Kör ovan gate-stack före/efter.
4. Säkerställ att inga `__pycache__`-artefakter följer med in i commit.
