# Optuna Dokumentation

Denna mapp innehåller all Optuna-relaterad dokumentation för Genesis-Core.

## Översikt

Dokumentationen täcker Optuna-integration, optimeringsworkflow, problemlösning och best practices.

## Dokument

### Genombrott och Problemlösning

- **BREAKTHROUGH_CONFIG_20251113.md** - Identifierad signal_adaptation ATR-zon flaskhals
  - Systematisk isoleringstestning
  - Genombrott-konfiguration (176 trades, PF 1.32, +8.41%)
  - Nyckelinsikter om signal_adaptation som primär entry-kontroll

- **OPTUNA_FIX_20251113.md** - Optuna-problem och lösning
  - Upptäckt att signal_adaptation var fixerat till för höga trösklar
  - Uppdaterad Optuna-spec med grid-varianter
  - Bugfix i engine.py för exit-konfigladdning

- **OPTUNA_FIX_SUMMARY.md** - Sammanfattning av Optuna-fixar

- **OPTUNA_6MONTH_PROBLEM_REPORT.md** - Problemrapport från 6-månaders körning

### Konfiguration och Best Practices

- **OPTUNA_BEST_PRACTICES.md** - Best practices för Optuna-körningar

- **OPTUNA_HARDENING_SPEC.md** - Hardening-spec (penalties, two-phase objective, pruning, trace-krav)

- **docs/daily_summaries/daily_summary_2025-12-18.md** - Explore→Validate (tvåstegsflöde) + promotion-säkerhet + resultat
  - Konfig: `config/optimizer/tBTCUSD_1h_optuna_phase3_fine_v7_smoke_explore_validate.yaml`
  - Runs: `results/hparam_search/run_20251218_ev_30t_nopromo`, `results/hparam_search/run_20251218_ev_60t_top5_nopromo`

- **OPTUNA_VS_BACKTEST_CONFIG_DIFFERENCE.md** - Skillnader mellan backtest och Optuna
  - Strukturskillnader i config-filer
  - Parameterflöde och transformationer
  - Checklista innan Optuna-körning

### Testing och Validering

- **PARITY_TEST_RESULTS_20251114.md** - Parity-test mellan backtest och Optuna
  - Verifiering av 100% paritet
  - Resultat: 99%+ paritet (små skillnader p.g.a. numeriska avrundningar)
  - Score-beräkningar och jämförelser

- **SCORE_AND_METRICS_ENHANCEMENT_20251114.md** - Score och metrics enhancement
  - Score i backtest-resultat
  - Metrics i Optuna-output
  - Konsistens mellan backtest och Optuna

### Performance

- **optuna_performance_improvements.md** - Performance-förbättringar

## Snabbstart

För att komma igång med Optuna-optimering, se:

1. **AGENTS.md** (i repo-roten) - Snabbguide och workflow
2. **docs/daily_summaries/daily_summary_2025-12-18.md** - Referens för Explore→Validate-flödet (smoke-säkert)
3. **OPTUNA_BEST_PRACTICES.md** - Best practices
4. **OPTUNA_VS_BACKTEST_CONFIG_DIFFERENCE.md** - Förstå skillnader

## Snabbstart (praktiskt)

Detta är ett minimalt flöde för en säker “smoke” innan längre körningar.

1. Preflight + validering (måste vara grönt innan lång körning):

- `python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml`
- `python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml`

2. Kör i canonical mode (1/1) och sätt rimliga guardrails:

PowerShell (Windows):

```powershell
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
$Env:GENESIS_MAX_CONCURRENT='2'
$Env:GENESIS_RANDOM_SEED='42'
$Env:GENESIS_FAST_HASH='0'
$Env:OPTUNA_MAX_DUPLICATE_STREAK='200'

python -m core.optimizer.runner config/optimizer/<config>.yaml
```

Not:

- Canonical mode (1/1) är SSOT för Optuna/Validate/champion-beslut.
- För canonical jämförbarhet: håll `GENESIS_FAST_HASH=0` (FAST_HASH är en debug/perf-knapp som kan ändra utfall).
- Om du behöver debugga 0/0, gör det explicit och jämför inte resultaten med Optuna.

### Resume-säkerhet (Optuna)

Runnern sätter en Optuna `user_attr` med nyckeln `genesis_resume_signature` på studien.
Den används för att **fail-fast** om du råkar försöka återuppta fel studie/DB eller om config/kod/runtime/mode-flaggor drivit.

- Om signaturen skiljer sig: körningen stoppar med "Optuna resume blocked: study signature mismatch".
- Det är OK att förlänga en lång körning genom att ändra stop-policy (`meta.runs.optuna.end_at` / `timeout_seconds`).
  Dessa fält ingår inte i signaturen.
- Legacy-studier kan sakna signature: då varnar runnern. Om du är säker på att du har rätt study/DB/config kan du backfilla med
  `GENESIS_BACKFILL_STUDY_SIGNATURE=1` (engångsåtgärd).
- Om du medvetet vill ignorera mismatch (ej rekommenderat för canonical beslut): sätt `GENESIS_ALLOW_STUDY_RESUME_MISMATCH=1`.

## Ops-notis: AI-assistans via remote MCP

Om du använder ChatGPT “Connect to MCP” för att assistera Optuna-arbete:

- Använd `POST /mcp` (application/json) som primär endpoint (inte `/sse`).
  - I vissa tunnel/proxy-setups kan `GET /sse` returnera `200 text/event-stream` men ändå buffra body så att inga bytes når klienten.
- Håll `GENESIS_MCP_REMOTE_SAFE=1` (read-only) som default när endpointen exponeras utanför localhost.
  Aktivera write/exec endast i kontrollerad miljö.

## Viktiga Insikter

### Signal Adaptation är Primär Entry-Kontroll

- När `signal_adaptation.zones` finns definierade används **endast dessa**, inte top-level trösklar
- Se `BREAKTHROUGH_CONFIG_20251113.md` för detaljer

### Parity mellan Backtest och Optuna

- 99%+ paritet när samma parametrar används
- Små skillnader (<5%) kan förklaras av numeriska avrundningar
- Se `PARITY_TEST_RESULTS_20251114.md` för detaljer

### Score-beräkning

- Score = sharpe + total_return + (return_to_dd \* 0.25) + clip(win_rate - 0.4, -0.2, 0.2)
- Championens score=260.73 är artificiellt hög p.g.a. max_drawdown=0.0
- Se `PARITY_TEST_RESULTS_20251114.md` för score-analys

## Checklista innan Optuna-körning

Se `OPTUNA_VS_BACKTEST_CONFIG_DIFFERENCE.md` för fullständig checklista. Kortfattat:

- [ ] Champion-parametrar i sökrymden?
- [ ] Smoke-test med champions exakta parametrar
- [ ] Preflight-validering (`validate_optimizer_config.py`)
- [ ] Verifiera att signal_adaptation.zones styr (inte top-level trösklar)
- [ ] **Config-equivalence proof**: kör `scripts/check_trial_config_equivalence.py --run-dir results/hparam_search/<run_id> --all` och kräv `[OK]`

### OOS/validation: spårbarhet för _effective config_

- Backtest artifacts innehåller `backtest_info.effective_config_fingerprint`.
  - Om två runs har samma fingerprint har de (per definition) kört samma _effective config_.
  - Om fingerprints skiljer sig men outcome är identiskt är parametern ofta inert (inte aktivt styrande).
- Optimerings-/valideringskörningar kan isoleras från implicit champion-merge via `meta.skip_champion_merge`.

## Relaterade Filer

- `config/optimizer/` - Optuna-konfigurationer
- `config/optimizer/config_equivalence_smoke.yaml` - Minimal smoke-config för drift-check proof
- `scripts/preflight_optuna_check.py` - Preflight-validering
- `scripts/validate_optimizer_config.py` - Champion-validering
- `scripts/check_trial_config_equivalence.py` - Drift-check (trial-config vs backtest-resultat)
- `src/core/optimizer/` - Optuna-integration kod
