# Repo Cleanup D5 Out-of-Band Execution Guide (2026-02-14)

## Syfte

Definiera en operativ rutin för cleanup av `results/**` utanför git-spårning, så länge ignore-policy lämnas oförändrad.

## Scope för D5 i denna commit

- Docs-only vägledning.
- Ingen ändring i `.gitignore`.
- Ingen git-spårad move/delete i `results/**`.

## Förutsättningar

- Trackability-blocker är dokumenterad i D4A.
- Policyalternativ är dokumenterade i D4B.
- `results/**` är ospårbart under nuvarande ignore-policy (`.gitignore:212` med `results/`).

## OOB-rutin (föreslagen)

1. **Inventera kandidater lokalt**
   - Lista kandidater per subträd (`hparam_search`, `backtests`, `trades`, m.fl.).
   - Klassificera varje kandidat: behåll / flytta / radera.

2. **Skapa lokal audit-logg**
   - Skriv en tidsstämplad rapport i `docs/ops/` med:
     - kandidat
     - åtgärd
     - storlek
     - motivering
     - utförare

3. **Kör icke-destruktiv dry-run först**
   - Verifiera paths och volym innan faktisk åtgärd.

4. **Utför lokal cleanup**
   - Flytta/radera enligt beslutad retention-policy.
   - Ingen förväntan om git-diff för artefakter under `results/**`.

5. **Post-check**
   - Uppdatera lokal audit-logg med utfall.
   - Dokumentera eventuella avvikelser.

## Risker

- Ingen commit-nivåspårbarhet för själva artefaktförändringen.
- Risk för lokal drift om loggning inte hålls konsekvent.

## Required gates (BEFORE + AFTER)

Körda enligt repo-policy:

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

Gate-status:

- Before-gates: pass
- After-gates: pass

## Guardrails

- Ingen påverkan på runtime/API/config.
- Ingen policyändring utan separat kontrakt och explicit godkännande.
- Dokumentera alltid vad som gjordes och varför.

## Status

- D5 i denna tranche är införd som docs-only operativ vägledning.
- Faktisk `results/**` execution är fortsatt föreslagen och sker out-of-band under nuvarande policy.
