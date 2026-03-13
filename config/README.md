# Config-översikt

Detta är en snabb karta över vad som faktiskt används i dagens körvägar.

## Används av pipeline/backtest/optimizer

- `config/runtime.json`
  - Runtime SSOT för strategi/parametrar (läses av pipeline).
- `config/backtest_defaults.yaml`
  - Defaultvärden för backtest/pipeline (baseline för jämförbara körningar).
- `config/strategy/champions/`
  - Champion-konfigurationer per symbol/tidsram (konsumeras av pipeline).

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
