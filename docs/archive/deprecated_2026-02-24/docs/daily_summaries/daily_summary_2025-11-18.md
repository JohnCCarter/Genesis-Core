# Daily Summary 2025-11-18 – Phase-8 Reset

## Phase-8 Reset

- Kopierade hela `config/`, `data/`, `reports/`, `results/` och `cache/` till `results/_archive/Phase8_kickoff/` (underkataloger per kategori) så allt material från Phase-7 finns tillgängligt utan att ligga i vägen.
- Rensade live-katalogerna: `config/tmp` återställdes till tracked baseline, `config/runtime.json` ersattes av `runtime.seed.json`, champion-override tas bort så endast officiella champions ligger kvar.
- `data/` + `results/` + `cache/` + genererade rapporter tömdes och nyskapades tomma så nästa datadrag/modellträning börjar från ett blankt läge.
- Verifierade att pipelines (features → evaluate → decision → backtest/optimizer) fortfarande pekar mot samma sökvägar och att default runtime läses korrekt efter seed-reset.

## Next

- Hämta nya datasets (curated v1 + metadata) och kör snabb backtest för sanity innan Phase-8 optimeringen får börja.
- Planera första Phase-8 körning (vilka timeframe + symboler) och uppdatera `config/tmp/` med nya tmp-profiler, nu när mappen är ren.
