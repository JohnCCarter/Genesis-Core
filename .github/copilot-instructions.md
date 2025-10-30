<!-- Updated by Copilot-guided review 2025-10-30 -->
# Genesis-Core Copilot Guide

## Samarbetsregler
- Läs `.cursor/rules/cursor-active-rules.mdc` för baskrav (svenska svar, steg-för-steg, diff < 100 rader); `reference-guide.md` innehåller full policy och `AGENTS.md` ger senaste lägesrapporten.
- Stabiliseringsfas: varje kodrad ska lösa ett konkret problem eller höja tillförlitlighet/prestanda/läsbarhet. Lägg till tester direkt vid logikändringar.

## Arkitektur
- FastAPI startas i `src/core/server.py`; endpoints ska vara tunna och delegera till rena funktionsmoduler i `src/core/strategy/` och `src/core/io/`.
- `src/core/strategy/decision.py` och `evaluate.py` bildar kärnloopen (ATR-, regime- och Fibonacci-gating). Bevara `state_out`-strukturen; den för vidare ATR-percentiler, fib-kontekst och cooldown mellan körningar.
- Champion-konfigurationer (`config/strategy/champions/*.json`) styr trösklar. `ChampionLoader` fallbackar mot default-tidsramar om filer saknas.

## Strategipipeline
- `evaluate_pipeline` hämtar champion, läser features via `features_asof.extract_features`, kör modellprediktion, räknar confidence och kallar `decision.decide`.
- Featureberäkning använder AS-OF-semantik: live kör näst sista baren; backtest styrs via `asof_bar`. Ändra alltid fönsterlogik i `features_asof.py` kontrollerat.
- `state_out` måste fortsatt exponera Fibonacci-kontekst för både HTF och LTF samt ATR-baserade toleranser (se senaste förändringar i `htf_fibonacci.py`).

## Konfiguration & SSOT
- SSOT ligger utanför git i `config/runtime.json` och manipuleras via `ConfigAuthority` för atomiska skrivningar och audit-logg (`logs/config_audit.jsonl`).
- `/config/runtime/propose` accepterar endast whitelistaste fält (`thresholds`, `gates`, `risk.risk_map`, `ev.R_default`). Utökningar kräver schemajustering i `core/config/schema.py` och valideringstester.
- Miljöer läses i `core/config/settings.py`; tester behöver `SYMBOL_MODE=synthetic` för att tvinga TEST-symboler.

## Backtest & Optimering
- `scripts/run_backtest.py --config-file path/to.json` kör `core/backtest/engine.BacktestEngine` mot Parquet-data under `data/curated/v1/candles/`.
- Optimiseringsflöde enligt `AGENTS.md`: coarse grid → proxy Optuna → fine Optuna → ev. fib-grid. Cacha resultat i `results/hparam_search/run_*` och summera med `python scripts/optimizer.py summarize <run_id>`.
- Trial-parametrar djupmergas över aktuell SSOT; schemaändringar kräver uppdatering av `_deep_merge` och associerade tester i `tests/test_optimizer_runner.py`.

## Bitfinex-integration
- REST-klienten (`core/io/bitfinex/exchange_client.py`) signerar med `json.dumps(..., separators=(",", ":"))`; återanvänd exakt format vid nya auth-kroppar.
- Nonce-hantering lever i `core/utils/nonce_manager.py`; kalla `bump_nonce` före retry på nonce-fel. Symbolmapping måste matcha TEST-whitelist i `src/core/server.py`.

## Observability & Loggning
- Metrics finns i `core/observability/metrics.py` och exponeras via `/observability/dashboard`; bruk `metrics.event`/`metrics.inc` för nya händelser.
- Loggar ska gå via `core/utils/logging_redaction.get_logger` för att maskera hemligheter och följa säkerhetspolicyn.

## Test & QA
- Standardkörning: `pwsh -File scripts/ci.ps1` (black → ruff → bandit → pytest). För manuell bandit: `bandit -r src -ll --skip B101,B102,B110`.
- Kritiska tester: `pytest tests/test_config_api_e2e.py::test_runtime_endpoints_e2e`, `tests/test_exchange_client.py::test_build_and_request_smoke`, `tests/test_ui_endpoints.py::test_debug_auth_masked` (kräver `.env`).
- Backtest-/optimeringsändringar kan påverka snapshots i `tests/test_optimizer_*` och JSON-resultat under `results/backtests/`; uppdatera dem konsekvent.

## Mönster & Konventioner
- Håll `src/core/strategy/*` rena och deterministiska; ingen I/O, returnera metadata för observability.
- Dokumentera nya state-/meta-nycklar och handoff-insikter i `AGENTS.md` för nästa agent.
- Rör inte runtime-filer som är gitignored (`config/runtime.json`, `logs/config_audit.jsonl`) direkt; använd befintliga API:er/kommandon.
- Lagra genererade rapporter under `results/backtests/` och `results/hparam_search/` enligt etablerat mönster.
