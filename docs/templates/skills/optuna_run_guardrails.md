# Optuna guardrails (preflight + validation)

## Skill-ID

`optuna_run_guardrails`

## Syfte

Säkerställer att Optuna-körningar följer preflight och konfigvalidering innan längre runs i stabiliseringsfasen.

## Metadata

- Version: 1.0.0
- Status: dev
- Owners: fa06662
- Tags: optuna, validation, stabilization

## Regler

### Måste

- Kör scripts/preflight_optuna_check.py innan Optuna-körning.
- Kör scripts/validate_optimizer_config.py och kräv exitcode 0 före lång körning.
- Använd canonical mode (GENESIS_FAST_WINDOW=1, GENESIS_PRECOMPUTE_FEATURES=1) vid jämförelser.

### Får inte

- Starta Optuna >30 min utan preflight/validering.
- Återanvänd storage DB när resume=false.
- Jämför resultat mellan olika exekveringslägen.

## Referenser

- file: scripts/preflight_optuna_check.py
- file: scripts/validate_optimizer_config.py
- doc: docs/optuna/OPTUNA_BEST_PRACTICES.md
