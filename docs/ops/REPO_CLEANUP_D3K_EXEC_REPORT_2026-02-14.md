# Repo Cleanup D3K Execution Report (2026-02-14)

## Syfte

Genomföra kandidatvis flytt av ett diagnose-script med högre extern referensyta, samt hålla länkad skill-referens korrekt.

## Flyttat script (move-only)

1. `scripts/diagnose_zero_trades.py`

Ny path:

- `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py`

## Scopead linked-reference update

Fil: `.github/skills/decision_gate_debug.json`

Genomförda ändringar (exakt 2 path-strängar):

1. Rule-text: `scripts/diagnose_zero_trades.py` → `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py`
2. `references[].value`: `scripts/diagnose_zero_trades.py` → `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py`

## Känd docs-referenspåverkan

Följande docs nämner tidigare script-path eller scriptnamn och uppdateras inte i D3K:

- `docs/bugs/FELSÖKNING_HANDOFF_2025-11-20.md`
- `docs/analysis/INVESTIGATION_COMPLETE.md`
- `docs/archive/phase6/ORIGINAL_REPO_MENTIONS.md`
- `docs/archive/phase6/DOCUMENTATION_ANALYSIS.md`

## Required gates (BEFORE + AFTER)

Körda enligt kontrakt:

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Verifiering

- Scope gate: endast kontrakterade filer i diff.
- Rename-diff verifierad för flytten.
- Move-only verifierad: inga kodhunks i flyttad `.py`-fil.
- Linked-reference gate verifierad: endast två path-strängar i skill-filen ändrade.
- No-code-drift: inga ändringar i `src/**`, `tests/**`, `config/**`, `results/**`, `tmp/**`.
- Before-gates: pass.
- After-gates: pass.
- Opus post-code diff-audit: krävs som slutgate.

## Status

- D3K är införd som move-only för ett diagnose-script, med länkad scopead referensjustering i `.github/skills/decision_gate_debug.json`.
- D3 övergripande scope är fortsatt föreslaget kandidatvis.
