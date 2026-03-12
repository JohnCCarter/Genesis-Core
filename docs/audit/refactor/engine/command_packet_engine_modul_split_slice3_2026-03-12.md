# Command Packet — engine-modul-split Slice 3

Datum: 2026-03-12
Branch: worktree-engine-modul-split
Base SHA: 45fef051 (slice 2 commit)
Mode: RESEARCH (source=branch:feature/engine-modul-split)
Risk: HIGH (touches `src/core/backtest/*`)
Required Path: Full (high-sensitivity)

---

## Objective

Extrahera `BacktestEngine._check_traditional_exit_conditions()` från `src/core/backtest/engine.py`
till nytt modul `src/core/backtest/engine_exit_utils.py` utan beteendeförändring.

## Scope IN

- `src/core/backtest/engine.py`
- `src/core/backtest/engine_exit_utils.py`
- `docs/audit/refactor/engine/command_packet_engine_modul_split_slice3_2026-03-12.md`

## Scope OUT

- Inga ändringar i `run()`-semantik utöver delegation av fallback-exit-anrop
- Inga ändringar i HTF-exit-logik (`_check_htf_exit_conditions`)
- Inga ändringar i `composable_engine.py`, `pipeline.py`, config-authority eller freeze-zoner
- Ingen ändring av publikt API/kontrakt

## Done-kriterier

- `engine.py` kallar `check_traditional_exit_conditions(...)` med samma semantiska input
- Originalmetoden tas bort från `BacktestEngine`
- `engine_exit_utils.py` innehåller extraherad logik verbatim (SL/TP/confidence/regime)
- Governance-gates körda och dokumenterade med PASS
- No behavior change verifierad

## Gates required (Opus46)

- `python -m black --check src/core/backtest/engine.py src/core/backtest/engine_exit_utils.py`
- `python -m ruff check src/core/backtest/engine.py src/core/backtest/engine_exit_utils.py`
- `python -m pytest tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest tests/backtest/test_backtest_engine.py tests/integration/test_new_htf_exit_engine_adapter.py`

## Stop Conditions

- Scope drift utanför Scope IN
- Beteendeskillnad i fallback exit-reasons (`EMERGENCY_SL|EMERGENCY_TP|CONF_DROP|REGIME_CHANGE`)
- Ny importcykel mellan `engine.py` och hjälparmodul
- Gate-fail utan tydlig rotorsak

## Pre-review (Opus46)

Utfall: **APPROVED_WITH_NOTES**

Noteringar som måste stängas före commit:

1. Slice-3 command packet måste finnas (åtgärdad i detta dokument)
2. Gates måste köras och loggas i evidens
3. Valfritt: fokuserat test för fallback-exit-kontrakt
