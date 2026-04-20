# RI advisory environment-fit trade-level deterministic baseline implementation packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded research-only implementation / results-only / default unchanged`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded research-only materialization of the first trade-level deterministic baseline on isolated research surfaces; no runtime/config/default/authority mutation.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** materialize the first bounded trade-level deterministic baseline as a research-only artifact slice that computes trade-side predicates, trade labels, row-side bands, bounded row mappings, yearly summaries, and deterministic replay proof without touching runtime, ML, or production-authority surfaces.
- **Candidate:** `RI advisory environment-fit trade-level deterministic baseline implementation`
- **Base SHA:** `b30e6fbac3839a2ced1c1c18474f5545779962b7`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`

### Scope

- **Scope IN:**
  - `docs/governance/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_packet_2026-04-17.md`
  - `tmp/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_20260417.py`
  - approved result artifacts under `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/`
  - `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - existing `results/**` artifacts outside the new approved output dir
  - any runtime-facing score implementation
  - any ML/model work
  - any Phase 4 opening
  - any promotion framing or runtime-readiness claim
  - any claim of restored exact row-level authority
  - any mutation of upstream captured evidence files in place
- **Expected changed files:**
  - `docs/governance/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_packet_2026-04-17.md`
  - `tmp/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_20260417.py`
  - `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/predicate_surface.json`
  - `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/trade_label_surface.ndjson`
  - `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/row_band_surface.ndjson`
  - `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/row_mapping_surface.ndjson`
  - `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/summary.json`
  - `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/boundary_manifest.json`
  - `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/manifest.json`
  - `results/research/ri_advisory_environment_fit/trade_level_deterministic_baseline_implementation_2026-04-17/closeout.md`
  - `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_2026-04-17.md`
- **Max files touched:** `11`

### Skill coverage

- Repo-local skill loaded: `.github/skills/python_engineering.json`
- Repo-local skill loaded: `.github/skills/genesis_backtest_verify.json`
- `genesis_backtest_verify` is used only as deterministic verification discipline for post-implementation gate selection; it does not authorize trading-artifact mutation in this slice.
- No dedicated repo-local skill currently exists for the trade-level deterministic baseline materialization surface.
- A dedicated skill for this exact lane is therefore only `föreslagen` and explicitly OUT OF SCOPE for this slice.

### Fixed inputs and authority boundaries

#### Contract / boundary inputs

- `docs/analysis/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_label_mapping_contract_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_evidence_family_leakage_boundary_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_definition_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_readiness_2026-04-17.md`

These are governance and definition inputs only. They define meaning, allowed families, and fail-closed boundaries.

#### Data / evidence inputs the script may consume directly

- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`

The script may derive trade-level predicate and label surfaces from those locked research inputs only.
It may not call runtime entrypoints, write back to upstream captures, or import any production-authority source.

#### Determinism and isolation constraints

The script must remain fully deterministic and isolated.

- no environment-variable reads
- no network access
- no globbing or current-working-directory discovery as an input-selection mechanism
- no randomness
- no wall-clock timestamps inside replay-hashed artifacts
- no imports from runtime/config-authority helpers or `src/core/**`

If any additional source is required, the slice must stop rather than discover a new input implicitly.

### Allowed implementation work

The script may do only the following:

1. materialize a trade-side predicate layer from already admitted realized-trade evidence families only
2. apply the fixed trade-label gate order to emit only:
   - `supportive_trade_outcome`
   - `hostile_trade_outcome`
   - `transition_trade_outcome`
   - `non_evaluable_trade_context`
3. materialize the row-side entry-time bands only:
   - `clarity_band`
   - `transition_proximity_band`
   - `confidence_band`
   - `context_support_band`
4. apply the fixed row-mapping rule order to emit only:
   - `supportive_context_likelihood`
   - `hostile_context_likelihood`
   - `transition_risk_likelihood`
   - `authority_strength`
   - `coverage_state`
5. emit yearly summaries, warnings, and deterministic replay proof

If a required field, mapping rule, or admitted contract definition is missing or ambiguous, the script must fail closed:

- stop, or
- emit `coverage_state = unsupported`, or
- emit `non_evaluable_trade_context`

It must never backfill from a new source or infer a stronger authority state than the admitted inputs justify.

### Explicitly forbidden operations

- any write under `src/**`, `tests/**`, `config/**`, or `artifacts/**`
- any runtime code path, runtime API path, or runtime config authority mutation
- any import from `src/core/**` or runtime/config-authority helper modules
- any ML/model fitting, threshold learning, or comparator work
- any environment-variable read, network access, glob/CWD-based source discovery, randomness, or wall-clock timestamp inserted into replay-hashed artifacts
- any use of post-entry evidence in row-side banding or row mapping, including:
  - `total_pnl`
  - `pnl_delta`
  - `mfe_16_atr`
  - `mae_16_atr`
  - `fwd_*`
  - `continuation_score`
  - future cohort membership
- any claim that row outputs are restored exact Phase-2-faithful authority
- any hidden weakening of unsupported coverage, weak-authority reporting, or contradiction-year reporting

### Required outputs

The slice must emit at minimum:

- one predicate artifact recording trade-side predicate states
- one trade-label surface artifact with final label and gate path
- one row-band surface artifact with the materialized entry-time bands
- one row-mapping surface artifact with bounded row outputs
- one summary artifact with yearly counts, warnings, and contradiction-year deltas
- one boundary manifest recording:
  - `runtime_integration = false`
  - `ml_opening = false`
  - `phase4_opening = false`
  - `exact_row_level_authority_recovery = false`
  - `post_entry_row_mapping_leakage = false`
- one manifest containing input hashes and replay hashes
- replay hashes must be computed from canonically serialized content only:
  - stable ordering
  - normalized key order
  - normalized newline/encoding behavior
  - no timestamp or run-specific metadata inside hashed payloads
- one closeout memo stating whether the bounded implementation stayed inside the contract and what the next admissible step is

### Gates required

- `pre-commit run --files docs/governance/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_packet_2026-04-17.md tmp/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_20260417.py docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_implementation_2026-04-17.md`
- `python -m pytest tests/backtest/test_runner_direct_includes_merged_config.py`
- `python -m pytest tests/backtest/test_backtest_engine.py::test_engine_run_skip_champion_merge_does_not_load_champion`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- bounded execution of the implementation script itself
- deterministic replay of the implementation script on identical inputs with stable hashes for:
  - predicate artifact
  - trade-label artifact
  - row-mapping artifact
  - summary artifact

### Stop Conditions

- any need to touch runtime code, runtime config, family-authority paths, or shared production helpers
- any need to import forbidden post-entry evidence into row-side bands or row mappings
- any need to widen output semantics beyond the already defined bounded trade labels and row outputs
- any missing or ambiguous required field/rule/contract input that would otherwise force heuristic backfill or implicit source expansion
- any output write outside the approved result directory and memo targets
- any replay instability on identical inputs
- any attempt to hide coverage collapse, weak-authority dominance, or contradiction-year inversion
- any wording that upgrades this slice into runtime readiness, ML readiness, promotion readiness, or restored exact row-level authority

### Output required

- one governance packet
- one bounded `tmp/` implementation script
- one isolated results directory with deterministic artifacts
- one closeout memo under `docs/analysis/`
- one implementation report suitable for Opus post-diff audit

## Bottom line

This packet proposes one narrow next step only:

- materialize the first bounded trade-level deterministic baseline entirely on research surfaces with deterministic replay and fail-closed warnings

It does not authorize runtime integration, ML comparison, Phase 4, or any claim that the old exact row-level authority problem has been recovered.
