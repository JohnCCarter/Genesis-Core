# RI advisory environment-fit — trade-level deterministic baseline implementation

This memo records the first bounded research-only materialization slice for the trade-level deterministic baseline.
It is artifact-only and fail-closed.

Governance packet: `docs/governance/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_packet_2026-04-17.md`

## What was materialized

The slice materialized exactly the approved research artifacts under:

- `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/`

Produced files:

- `predicate_surface.json`
- `trade_label_surface.ndjson`
- `row_band_surface.ndjson`
- `row_mapping_surface.ndjson`
- `summary.json`
- `boundary_manifest.json`
- `manifest.json`
- `closeout.md`

The result stayed contained.
`manifest.json` records `containment.verdict = PASS` and no unexpected create/modify/delete events outside the approved output root.

## Deterministic replay evidence

Replay remained stable on identical locked inputs.
The summary artifact recorded these matching hashes:

- predicate hash: `1f4b7d6c96acc0cdb5e9445f7b6846ff0b03858768fbb4b2083fa951760c4745`
- trade-label hash: `2dc3ea8fe43188a53b1a1db8aca72b9a63e46e286d19bf4426f0cfcdfa2d8826`
- row-band hash: `d3943c7227d0df8c6ef40fa081aeec9faf1441313cfba2e79ae03a15467bc409`
- row-mapping hash: `e094545f1ac5e0d1fd73f4aea4af76dda19f95201d09e6f41df8c3b671288dbe`
- summary hash: `9dfb79fa511f938854d88c6d458479603bc84a0fcab670e7cbe0b7134e56bae8`

So the research slice is reproducible on its locked capture-v2 input surface.

## What the slice proved

### 1. The predicate layer can be materialized deterministically

The script materialized the required trade-side predicate surface and did so without touching runtime or ML paths.
That part is now no longer hypothetical.

### 2. The row-band layer can also be materialized deterministically

The script materialized bounded row-side bands from entry-time inputs only.
The yearly band counts are explicit rather than hidden:

- clarity bands
- transition-proximity bands
- confidence bands
- context-support bands

This stayed below runtime-authority surfaces and remained explicitly exploratory / non-authoritative.

### 3. The current locked capture-v2 surface still cannot support directional trade labels honestly

The decisive fail-closed finding is unchanged in substance:

- `coverage_evaluable_count = 146`
- `path_quality_available_count = 0`
- `instability_available_count = 0`
- all 146 trades fell through `conflict_fallback`
- all 146 trades remained `non_evaluable_trade_context`

So the baseline implementation did **not** recover supportive/hostile/transition trade authority from the current locked surface.
It proved the opposite more concretely:

- the directional trade-label layer still lacks admissible realized path-quality inputs
- the baseline can be implemented honestly only by failing closed on that gap

### 4. Row mapping remained fully non-evaluable, as required by the contract

Because the linked trade-label surface stayed fully non-evaluable, the row mapping propagated that state instead of pretending to know more:

- `coverage_state = non_evaluable_trade_context` for all 146 rows
- `authority_strength = 0` for all 146 rows
- all supportive/hostile/transition likelihood outputs remained `0`

This is a weakness signal, but it is the honest one.
The slice did not leak post-entry evidence into row mapping to make the surface look more useful than it is.

## 2024 versus 2025

The contradiction-year surface remained explicit.
The implementation did **not** hide `2025`.

Observed result:

- `directional_balance_2024 = 0`
- `directional_balance_2025 = 0`
- `directional_inversion_detected = false`
- `non_evaluable_delta_2025_minus_2024 = 2`

So there was no directional inversion only because both years stayed fully non-evaluable at the trade-label layer.
That is not a success signal.
It is simply a stable fail-closed outcome.

## Boundary status

The boundary manifest stayed explicit:

- `runtime_integration = false`
- `ml_opening = false`
- `phase4_opening = false`
- `exact_row_level_authority_recovery = false`
- `post_entry_row_mapping_leakage = false`
- `approximate_band_thresholds = true`
- `exploratory = true`
- `non_authoritative = true`

So this slice remains strictly below runtime, ML, Phase 4, and any exact row-level-authority claim.

## Gates run

The following required gates were run and passed:

- targeted docs gate on `docs/governance/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_packet_2026-04-17.md`
- bounded script execution of `tmp/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_20260417.py`
- `python -m pytest tests/backtest/test_runner_direct_includes_merged_config.py tests/backtest/test_backtest_engine.py::test_engine_run_skip_champion_merge_does_not_load_champion tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

All five selected pytest gates passed.

## Honest verdict

The first bounded implementation slice is now complete.
It succeeded operationally and failed closed analytically.

That means:

- predicate layer: materialized
- row-band layer: materialized
- deterministic replay: proven
- containment: proven
- supportive/hostile/transition trade authority on locked capture-v2 surface: **still not recovered**
- exact row-level authority: still closed

## Exact next admissible step

The narrowest honest next move is **not** runtime integration and not ML comparison.

The next admissible question is:

- may a richer realized-trade evidence surface open for the missing path-quality / instability predicates?

If the answer is no, then the current trade-level deterministic baseline remains a documented fail-closed boundary artifact, not a promotable scoring surface.
