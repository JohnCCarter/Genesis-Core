# Daily Summary - 2026-01-15

## Summary of Work

Dagens fokus var att stärka repo:s "custom agents"-setup så att den är **fail-fast**, "overseer-friendly" och minimalt behörig.

Detta inkluderade tydliga authority boundaries + eskaleringsregler och att normalisera YAML-frontmatter (`tools:`) så att VS Code inte visar kvarvarande info/rename-diagnostics.

Utöver governance-lagret gjordes även Optuna-relaterade förbättringar för **jämförbarhet (“äpplen och päron”)** och en mer robust Explore-körning (konfig + guardrails).

## Key Changes

- **Custom agents (governance + guardrails)**:

  - `.github/agents/Plan.agent.md`
  - `.github/agents/AnalysisAudit.agent.md`
  - `.github/agents/GovernanceQA.agent.md`
  - `.github/agents/OpsRunner.agent.md`

  Ändringar: authority boundary, stop conditions (fail-fast), escalation-template och tool allow-lists.

- **Tool frontmatter normalization**:

  - Bytte `tools:` till block-list YAML och rensade bort ogiltiga/överflödiga entries för att undvika editor-diagnostics.

- **Noterat/klargjort**:

  - Per-subagent modellval stöds inte via agent-YAML; subagenter följer den modell/kapacitet som Copilot Chat-sessionen erbjuder.

- **Optuna: jämförbarhet + guardrails**:

  - Nya konfigar för utforskning på 2024-fönstret:
    - `config/optimizer/tBTCUSD_1h_optuna_simple_v2_explore2024_smoke10_20260115.yaml`
    - `config/optimizer/tBTCUSD_1h_optuna_simple_v2_explore2024_run50_20260115.yaml`
  - “Comparable”-skydd vid jämförelser/promotion:
    - `src/core/optimizer/runner.py`: fail-fast om `score_version` skiljer (när båda finns), warn-only vid drift i `backtest_info`.
    - `scripts/run_backtest.py`: `--compare` gör nu en jämförbarhets-check (med `--compare-warn-only` som legacy/forensics).
    - `scripts/optimizer.py`: visar `score_version` (och best-effort comparability info från sparad backtest-artefakt) i `summarize`.
  - Diff-utilities:
    - `src/core/utils/diffing/results_diff.py`: ny `check_backtest_comparability()` + formattering av issues.
  - Tester:
    - `tests/test_optimizer_runner.py`, `tests/utils/diffing/test_results_diff.py`, `tests/test_registry_validator.py`.

- **Determinism/forensics: GENESIS_FAST_HASH hardening (canonical mode)**:

  - Evidens: `GENESIS_FAST_HASH=1` kan ge stabila men **annorlunda** resultat jämfört med baseline (icke-jämförbart), trots samma seed/period.
  - Policy: behandla `GENESIS_FAST_HASH` som **debug/perf-only**.
  - Guardrails:
    - `src/core/pipeline.py`: canonical mode tvingar `GENESIS_FAST_HASH=0`.
    - `scripts/preflight_optuna_check.py`: varnar om `GENESIS_FAST_HASH=1` i canonical mode och kan faila via `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`.
    - `.env.example`: kommenterad rekommendation att hålla `GENESIS_FAST_HASH=0` för jämförbara runs.
  - Tester:
    - `tests/test_pipeline_fast_hash_guard.py`
    - `tests/test_preflight_optuna_check.py`

## Verification

- Pytest (riktade tester): ✅ (23 passed)

  - `tests/test_optimizer_runner.py`
  - `tests/utils/diffing/test_results_diff.py`
  - `tests/test_registry_validator.py`

- Pre-commit: ✅ (`pre-commit run --all-files`)

## Next Steps

- (Valfritt) Rensa/justera ev. onödiga `# nosec`-annoteringar som Bandit varnar om (för att minska brus).
