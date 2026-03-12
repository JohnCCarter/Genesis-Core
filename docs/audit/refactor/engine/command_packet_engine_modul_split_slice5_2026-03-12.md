# Command Packet — engine-modul-split Slice 5

Datum: 2026-03-12
Branch: worktree-engine-modul-split
Base SHA: 6d9c0880 (slice 4 commit)
Mode: RESEARCH (source=branch:feature/engine-modul-split)
Risk: HIGH (touches `src/core/backtest/*`)
Required Path: Full (high-sensitivity)
Category: refactor(server)
Constraint: NO BEHAVIOR CHANGE

---

## Objective

Slutföra engine-modul-split med no-behavior-change extraktion av
`BacktestEngine._check_htf_exit_conditions()` till ny modul
`src/core/backtest/engine_htf_exit_dispatcher.py`.

## Skill Usage

- `.github/skills/repo_clean_refactor.json`
- `.github/skills/feature_parity_check.json`

## Scope IN

- `src/core/backtest/engine.py`
- `src/core/backtest/engine_htf_exit_dispatcher.py` (ny)
- `docs/audit/refactor/engine/command_packet_engine_modul_split_slice5_2026-03-12.md`

## Scope OUT

- Inga ändringar i `run()` utöver oförändrat metodanrop
- Inga ändringar i fallback-exit (`engine_exit_utils`) eller precompute-flöde
- Inga ändringar i `composable_engine.py`, `pipeline.py`, config-authority eller freeze-zoner
- Ingen ändring av publikt API/kontrakt

## Done-kriterier

- `_check_htf_exit_conditions`-logik flyttas verbatim till dispatcher-funktion
- `engine.py` behåller metoden som tunn delegation med samma call-shape
- Samma return reasons och debug/logg-sidodata
- Governance-gates körda med PASS
- Dispatcher får inte runtime-importera `BacktestEngine`

## Föreslagna gates

- `pre-commit run --all-files`
- `python -m black --check src/core/backtest/engine.py src/core/backtest/engine_htf_exit_dispatcher.py`
- `python -m ruff check src/core/backtest/engine.py src/core/backtest/engine_htf_exit_dispatcher.py`
- `python -m bandit -r src -c bandit.yaml`
- `python -m pytest tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `python -m pytest tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- `python -m pytest tests/backtest/test_htf_exit_engine.py tests/backtest/test_htf_exit_engine_selection.py tests/backtest/test_htf_exit_engine_htf_context_schema.py tests/integration/test_new_htf_exit_engine_adapter.py tests/backtest/test_backtest_engine.py`

## Stop Conditions

- Scope drift utanför Scope IN
- Ändrade return-reasons eller action-mappning i HTF-exitvägen
- Ändrad trail-stop/break-even-semantik
- Ny importcykel mellan engine och dispatcher

## Pre-review (Opus46)

Utfall: **APPROVED_WITH_NOTES**

Inlåsta noter:

1. Formella kontraktsfält + skill-usage måste finnas
2. Ingen runtime-import av `BacktestEngine` i dispatcher-modul
3. Full gate-stack inklusive pre-commit + bandit krävs före commit

## Gate-resultat

| Gate                                                 | Resultat |
| ---------------------------------------------------- | -------- |
| pre-commit run --all-files                           | PASS     |
| black (`engine.py`, `engine_htf_exit_dispatcher.py`) | PASS     |
| ruff (`engine.py`, `engine_htf_exit_dispatcher.py`)  | PASS     |
| bandit (`-r src -c bandit.yaml`)                     | PASS     |
| import smoke                                         | PASS     |
| determinism replay smoke                             | PASS     |
| feature cache invariance                             | PASS     |
| pipeline invariant selector                          | PASS     |
| parity: runtime vs precomputed                       | PASS     |
| parity: precompute vs runtime integration            | PASS     |
| focused HTF + adapter + backtest tests               | PASS     |

## Post-audit (Opus46)

Utfall: **APPROVED**

- READY_TO_COMMIT: **YES**
