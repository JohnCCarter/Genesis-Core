# Backtest verification (deterministic v1)

## Skill-ID

`genesis_backtest_verify`

## Syfte

Vertical slice v1: validates registry + compares backtest artifacts deterministically. Intended to be runnable via scripts/run_skill.py.

## Metadata

- Version: 1.0.0
- Status: stable
- Locked: true
- Owners: fa06662
- Tags: backtest, verification, determinism

## Steg

- validate_registry (type: registry_validate)
- compare (type: compare_backtest_results)
  - baseline_path: registry/fixtures/backtest_sample.json
  - candidate_path: registry/fixtures/backtest_sample.json

## Regler

### Måste

- Kör deterministiskt (ingen slump).
- Inga hemligheter i loggar eller artifacts.

### Får inte

- Skapa eller modifiera trading artifacts utan explicit flagga.
