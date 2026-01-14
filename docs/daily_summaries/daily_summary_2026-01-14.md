# Daily Summary - 2026-01-14

## Summary of Work

Dagens fokus var att slutföra en **evidence-based feature/indicator audit** för `tBTCUSD_1h` som täcker hela kedjan:

- candles → indikatorer → SSOT-features → modellens schema → probas/confidence → decision → exits/backtest

Målet var att göra kedjan **reproducerbar** (ankrad i verkliga artifacts) och att lägga **guardrails** (scripts/tests) så att samma frågor går snabbare att besvara nästa gång.

## Key Changes

- **Audit-rapport (primär deliverable)**:

  - `reports/feature_audit/audit_20260114_tBTCUSD_1h.md`
  - Inkluderar dubbel-baseline (champion + Optuna trial) samt provens-ankare från `results/backtests/*.json`.

- **Runbook + mall**:

  - `docs/analysis/FEATURE_INDICATOR_AUDIT_RUNBOOK.md` (metod och beviskrav)
  - `docs/analysis/FEATURE_INDICATOR_AUDIT_PROMPT.md` (prompt/template)

- **Automation för stora backtest-artefakter**:

  - `scripts/extract_backtest_provenance.py` + `tests/test_extract_backtest_provenance.py`
  - Ger ett kompakt, report-vänligt utdrag (period/mode/provenance) utan manuell scroll.

- **Schema-kontraktstest (SSOT → schema keys)**:

  - `tests/test_feature_schema_contract_tBTCUSD_1h.py`
  - Låser att SSOT producerar alla schema-keys för `config/models/tBTCUSD_1h.json` med finita värden.

- **Bugfix: HTF-exit adapter key-normalisering**:

  - `src/core/backtest/engine.py` normaliserar HTF fib-nivåer till `htf_fib_0382/htf_fib_05/htf_fib_0618` även när context använder float-nycklar.
  - Regression: `tests/test_new_htf_exit_engine_adapter.py`.

- **Preflight hardening**:

  - `scripts/preflight_optuna_check.py` sätter nu `all_ok=False` när timeout-checken failar.
  - Regression: `tests/test_preflight_optuna_check.py`.

- **MCP remote QoL (ops)**:
  - `.env.example` dokumenterar `GENESIS_MCP_PORT` + `GENESIS_MCP_REMOTE_SAFE`.
  - `mcp_server/remote_server.py` föredrar `GENESIS_MCP_PORT`/`MCP_PORT` framför `PORT` (med robust int-parsning).

## Verification

- QA suite:

  - `black --check src tests scripts mcp_server` ✅
  - `ruff check src tests scripts mcp_server` ✅
  - `bandit -r src -ll --skip B101,B102,B110` ✅ (0 findings)
  - `pytest` ✅ (612 passed, 1 skipped)
  - `pre-commit run --all-files` ✅

- Noterat från testkörning:
  - `DeprecationWarning` i `src/core/backtest/engine.py` kring `pd.api.types.is_datetime64tz_dtype`.
  - Några förväntade sklearn/optuna warnings i tester (single-class ROC AUC, experimental sampler flags).

## Next Steps

- (Valfritt) Byt bort `pd.api.types.is_datetime64tz_dtype` enligt pandas-rekommendation (`isinstance(dtype, pd.DatetimeTZDtype)`) för att slippa framtida break.
- Om MCP/ops-ändringarna bedöms “out of scope” för audit/backtest: dela upp i separat commit/PR för enklare granskning.
- Återanvänd runbooken för fler symbol/timeframes vid behov och behåll “evidence-first” disciplinen.
