# Backtest comparability (canonical 1/1)

## Skill-ID

`backtest_comparability`

## Syfte

Säkerställer jämförbarhet mellan backtester genom samma mode-flaggor, seed och fönster.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: backtest, determinism, comparability

## Regler

### Måste

- Använd GENESIS_FAST_WINDOW=1 och GENESIS_PRECOMPUTE_FEATURES=1 för quality decisions.
- Sätt GENESIS_RANDOM_SEED=42 (eller dokumentera avvikelse).
- Jämför endast runs med samma tidsfönster och symbol/timeframe.

### Får inte

- Blanda streaming vs fast mode i samma jämförelse.
- Jämför runs med olika seed utan att säga det explicit.
- Blanda olika data- eller warmup-fönster i samma slutsats.

## Referenser

- doc: docs/features/FEATURE_COMPUTATION_MODES.md
- file: scripts/run_backtest.py
