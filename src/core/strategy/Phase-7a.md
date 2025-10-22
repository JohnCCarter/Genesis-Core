# Phase 7a – Engångsoptimering (MVP-plan)

## 1. Datasnapshot & baseline ✅ (2025-10-20)
- Frys datasetet med ett `data_snapshot_id` (tidsintervall + källfil) och logga det per försök.
- Förbered enkel feature-cache (valfritt) för återanvändning av indikatorer inom samma snapshot.
- När snapshoten är låst: verifiera att `evaluate_pipeline` kan köras fristående med valbara configs.
- **Snapshot (2025-10-20):**
  - `data_snapshot_id`: `tBTCUSD_1h_2024-10-22_2025-10-01_v1`
  - Källa: `data/curated/v1/candles/tBTCUSD_1h.parquet`
  - Period i datafil: `2024-10-22 → 2025-10-01`, warmup `150`
  - Baseline-run: `python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start 2024-10-22 --end 2025-10-01 --warmup 150`
  - Resultatfil: `results/backtests/tBTCUSD_1h_20251020_155245.json`

## 2. Sökrymder & scoring ✅ (klar 2025-10-20)
- Beskriv parametrar i en YAML/JSON (listor eller intervall för thresholds, risk, osv.).
- Implementera scoring med primär/sekundär metric (Sharpe, MaxDD, trades) och definiera minimikrav.
- Lägg in schema-validering så ogiltiga kombinationer fångas tidigt.
- **Artefakter:**
  - Sökrymd: `config/optimizer/tBTCUSD_1h_search.yaml`
  - Scoring: `src/core/optimizer/scoring.py`
  - Constraints: `src/core/optimizer/constraints.py`

## 3. Körmotor & loggning ✅ (klar 2025-10-20)
- Bygg en “optimizer runner” som genererar parameter-set, kör backtest (mot snapshoten) och loggar varje försök.
- Spara kompletta resultat till `results/hparam_search/<timestamp>/trial_<n>.json` inklusive data-id, git-sha och tidsåtgång.
- Hoppa över försök som redan har körts (för återstartbarhet).
- **Runner:** `src/core/optimizer/runner.py` (grid-expansion, backtest launch, scoring, logging).
- **Kvar:** resume/skip-logik, concurrency och CLI-wrapper (ingår i robusthetssteget nedan).

## 4. Robusthet & resurser ✅ (klar 2025-10-21)
- Hantera fel (exceptions, timeouts) och fortsätt med nästa försök.
- Planera max antal samtidiga backtester, CPU/RAM-budget och logga körtid per försök.
- Upprätta rutin för att städa gamla resultatmappar vid behov.
- **Implementation:**
  - `runs.max_concurrent` styr ThreadPoolExecutor (default 1).
  - `runs.max_attempts` ger retry med backoff (5s-60s) + logg i `trial_x.log`.
  - `run_meta.json` innehåller snapshot-id, git-commit, starttid, config-path.
  - `trial_x.json` fylls med `attempts`, `skipped` och `error` vid misslyckande.
- **Kvar:** CLI-wrapper för resume/skip-rapport (ingår i steg 6).

## 5. Champion-hantering ✅ (klar 2025-10-21)
- Jämför försök mot minimikraven och håll koll på bästa konfigurationen.
- Skriv champion till `config/strategy/champions/<symbol_tf>.json` med metadata (parametrar, metrics, data-id, git-sha) och ta backup på tidigare champion.
- Om ingen uppfyller kraven: behåll befintlig champion.
- **Implementation:**
  - `ChampionManager` (`src/core/optimizer/champion.py`) hanterar backup + skrivning.
  - Runner plockar bästa trial (utan hard failures) och uppdaterar champion med metadata.
  - Tester: `tests/test_optimizer_champion.py`, `tests/test_optimizer_runner.py`.
- **Kvar:** rapportering/CLI samt dokumentation (steg 6 & 8).

## 6. Validering & rapport ✅ (klar 2025-10-21)
- Planera walk-forward/valideringsflöde (antal fönster, hur champion utses).
- Efter körning: generera rapport (topp 5 + metrics) och CLI-översikt (`python scripts/optimizer.py summarize --run <id>`).
- Dokumentera tydligt hur man manuellt kan sätta champion vid behov.
- **Implementation:**
  - CLI `scripts/optimizer.py summarize` visar counts, bästa trial, top N (`--top`).
  - Tester: `tests/test_optimizer_cli.py`, `tests/test_optimizer_runner.py` (mini-run), `tests/conftest.py` fixtures.
- **Kvar:** Walk-forward validering (framtida steg).

## 7. Auto-reload ✅ (klar 2025-10-21)
- Lägg till hook i live/backtestmotor för att läsa champion vid start/rollover.
- Inför schema/signaturkontroll innan auto-reload aktiveras; fallback vid ogiltig fil.
- **Implementation:**
  - `ChampionLoader` (`src/core/strategy/champion_loader.py`) laddar champion med mtime-koll och fallback.
  - `evaluate_pipeline` och `BacktestEngine` använder loadern och injicerar `meta.champion.source`.
  - Tester: `tests/test_champion_loader.py`, `tests/test_evaluate_pipeline.py` (champion-meta), `tests/test_optimizer_runner.py` (Patchad expand_parameters).

## 8. Test & dokumentation ✅ (klar 2025-10-21)
- Unit-/integrationstester för scoring, championwriter och minst ett mini-sök.
- Dokumentera processen i `docs/optimizer.md` (sökrymder, körning, fallback, cleanup).
- **Implementation:** Full testsvit + dokumentation uppdaterad (`README.agents.md`, `docs/optimizer.md`).
