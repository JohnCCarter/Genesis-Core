# Daily Summary - 2026-01-22

## Summary of Work

Dagens fokus var att städa upp **legacy-imports i aktiva scripts** så att de följer repo-ts src-layout:

- Lägg `<repo>/src` på `sys.path`
- Importera via `core.*` (inte `src.core.*`)

Detta minskar “works on my machine”-risk och gör scripts mer portabla mellan körsätt (VS Code, terminal, CI).

## Key Changes

- **Scripts: normaliserade imports från `src.core.*` → `core.*` (exkluderar archive)**
  - Berörda filer (aktiva):
    - `scripts/analyze_regime_performance.py`
    - `scripts/generate_meta_labels.py`
    - `scripts/evaluate_model.py`
    - `scripts/select_champion.py`
    - `scripts/benchmark_numba_labeling.py`
    - `scripts/backtest_with_fees.py`
    - `scripts/tune_confidence_threshold.py`
    - `scripts/tune_triple_barrier.py`
    - `scripts/validate_purged_wfcv.py`
    - `scripts/validate_vectorized_features.py`

- **Bootstrap-fix: korrekt sys.path i ett script**
  - `scripts/optimize_ema_slope_params.py` lägger nu `<repo>/src` på `sys.path` och importerar `core.*`.

- **Guardrail-test för att förhindra regress**
  - Nytt test: `tests/test_no_src_core_imports_in_scripts.py`
  - AST-baserad kontroll som flaggar `src.core`-imports i `scripts/**`.
  - Medvetet undantag: `scripts/archive/**`, `scripts/_archive/**`, `scripts/archive_local/**` (praktiskt beslut: legacy ska inte blocka aktiv utveckling).

## Verification

- `pytest` (grönt)
- `ruff check` på berörda filer (grönt)

## Next Steps

- **Fortsatt scripts-hygien (valfritt, separat PR om det görs):**
  - Inventera `sys.path`-bootstraps i `scripts/**` och standardisera där det är värt det (många filer har historiska varianter).
  - Håll `scripts/archive/**` utanför guardrails tills vi medvetet tar den portningen.

- **Nästa konkreta tekniska uppgift (separat):**
  - Utred/implementera robust timeframe-alias/fallback för `1M` vs `1mo` + regressiontest.
