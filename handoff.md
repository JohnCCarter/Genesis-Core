Plan: Shadow artifact pytest (P1 OFF)
Målet är att lägga till ett minimalt, test-only shadow artifact-smoke i OFF-läge utan produktionsdrift. Vi återanvänder samma eval-path som befintliga kontraktstester i test_evaluate_pipeline.py via evaluate_pipeline i evaluate.py. Testet i ny fil tests/test_regime_shadow_artifacts.py extraherar befintliga regim-/observability-fält och beräknar en test-lokal clarity_score från confidence.overall (int clamp 0–100), validerar kvalitet, och skriver artifacts endast när REGIME_EVIDENCE_DIR är satt. Ingen ändring i core-semantik, inga nya dependencies, inga champions/config-ingrepp.

Steps

Skapa tests/test_regime_shadow_artifacts.py med testet test_regime_shadow_artifacts_smoke.
Återanvänd eval-harnessmönster från test_evaluate_pipeline.py (test_evaluate_pipeline_shadow_error_rate_contract, test_evaluate_pipeline_authority_mode_source_invariant_contract) för deterministisk monkeypatch och stabil config-normalisering.
Kör P1 OFF-mode i testet (ingen parity-assert här), samla samples från result/meta:
labels: både authoritative (result["regime"]) och shadow (meta["observability"]["shadow_regime"]["shadow"])
clarity: test-projektion från confidence till int i [0,100].
Implementera valideringar i testet:
sample_count: prefererat >=200, fallback >=50 vid begränsat underlag
alla clarity_score är heltal i [0,100]
labels finns per sample.
Implementera opt-in artifact write via REGIME_EVIDENCE_DIR:
clarity_histogram.json (10-bins: 0–9 … 90–100)
clarity_quantiles.json (p50, p80, p90, p95, top20_threshold, mean, std, total)
shadow_samples.ndjson (minst: symbol, timeframe, bar_index/timestamp, regime_label(s), clarity_score; optional components om tillgängliga).
Verifiera att .gitignore redan täcker artifacts (den gör det; ingen ändring behövs).
Kör testet i båda lägena (unset/set REGIME_EVIDENCE_DIR) och kontrollera filskapande endast i set-läget.
Verification

Unset env: kör pytest -q tests/test_regime_shadow_artifacts.py::test_regime_shadow_artifacts_smoke och verifiera pass utan filskrivning.
Set env: sätt REGIME_EVIDENCE_DIR till temp-katalog, kör samma test, verifiera att exakt tre artifacts finns och att innehållsvalidering passerar.
Kör även baseline-gates som redan används i trancherna: import smoke, determinism smoke, feature cache invariance, pipeline hash invariant.
Decisions

Clarity-källa: test-projektion (inte nytt runtimefält).
Label-källa i samples: både shadow + authoritative.
Tröskelpolicy: prefer 200, fallback 50.
Filform: exakt leverabel enligt spec (tests/test_regime_shadow_artifacts.py, test_regime_shadow_artifacts_smoke).
