# Daily Summary - 2026-02-11

## Sammanfattning

Fokus idag: **dokumentera Phase 3 paper trading + Azure/remote-spåret** och hårdna runnern mot en tyst men farlig felklass (fel candle-window ordering).

Målet var att få bort "kunskap i chatten" och istället göra det reproducerbart i repo:t: runbooks/deployment-guides pekar nu till rätt daily summaries, och runnern har regressiontest så ordering-buggen inte kan komma tillbaka obemärkt.

## Viktiga ändringar

### Paper trading runner: korrekt candle-window ordering + guardrail

- `scripts/paper_trading_runner.py`
  - Fetchar candles window som _newest-first_ (`sort=-1`) och vänder tillbaka till kronologisk ordning (oldest → newest).
  - Defensiv startup-guard: reset av persisted `pipeline_state` vid extrem `last_close`-mismatch (för att undvika inkompatibelt state efter tidigare bug/format).

- `tests/test_paper_trading_runner_candles_window_ordering.py`
  - Regressiontest: verifierar att request använder `sort=-1` och att output-arrayer är kronologiska.
  - Test för helper som resetar `pipeline_state` vid stor mismatch.

### Docs: Azure/remote arbete indexerat från rätt ställen

- `docs/paper_trading/phase3_runbook.md` och `docs/paper_trading/runner_deployment.md`
  - Pekar explicit till Azure/remote status + relevanta daily summaries.

- `docs/paper_trading/server_setup.md`
  - Systemd-exempel justerat för Linux/Azure VM (native paths + Linux-venv).

- `docs/paper_trading/operations_summary.md` + `docs/paper_trading/README.md`
  - Samlar "Remote deployment"-status och korslänkar så operativ kontext är lätt att hitta.

- `docs/paper_trading/daily_summaries/day3_summary_2026-02-11.md`
  - Dokumenterar identity/subscription blocker, VS Code filter-fällan och VM generalization-incident + recovery-path.

### Repo-hygien

- `.gitignore`: ignorerar nu `*.msi` (minskar risk att lokala installers råkar committas).

## Verifiering

- Riktat pytest för nya regressioner (i `.venv`): ✅
- Ruff på ändrade filer: ✅
- Black `--check` på ändrade filer: ✅

## Kvarvarande blockerare / nästa steg

- **Ops (Azure VM):** Remote runner är igång med systemd och **preflight PASS**. Nästa steg är att efter ~24h granska
  `logs/paper_trading/acceptance_check_<UTC_TS>.txt` och verifiera att `dry_run_acceptance.sh` ger PASS.
- **Azure:** subscription visibility var en blockerare tidigare; om den dyker upp igen (t.ex. för recovery/provisioning), verifiera tenant/identity och rensa VS Code subscription-filter.
