# Script Activity Evidence Report

- Generated at: `2026-02-17T14:59:08.945707+00:00`
- Classifier version: `c7-v1`
- include_archive: `False`

## Summary

- Total scripts: **129**
- ACTIVE: **15**
- REVIEW: **51**
- STALE: **63**

## Top scripts

| Script | Status | Score | Last commit (days) | Runtime refs | Tests refs | Docs active refs | Docs historical refs |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `scripts/train_model.py` | `ACTIVE` | 21 | 39 | 1 | 1 | 3 | 6 |
| `scripts/preflight_optuna_check.py` | `ACTIVE` | 18 | 19 | 1 | 1 | 10 | 0 |
| `scripts/fetch_historical.py` | `ACTIVE` | 17 | 39 | 1 | 0 | 2 | 8 |
| `scripts/paper_trading_runner.py` | `ACTIVE` | 17 | 1 | 1 | 1 | 6 | 1 |
| `scripts/precompute_features.py` | `ACTIVE` | 17 | 39 | 1 | 0 | 3 | 3 |
| `scripts/run_backtest.py` | `ACTIVE` | 17 | 26 | 3 | 0 | 32 | 7 |
| `scripts/extract_backtest_provenance.py` | `ACTIVE` | 14 | 33 | 1 | 0 | 1 | 0 |
| `scripts/select_champion.py` | `ACTIVE` | 14 | 19 | 1 | 0 | 1 | 5 |
| `scripts/validate_optimizer_config.py` | `ACTIVE` | 14 | 19 | 1 | 0 | 8 | 1 |
| `scripts/build_auth_headers.py` | `ACTIVE` | 13 | 39 | 1 | 0 | 1 | 3 |
| `scripts/optimizer.py` | `ACTIVE` | 13 | 32 | 1 | 0 | 10 | 0 |
| `scripts/validate_registry.py` | `ACTIVE` | 11 | 32 | 0 | 0 | 3 | 0 |
| `scripts/verify_mcp_installation.py` | `ACTIVE` | 11 | 12 | 1 | 0 | 0 | 0 |
| `scripts/run_skill.py` | `ACTIVE` | 10 | 32 | 0 | 1 | 1 | 0 |
| `scripts/precompute_features_v17.py` | `ACTIVE` | 9 | 19 | 0 | 0 | 1 | 1 |
| `scripts/validate_data.py` | `REVIEW` | 7 | 39 | 0 | 0 | 0 | 3 |
| `scripts/check_trial_config_equivalence.py` | `REVIEW` | 6 | 39 | 0 | 0 | 5 | 0 |
| `scripts/create_trial_208_config.py` | `REVIEW` | 6 | 39 | 0 | 0 | 0 | 0 |
| `scripts/curate_features.py` | `REVIEW` | 6 | 39 | 0 | 0 | 0 | 0 |
| `scripts/evaluate_model.py` | `REVIEW` | 6 | 19 | 0 | 0 | 1 | 2 |
| `scripts/extract_optuna_blocks_top_trials.py` | `REVIEW` | 6 | 39 | 0 | 0 | 0 | 0 |
| `scripts/precompute_features_v18.py` | `REVIEW` | 6 | 39 | 0 | 0 | 0 | 0 |
| `scripts/sweep_optuna_holdout_top_trials.py` | `REVIEW` | 6 | 39 | 0 | 0 | 0 | 0 |
| `scripts/validate_holdout.py` | `REVIEW` | 6 | 39 | 0 | 0 | 0 | 1 |
| `scripts/validate_purged_wfcv.py` | `REVIEW` | 6 | 19 | 0 | 0 | 3 | 0 |
| `scripts/verify_exits_forced.py` | `REVIEW` | 6 | 39 | 0 | 0 | 0 | 0 |
| `scripts/analyze_optuna_db.py` | `REVIEW` | 5 | 39 | 0 | 0 | 2 | 2 |
| `scripts/analyze_optuna_run_identity.py` | `REVIEW` | 5 | 19 | 0 | 0 | 1 | 0 |
| `scripts/analyze_regime_performance.py` | `REVIEW` | 5 | 19 | 0 | 0 | 1 | 0 |
| `scripts/analyze_w2_exit_breakdown.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 0 |
| `scripts/apply_runtime_patch.py` | `REVIEW` | 5 | 39 | 0 | 0 | 3 | 0 |
| `scripts/backtest_with_fees.py` | `REVIEW` | 5 | 19 | 0 | 0 | 1 | 1 |
| `scripts/benchmark_backtest.py` | `REVIEW` | 5 | 39 | 0 | 0 | 3 | 0 |
| `scripts/benchmark_numba_labeling.py` | `REVIEW` | 5 | 19 | 0 | 0 | 1 | 0 |
| `scripts/benchmark_optuna_performance.py` | `REVIEW` | 5 | 39 | 0 | 0 | 6 | 0 |
| `scripts/calculate_paper_trading_metrics.py` | `REVIEW` | 5 | 13 | 0 | 0 | 9 | 0 |
| `scripts/calibrate_fib_gates.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 0 |
| `scripts/curate_1d_candles.py` | `REVIEW` | 5 | 19 | 0 | 0 | 1 | 0 |
| `scripts/extract_ev_distribution.py` | `REVIEW` | 5 | 15 | 0 | 0 | 1 | 0 |
| `scripts/generate_meta_labels.py` | `REVIEW` | 5 | 19 | 0 | 0 | 2 | 2 |
| `scripts/hqt_audit_pf_first.py` | `REVIEW` | 5 | 13 | 0 | 0 | 2 | 0 |
| `scripts/optimize_ema_slope_params.py` | `REVIEW` | 5 | 19 | 0 | 0 | 1 | 1 |
| `scripts/promote_v5a_to_champion.py` | `REVIEW` | 5 | 14 | 0 | 0 | 3 | 0 |
| `scripts/reproduce_trial_subprocess.py` | `REVIEW` | 5 | 39 | 0 | 0 | 2 | 0 |
| `scripts/run_champion_smoke.py` | `REVIEW` | 5 | 39 | 0 | 0 | 2 | 0 |
| `scripts/run_composable_backtest_no_fib.py` | `REVIEW` | 5 | 15 | 0 | 0 | 2 | 0 |
| `scripts/run_composable_backtest_phase2.py` | `REVIEW` | 5 | 15 | 0 | 0 | 1 | 0 |
| `scripts/run_composable_backtest_poc.py` | `REVIEW` | 5 | 18 | 0 | 0 | 2 | 0 |
| `scripts/run_extended_validation_2024.py` | `REVIEW` | 5 | 13 | 0 | 0 | 5 | 0 |
| `scripts/run_milestone3_exp1.py` | `REVIEW` | 5 | 14 | 0 | 0 | 3 | 0 |
| `scripts/run_milestone4_exp1.py` | `REVIEW` | 5 | 13 | 0 | 0 | 2 | 0 |
| `scripts/run_milestone4_exp2.py` | `REVIEW` | 5 | 13 | 0 | 0 | 2 | 0 |
| `scripts/sanity_check_evgate_percentiles.py` | `REVIEW` | 5 | 13 | 0 | 0 | 1 | 0 |
| `scripts/sanity_check_size_zero_reasons.py` | `REVIEW` | 5 | 13 | 0 | 0 | 3 | 0 |
| `scripts/scan_phase3_fine_runs.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 0 |
| `scripts/smoke_test_fixes.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 2 |
| `scripts/summarize_hparam_results.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 3 |
| `scripts/test_ws_public.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 5 |
| `scripts/tune_confidence_threshold.py` | `REVIEW` | 5 | 19 | 0 | 0 | 1 | 0 |
| `scripts/tune_triple_barrier.py` | `REVIEW` | 5 | 19 | 0 | 0 | 2 | 0 |
| `scripts/validate_vectorized_features.py` | `REVIEW` | 5 | 19 | 0 | 0 | 1 | 0 |
| `scripts/validate_zero_trade_risk.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 2 |
| `scripts/verify_candidate_exact.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 0 |
| `scripts/verify_config_loading.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 0 |
| `scripts/verify_fib_connection.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 0 |
| `scripts/verify_runner_fix.py` | `REVIEW` | 5 | 39 | 0 | 0 | 1 | 0 |
| `scripts/benchmark_performance.py` | `STALE` | 2 | 39 | 0 | 0 | 0 | 1 |
| `scripts/calculate_ic_by_regime.py` | `STALE` | 2 | 39 | 0 | 0 | 0 | 1 |
| `scripts/validate_all_indicators.py` | `STALE` | 2 | 39 | 0 | 0 | 0 | 2 |
| `scripts/audit_optuna_objective_parity.py` | `STALE` | 1 | 39 | 0 | 0 | 0 | 1 |
| `scripts/burn_in.py` | `STALE` | 1 | 39 | 0 | 0 | 0 | 1 |
| `scripts/compare_htf_exits.py` | `STALE` | 1 | 39 | 0 | 0 | 0 | 1 |
| `scripts/compare_modes.py` | `STALE` | 1 | 19 | 0 | 0 | 2 | 1 |
| `scripts/compare_swing_strategies.py` | `STALE` | 1 | 39 | 0 | 0 | 0 | 1 |
| `scripts/migrate_model_structure.py` | `STALE` | 1 | 39 | 0 | 0 | 0 | 2 |
| `scripts/parse_burnin_log.py` | `STALE` | 1 | 2 | 0 | 0 | 0 | 2 |
| `scripts/precompute_features_fast.py` | `STALE` | 1 | 39 | 0 | 0 | 0 | 2 |
| `scripts/repo_inventory_report.py` | `STALE` | 1 | 2 | 0 | 0 | 0 | 1 |
| `scripts/smoke_submit_call.py` | `STALE` | 1 | 39 | 0 | 0 | 0 | 2 |
| `scripts/smoke_submit_flow.py` | `STALE` | 1 | 39 | 0 | 0 | 0 | 2 |
| `scripts/validate_v17_holdout.py` | `STALE` | 1 | 19 | 0 | 0 | 0 | 1 |
| `scripts/analyze_gate_dominance.py` | `STALE` | 0 | 26 | 0 | 0 | 0 | 0 |
| `scripts/benchmark_features_modes.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/calculate_score_260.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/calculate_score_realistic.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/check_robustness_top_trials.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/cleanup_optimizer_configs.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/create_parity_test_config.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/create_trial_1381_config.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/create_trial_1940_config.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/curate_3h_candles.py` | `STALE` | 0 | 19 | 0 | 0 | 0 | 0 |
| `scripts/diag_trades.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/evaluate_all_models.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/freeze_data.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/get_trial_params.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/identify_config_difference.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/inspect_dates.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/inspect_trial_4.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/join_holdout_blocks.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/list_top_trials.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/monitor_optuna_study.py` | `STALE` | 0 | 19 | 0 | 0 | 0 | 0 |
| `scripts/optimize_htf_custom.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/organize_optuna_docs.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/phase2_metrics.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/profile_pipeline.py` | `STALE` | 0 | 19 | 0 | 0 | 0 | 0 |
| `scripts/reproduce_mismatch.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/reproduce_trial_from_merged_config.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/resample_1h_to_3h.py` | `STALE` | 0 | 35 | 0 | 0 | 0 | 0 |
| `scripts/resample_1h_to_6h.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/run_ltf_confidence_grid.py` | `STALE` | 0 | 19 | 0 | 0 | 0 | 0 |
| `scripts/run_optimizer_smoke.py` | `STALE` | 0 | 19 | 0 | 0 | 0 | 0 |
| `scripts/run_phase2c_extended.py` | `STALE` | 0 | 19 | 0 | 0 | 0 | 0 |
| `scripts/run_phase2d_corrected.py` | `STALE` | 0 | 19 | 0 | 0 | 0 | 0 |
| `scripts/run_phase3_fine.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/show_best_results.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/show_feature_loading_modes.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/show_loaded_model.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/show_v4_features_loading.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/simple_htf_integration_check.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/sync_precompute_and_train.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/trace_champion_loading.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/validate_atr_vectorized.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/validate_v17_ic.py` | `STALE` | 0 | 19 | 0 | 0 | 0 | 0 |
| `scripts/verify_async_candles.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/verify_exits_forced_v2.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/verify_exits_loose.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/verify_integration.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/verify_v17_htf_cols.py` | `STALE` | 0 | 39 | 0 | 0 | 0 | 0 |
| `scripts/classify_script_activity.py` | `STALE` | -3 | 0 | 0 | 0 | 0 | 2 |

## Note

Klassificeringen är evidensbaserad prioritering för cleanup-beslut, inte automatisk radering/flytt. Verifiera alltid med tranche-kontrakt + Opus review.
