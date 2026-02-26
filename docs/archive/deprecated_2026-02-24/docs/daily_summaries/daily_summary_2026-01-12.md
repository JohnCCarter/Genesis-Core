# Daily Summary - 2026-01-12

## Summary of Work

Dagens fokus var att återbygga förtroende för OOS-validering när olika trial-configs verkade ge identiska outcomes.

Kärnan var att skilja på två fall:

1. **Config override/drift (bugg)**: trial-configen appliceras inte som förväntat (t.ex. tyst champion-merge eller cache-artefakter).
2. **Inert parameter (förväntat)**: configen _är_ olika (och auditbart olika), men parametern påverkar inte beslut/trades i praktiken.

## Key Changes

- **Audit fingerprint i backtest artifacts**:

  - Backtest-resultat inkluderar `backtest_info.effective_config_fingerprint`.
  - Detta gör det möjligt att avgöra om två runs faktiskt körde olika _effective config_.

- **Config authority / isolering från champion**:

  - Optimerings-/valideringskörningar kan isoleras från implicit champion-merge via `meta.skip_champion_merge`.
  - Detta minskar risken att en trial "ser" champion i smyg och därmed blir identisk med andra trials.

- **Tolkning: olika fingerprint men identiskt outcome**:

  - Verifierat att man kan få olika fingerprint men identiska trades/metrics när parametern inte är aktivt styrande.
  - Exempel: i `decision.py` används regim-tröskeln från `regime_proba` om den är en dict; då kan zonens `entry_conf_overall` (som bara sätter default) bli irrelevant.

## Runs / Artifacts

- **Mini OOS-smoke (för att bevisa fingerprint + outcome-diff)**:

  - `results/hparam_search/run_20260112_oos_fingerprint_smoke2`
  - Visade tydlig divergens i trades/metrics när vi varierade en parameter som faktiskt påverkar tröskeln.

- **Re-validation subset av långkörning (2025-fönster)**:

  - Källa: `results/hparam_search/run_20260109_154651/validation/trial_001..005.json`
  - Re-run: `results/hparam_search/run_20260112_reval_longrun2025_fingerprint`
  - Samtliga outputs innehåller `backtest_info.effective_config_fingerprint`.

## Verification

- QA suite:

  - `black` ✅
  - `ruff` ✅
  - `bandit -r src` ✅
  - `pytest` ✅
  - `pre-commit run --all-files` ✅

## Next Steps

- Om identiska outcomes dyker upp igen: jämför alltid först fingerprints.
- När fingerprints skiljer sig: fokusera på att identifiera om parametern verkligen är aktiv (dvs påverkar beslut/gates/exits), annars riskerar Optuna att "optimera" brus.
