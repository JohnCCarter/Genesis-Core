# Vectorized Cache Workflow

## Precompute

- `python scripts/precompute_features_fast.py --symbol tBTCUSD --timeframe 1h`
- Output: `data/archive/features/tBTCUSD_1h_features.feather|parquet`

## Användning i backtest

1. Flagga i config eller CLI (`--use-vectorized-cache`)
2. Vid pipeline-start:
   - Ladda Feather → DataFrame
   - Indexera på timestamp/bar
   - Passa `features_df.loc[asof_timestamp]` till decision pipeline
3. Fallback till `_extract_asof()` om cache saknar bar

## Optuna / Runner

- Ladda cache en gång per worker och återanvänd
- Rensa `_cache/` innan långa körningar (för att undvika stale/paritetfel)

## Validering

- Kör parity-checklistan före första driftsättning
- Logga tidsbesparing per trial/run

## Underhåll

- Uppdatera cachen när feature-pipelinen ändras (ny release)
- Dokumentera kördatum och commit-hash i `data/archive/features/README.md`

## Körning / CLI

- Backtest: `python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --use-vectorized`
  - med `--vectorized-cache data/features/tBTCUSD_1h_features.feather` för explicit cachefil
  - eller `--vectorized-version v17` för standardkataloger
- Skriptet aktiverar `cfg.vectorized.use_cache = True` och injicerar `path`/`version` så pipeline togglas utan kodändring.

## Optuna / grid-config

Lägg till block i optimizer-konfig (`config/optimizer/*.yaml`):

```yaml
meta:
  vectorized:
    use_cache: true
    version: v17
    # path: data/features/tBTCUSD_1h_features.feather  # valfritt
```

`core.optimizer.runner` mergar automatiskt detta med varje trial-parameter så att backtesterna körs mot cachet. Se `config/optimizer/tBTCUSD_1h_fib_grid_v2.yaml` för ett konkret exempel.
