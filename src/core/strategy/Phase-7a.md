# Phase 7a – Engångsoptimering (MVP-plan)

## 1. Datasnapshot & baseline
- Frys datasetet med ett `data_snapshot_id` (tidsintervall + källfil) och logga det per försök.
- Förbered enkel feature-cache (valfritt) för återanvändning av indikatorer inom samma snapshot.
- När snapshoten är låst: verifiera att `evaluate_pipeline` kan köras fristående med valbara configs.
- **Snapshot (2025-10-20):**
  - `data_snapshot_id`: `tBTCUSD_1h_2024-10-22_2025-10-01_v1`
  - Källa: `data/curated/v1/candles/tBTCUSD_1h.parquet`
  - Period i datafil: `2024-10-22 → 2025-10-01`, warmup `150`
  - Baseline-run: `python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start 2024-10-22 --end 2025-10-01 --warmup 150`
  - Resultatfil: `results/backtests/tBTCUSD_1h_20251020_155245.json`

## 2. Sökrymder & scoring
- Beskriv parametrar i en YAML/JSON (listor eller intervall för thresholds, risk, osv.).
- Implementera scoring med primär/sekundär metric (Sharpe, MaxDD, trades) och definiera minimikrav.
- Lägg in schema-validering så ogiltiga kombinationer fångas tidigt.

## 3. Körmotor & loggning
- Bygg en “optimizer runner” som genererar parameter-set, kör backtest (mot snapshoten) och loggar varje försök.
- Spara kompletta resultat till `results/hparam_search/<timestamp>/trial_<n>.json` inklusive data-id, git-sha och tidsåtgång.
- Hoppa över försök som redan har körts (för återstartbarhet).

## 4. Robusthet & resurser
- Hantera fel (exceptions, timeouts) och fortsätt med nästa försök.
- Planera max antal samtidiga backtester, CPU/RAM-budget och logga körtid per försök.
- Upprätta rutin för att städa gamla resultatmappar vid behov.

## 5. Champion-hantering
- Jämför försök mot minimikraven och håll koll på bästa konfigurationen.
- Skriv champion till `config/strategy/champions/<symbol_tf>.json` med metadata (parametrar, metrics, data-id, git-sha) och ta backup på tidigare champion.
- Om ingen uppfyller kraven: behåll befintlig champion.

## 6. Validering & rapport
- Planera walk-forward/valideringsflöde (antal fönster, hur champion utses).
- Efter körning: generera rapport (topp 5 + metrics) och CLI-översikt (`python scripts/optimizer.py summarize --run <timestamp>`).
- Dokumentera tydligt hur man manuellt kan sätta champion vid behov.

## 7. Auto-reload (steg 2)
- Lägg till hook i live/backtestmotor för att läsa champion vid start/rollover.
- Inför schema/signaturkontroll innan auto-reload aktiveras; fallback vid ogiltig fil.

## 8. Test & dokumentation
- Unit-/integrationstester för scoring, championwriter och minst ett mini-sök.
- Dokumentera processen i `docs/optimizer.md` (sökrymder, körning, fallback, cleanup).

