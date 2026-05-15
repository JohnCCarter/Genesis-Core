# Config-översikt

Detta är en snabb karta över vad som faktiskt används i dagens körvägar.

## Används av pipeline/backtest/optimizer

- `config/runtime.json`
  - Runtime SSOT för strategi/parametrar (läses av pipeline).
- `config/backtest_defaults.yaml`
  - Defaultvärden för backtest/pipeline (baseline för jämförbara körningar).
- `config/strategy/champions/`
  - Champion-konfigurationer per symbol/tidsram (konsumeras av pipeline).

## Runtime live-update boundary

- `config/runtime.json` är runtime-SSOT på disk.
- `POST /config/runtime/validate` validerar payload mot `RuntimeConfig`, men avgör **inte** om fältet får skrivas live via config-API:t.
- `POST /config/runtime/propose` är den guardade live-write-pathen och accepterar bara allowlistade patchytor; schema-valida men live-blockade patchar returnerar det grova publika felet `non_whitelisted_field` i stället för intern fältdetalj.
- Nuvarande live-skrivbara toppytor är `strategy_family`, `thresholds`, `gates`, `risk` (endast `risk_map`), `ev` (endast `R_default`) och utvalda `multi_timeframe`-underytor.
- Ytor som `exit`, `warmup_bars`, `features`, `htf_exit_config`, `htf_fib` och `ltf_fib` är deklarerade i runtime-schemat men är för närvarande **inte** live-skrivbara via propose-pathen.
- För exakt current-state-matris, se `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`.

## Används av scripts/verktyg (inte trading-pipeline)

- `config/champion_weights.json`
  - Viktprofiler för champion/model-selection.
  - OBS: Ingen verifierad aktiv konsument finns i nuvarande branch, så filen behandlas som behållen referens/legacy tills separat retirement-beslut finns.

- `config/validation_config.json`
  - Validerings- och urvalströsklar för modell/feature-arbete.
  - OBS: Ingen verifierad aktiv runtime-konsument finns i nuvarande branch, så filen behandlas som behållen referens/legacy tills separat retirement-beslut finns.

## Legacy / superseded (behålls för historik)

- `config/strategy/defaults.json`
  - Legacy defaults som inte läses av dagens pipeline-kod (primärt refererad i äldre/superseded docs).
  - OBS: Justera inte denna fil med förväntan att det påverkar körresultat.
