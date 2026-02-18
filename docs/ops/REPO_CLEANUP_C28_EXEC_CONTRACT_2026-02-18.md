# Repo Cleanup Fas C28 Execution Contract (2026-02-18)

## Category

`tooling`

## Scope IN (strict)

1. `scripts/README.md` (update policy/checklist)
2. `scripts/deprecate_move.py` (update wrapper template with usage logging)
3. `docs/ops/REPO_CLEANUP_C28_EXEC_CONTRACT_2026-02-18.md` (create)
4. `docs/ops/REPO_CLEANUP_C28_EXEC_REPORT_2026-02-18.md` (create)
5. Create missing wrappers for archive moves within 14-day deprecation window (exact file set):

- `scripts/calculate_score_260.py` (create)
- `scripts/calculate_score_realistic.py` (create)
- `scripts/check_robustness_top_trials.py` (create)
- `scripts/cleanup_optimizer_configs.py` (create)
- `scripts/create_parity_test_config.py` (create)
- `scripts/create_trial_1381_config.py` (create)
- `scripts/create_trial_1940_config.py` (create)
- `scripts/diag_trades.py` (create)
- `scripts/evaluate_all_models.py` (create)
- `scripts/freeze_data.py` (create)
- `scripts/get_trial_params.py` (create)
- `scripts/identify_config_difference.py` (create)
- `scripts/inspect_dates.py` (create)
- `scripts/inspect_trial_4.py` (create)
- `scripts/join_holdout_blocks.py` (create)
- `scripts/list_top_trials.py` (create)
- `scripts/analyze_feature_importance.py` (create)
- `scripts/analyze_feature_synergy.py` (create)
- `scripts/analyze_permutation_importance.py` (create)
- `scripts/benchmark_optimizations.py` (create)
- `scripts/calculate_ic_metrics.py` (create)
- `scripts/calculate_partial_ic.py` (create)
- `scripts/compare_htf_exits.py` (create)
- `scripts/compare_modes.py` (create)
- `scripts/compare_swing_strategies.py` (create)
- `scripts/fdr_correction.py` (create)
- `scripts/feature_ic_v18.py` (create)
- `scripts/monitor_feature_drift.py` (create)
- `scripts/debug_config_merge.py` (create)
- `scripts/debug_decision_pipeline.py` (create)
- `scripts/debug_htf_exit_usage.py` (create)
- `scripts/debug_htf_loading.py` (create)
- `scripts/debug_mcp_tunnel.py` (create)
- `scripts/debug_model_bias.py` (create)
- `scripts/debug_param_transforms.py` (create)
- `scripts/debug_strategy_signals.py` (create)
- `scripts/debug_swing_detection.py` (create)
- `scripts/diagnose_cooldown_vetoes.py` (create)
- `scripts/diagnose_execution_gap_v2.py` (create)
- `scripts/diagnose_execution_layer_gap.py` (create)
- `scripts/diagnose_feature_parity.py` (create)
- `scripts/diagnose_fib_flow.py` (create)
- `scripts/diagnose_ml_probas.py` (create)
- `scripts/diagnose_optuna_issues.py` (create)
- `scripts/diagnose_zero_trades.py` (create)
- `scripts/debug_trial_1032.py` (create)
- `scripts/inspect_ui.py` (create)
- `scripts/reliability.py` (create)
- `scripts/filter_model_features.py` (create)
- `scripts/probe_min_order_sizes.py` (create)
- `scripts/probe_min_order_sizes_live.py` (create)
- `scripts/run_timeframe_sweep.py` (create)
- `scripts/train_meta_model.py` (create)
- `scripts/train_regression_model.py` (create)
- `scripts/test_6h_original_model.py` (create)
- `scripts/test_abort_heuristic.py` (create)
- `scripts/test_deep_merge.py` (create)
- `scripts/test_exit_fibonacci.py` (create)
- `scripts/test_fibonacci_exits_real_backtest.py` (create)
- `scripts/test_frozen_exit_context.py` (create)
- `scripts/test_htf_exit_engine.py` (create)
- `scripts/test_htf_fibonacci_mapping.py` (create)
- `scripts/test_htf_simple_validation.py` (create)
- `scripts/test_local_keepalive.py` (create)
- `scripts/test_model_on_training_data.py` (create)
- `scripts/test_optuna_cache_reuse.py` (create)
- `scripts/test_partial_exit_infrastructure.py` (create)
- `scripts/test_post_local.py` (create)
- `scripts/test_rest_auth.py` (create)
- `scripts/test_rest_public.py` (create)
- `scripts/test_sse_local.py` (create)
- `scripts/test_static_frozen_exits.py` (create)
- `scripts/test_ws_auth.py` (create)
- `scripts/smoke_test.py` (create)
- `scripts/smoke_test_eth.py` (create)
- `scripts/submit_test.py` (create)

## Scope OUT

- `.github/workflows/**` och övrig CI-konfiguration
- `src/**`, `tests/**`, `config/**`, `mcp_server/**`
- `scripts/archive/**` targets (ingen funktionell ändring)
- Alla raderingar av scripts

## Constraints

- `NO BEHAVIOR CHANGE` för target-scripts och runtime-flöden.
- Endast docs + wrappers + wrapper-template-loggning.
- Wrapper-loggning ska vara best-effort och får inte påverka args-forwarding eller exit-code-beteende.
- Python-wrapper invariants:
  - Import-path får inte ändra beteende för redan befintliga wrappers.
  - För nyåterskapade wrappers (saknade root-paths) införs endast CLI-forwarding; inga funktionella ändringar i archive-targets.
- Loggfil: `scripts/deprecated-usage.log` (append), JSONL per körning med fält:
  - `timestamp` (ISO-8601)
  - `wrapper_path`
  - `target_path`

## Preconditions

1. User intent (2026-02-18): ingen radering i denna ändring.
2. 14-dagars policy ska införas i `scripts/README.md`.
3. Saknade wrappers ska återställas för archive-flyttar inom senaste 14 dagar.

## Required gates

### BEFORE

1. `pre-commit run --all-files`
2. `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `python -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `python -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`

### AFTER

1. `pre-commit run --all-files`
2. `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `python -m pytest -q tests/test_backtest_determinism_smoke.py`
4. `python -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
5. `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`
6. Scope guard: endast Scope IN-filer ändrade
7. Wrapper usage-logg verifiering (manuell):

- Representativt wrapper-anrop skapar en loggrad i `scripts/deprecated-usage.log`.
- Simulerat loggskrivfel (best-effort) påverkar inte wrapperns args-forwarding eller exit-code-beteende.

## Done criteria

1. `scripts/README.md` innehåller 14-dagarspolicy + checklista för radering.
2. Wrapper-template i `scripts/deprecate_move.py` loggar usage enligt krav utan beteendedrift.
3. Alla 76 saknade wrappers i Scope IN finns på plats.
4. Inga script-raderingar i C28.
5. Usage-loggning verifierad som best-effort utan beteendedrift.
6. Gates gröna och Opus post-code audit `APPROVED`.
