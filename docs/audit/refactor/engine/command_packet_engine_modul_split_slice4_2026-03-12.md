# Command Packet — engine-modul-split Slice 4

Datum: 2026-03-12
Branch: worktree-engine-modul-split
Base SHA: 890e8588 (slice 3 commit)
Mode: RESEARCH (source=branch:feature/engine-modul-split)
Risk: HIGH (touches `src/core/backtest/*`)
Required Path: Full (high-sensitivity)

---

## Objective

Fortsätta engine-modul-split med minsta säkra no-behavior-change extraktion:
flytta precompute-blocket i `BacktestEngine.load_data()` till dedikerad modul
`src/core/backtest/engine_precompute.py` och behålla identisk runtime-semantik.

## Scope IN

- `src/core/backtest/engine.py`
- `src/core/backtest/engine_precompute.py` (ny)
- `docs/audit/refactor/engine/command_packet_engine_modul_split_slice4_2026-03-12.md`

## Scope OUT

- Inga ändringar i `run()` eller order/exit-semantik
- Inga ändringar i `_check_htf_exit_conditions`
- Inga ändringar i `composable_engine.py`, `pipeline.py`, config-authority eller freeze-zoner
- Ingen ändring av publikt API/kontrakt

## Done-kriterier

- Precompute-logiken i `load_data()` delegeras till ny hjälparfunktion med samma resultat
- `self._precomputed_features` och HTF-precompute-mappning beter sig identiskt
- Alla befintliga cache-nycklar, filnamn och defaults bevaras
- Governance-gates körda och dokumenterade med PASS

## Föreslagna gates

- `python -m black --check src/core/backtest/engine.py src/core/backtest/engine_precompute.py`
- `python -m ruff check src/core/backtest/engine.py src/core/backtest/engine_precompute.py`
- `python -m pytest tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `python -m pytest tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- `python -m pytest tests/backtest/test_backtest_engine.py tests/integration/test_new_htf_exit_engine_adapter.py`

## Stop Conditions

- Scope drift utanför Scope IN
- Cache-key/precompute-drift eller ändrade on-disk cache-paths
- Beteendedrift i `self._precomputed_features` innehåll/shape
- Ny importcykel mellan `engine.py` och precompute-modul

## Pre-review (Opus46)

Utfall: **APPROVED_WITH_NOTES**

Obligatoriska noter inlåsta i kontraktet:

1. Parity-selectors måste köras (runtime vs precomputed)
2. Ingen runtime-import av `BacktestEngine` i `engine_precompute.py`
3. Bevara exakt ordning för toggles, cache-key, try/except och loggning

## Gate-resultat

| Gate | Resultat |
|---|---|
| black (`engine.py`, `engine_precompute.py`) | PASS |
| ruff (`engine.py`, `engine_precompute.py`) | PASS |
| import smoke | PASS |
| determinism replay smoke | PASS |
| feature cache invariance | PASS |
| pipeline invariant selector | PASS |
| parity: runtime vs precomputed | PASS |
| parity: precompute vs runtime integration | PASS |
| focused engine + HTF adapter tests | PASS |

## Post-audit (Opus46)

Utfall: **APPROVED_WITH_NOTES**

- READY_TO_COMMIT: **YES**
- Notering (icke-blockerande): behåll gate-evidens i auditpacket för spårbarhet
