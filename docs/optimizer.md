# Optimizer Runner & Rapportering (Phase-7a)

Senast uppdaterad: 2025-10-21

## 1. Översikt
Phase-7a introducerar en engångsoptimering för 1h-strategin:
- Grid-expansion av parametrar via `run_optimizer`
- Scoring/constraints för att filtrera resultat
- Champion-hantering med auto-reload (körning i pipeline/backtest)
- Rapport-CLI för snabb översikt

## 2. Arbetsflöde
1. **Datasnapshot** – lås dataset (`results/backtests/<baseline>.json`, dokumenterat i `Phase-7a.md`).
2. **Sökrymd** – definieras i `config/optimizer/<symbol_tf>_search.yaml` (grid + constraints).
3. **Runner** – `src/core/optimizer/runner.py` expanderar parametrar och startar `scripts/run_backtest.py` per trial.
4. **Scoring** – `src/core/optimizer/scoring.py` + `constraints.py` genererar score/failures.
5. **Champion** – bästa godkända trial sparas till `config/strategy/champions/<symbol_tf>.json` (backup skapas).
6. **Auto-reload** – `ChampionLoader` används av pipeline/backtest för att läsa champion vid nästa körning.
7. **Rapport** – CLI `scripts/optimizer.py summarize` summerar run och toppresultat.

## 3. Run-struktur
`results/hparam_search/<run_id>/` innehåller:
- `run_meta.json`: metadata (snapshot_id, git_commit, starttid, config-path)
- `trial_<n>.json`: score, constraints, logfil, attempts, results-path
- `trial_<n>.log`: stdout/stderr från run_backtest

## 4. Champion-hantering
`ChampionManager` skriver championfil + backup. Auto-reload via `ChampionLoader`:
- `load(symbol, timeframe)` – läser championfil eller faller tillbaka till baseline (`config/timeframe_configs.py`).
- `load_cached` – återanvänder senaste config men läser om vid mtime-förändring eller fil borttagen.
- Pipeline/backtest injicerar `meta["champion"]["source"]` så att run-loggar visar använd källa.

## 5. CLI – `scripts/optimizer.py`
### 5.1 Kommandon
- `python scripts/optimizer.py summarize <run_id>`
  - Läser `run_meta.json` + `trial_*.json`
  - Skriver totals, `skipped`, `failed`, `valid`
  - Visar bästa trial + topp N (flagga `--top`)

### 5.2 Exempel
```bash
python scripts/optimizer.py summarize run_20251021_101500 --top 5
```

### 5.3 Felhantering
- `FileNotFoundError` om run-id saknas
- Ogiltiga JSON-filer ignoreras (loggas ej)

## 6. Tester
- `tests/test_optimizer_runner.py` – mini-runner med mocked trials & championwriter
- `tests/test_optimizer_cli.py` – CLI sammanfattar metadata/top trial
- `tests/test_champion_loader.py` – fallback & auto-reload (mtime)
- `tests/test_evaluate_pipeline.py` – championmetadata injiceras i meta
- `tests/conftest.py` – gemensamma fixtures

## 7. Dokumentation & status
- `README.agents.md` – uppdaterat fokus/next steps för Phase-7a
- `src/core/strategy/Phase-7a.md` – steg 1-7 markerade klara, steg 8 dokumenterar tests & docs

## 8. Nästa steg (valfria förbättringar)
- Walk-forward / valideringsrapport (Plan steg 6)
- Utökat CLI (percentiler, export till JSON)
- Live-server auto-reload (schemalagd refresh) om önskas
