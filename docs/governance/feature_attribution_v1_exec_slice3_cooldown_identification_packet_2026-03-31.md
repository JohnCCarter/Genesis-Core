# Feature Attribution v1 — execution slice 3 packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / execution-slice / single-row only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `HIGH` — why: this slice executes the high-sensitivity canonical strategy route to classify one admitted Feature Attribution row against the locked baseline, while remaining default-off and without broadening runner/CLI/env authority.
- **Required Path:** `Full`
- **Objective:** Execute the third governed Feature Attribution v1 identification slice for `Cooldown gate seam` only and classify it descriptively as `additive`, `neutral`, `adverse`, `inconclusive`, or `invalid` against the locked baseline.
- **Candidate:** `Cooldown gate seam`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** this execution packet; one explicit single-row execution slice for `Cooldown gate seam` only; locked baseline provenance from `results/research/fib_baseline_backtest_v1/summary.md` and `results/research/fib_baseline_backtest_v1/metrics.json`; existing internal execution path only (`src/core/pipeline.py`, `src/core/backtest/engine.py`, `src/core/strategy/evaluate.py`, `src/core/strategy/decision.py`) with no code changes during execution; one human-readable report under `results/research/feature_attribution_v1/reports/`; one machine-readable manifest under `results/research/feature_attribution_v1/manifests/`.
- **Scope OUT:** no source-code changes; no tests added/edited; no new CLI surface; no new env-var surface; no runner expansion; no execution of any row other than `Cooldown gate seam`; no cluster execution; no multi-row ranking; no promotion/cutover semantics; no edits under `config/strategy/champions/**`; no fib reopening; no artifacts outside the explicitly named report/manifest outputs.
- **Expected changed files:** `docs/governance/feature_attribution_v1_exec_slice3_cooldown_identification_packet_2026-03-31.md`, `results/research/feature_attribution_v1/reports/fa_v1_cooldown_20260331_01.md`, `results/research/feature_attribution_v1/manifests/fa_v1_cooldown_20260331_01.json`
- **Max files touched:** `3`

### Frozen execution inputs

| Field                   | Value                                                     |
| ----------------------- | --------------------------------------------------------- |
| `run_id`                | `fa_v1_cooldown_20260331_01`                              |
| `selected_row_label`    | `Cooldown gate seam`                                      |
| `mode`                  | `neutralize`                                              |
| `symbol`                | `tBTCUSD`                                                 |
| `timeframe`             | `3h`                                                      |
| `start_date`            | `2023-01-01`                                              |
| `end_date`              | `2024-12-31`                                              |
| `baseline_summary_ref`  | `results/research/fib_baseline_backtest_v1/summary.md`    |
| `baseline_metrics_ref`  | `results/research/fib_baseline_backtest_v1/metrics.json`  |
| `config_source`         | `config/strategy/champions/tBTCUSD_3h.json:merged_config` |
| `capital`               | `10000.0`                                                 |
| `commission`            | `0.002`                                                   |
| `slippage`              | `0.0005`                                                  |
| `warmup_bars`           | `120`                                                     |
| `GENESIS_MODE_EXPLICIT` | `0`                                                       |
| `GENESIS_FAST_HASH`     | `0`                                                       |
| `GENESIS_RANDOM_SEED`   | `42`                                                      |

### Preconditions

- execute only at Base SHA `68537da2`
- stop if the checked-out HEAD does not resolve to `68537da2` at execution time
- stop if `results/research/fib_baseline_backtest_v1/summary.md` or `results/research/fib_baseline_backtest_v1/metrics.json` cannot be hash-locked in the manifest
- stop if the resolved effective config from `config/strategy/champions/tBTCUSD_3h.json:merged_config` cannot be hash-locked in the manifest
- stop if the resolved baseline effective config already has `gates.cooldown_bars = 0`, because the admitted cooldown seam is then operationally dormant in the locked baseline and cannot yield a meaningful one-row candidate-vs-baseline diff
- stop unless the locked baseline artifacts can be proven to derive from the same authoritative effective config as the resolved `config/strategy/champions/tBTCUSD_3h.json:merged_config`; if that equivalence cannot be proven, the slice is `invalid` and must not run

### Skill Usage

- Repo-local SPEC anchors must be invoked explicitly for this `HIGH` / `Full` execution slice.
- Required SPEC anchors:
  - `.github/skills/backtest_run.json` — execution-discipline anchor for canonical backtest handling
  - `.github/skills/feature_parity_check.json` — conditional parity anchor only; for this slice it is recorded as not runtime-authoritative and not execution-gating because the selected row does not touch feature-computation surfaces
  - `.github/skills/ri_off_parity_artifact_check.json` — artifact-integrity anchor for machine-readable manifest/report contract discipline
- These SPEC anchors do **not** replace determinism replay, config-authority checks, feature-cache invariance, pipeline-invariant checks, or the manual effective-config proof.
- Dry-run skill invocations in this slice prove repository-local SPEC-anchor resolution only; slice-level compliance must still be established by the packet manifest plus determinism, config-authority, cache, pipeline, and manual-proof gates.
- For this slice specifically, a `STOP` signal from `.github/skills/backtest_run.json` indicating `no executable steps` is informational only and must not be treated as a slice failure.

### Execution path

This slice must use the existing internal execution path only.

Allowed path for this slice:

- `GenesisPipeline.setup_environment(seed=42)`
- `GenesisPipeline.create_engine(...)`
- `BacktestEngine.run(policy=..., configs=merged_config, verbose=False)`

The explicit request surface must remain internal and exact-match only:

- `policy["feature_attribution"]["selected_row_label"] = "Cooldown gate seam"`
- `policy["feature_attribution"]["mode"] = "neutralize"`

No new CLI flag, runner option, config-authority path, or environment toggle may be introduced for this execution slice.

### Classification boundary

The output label for this slice must remain descriptive-only and must use the locked Phase 5 vocabulary only:

- `additive`
- `neutral`
- `adverse`
- `inconclusive`
- `invalid`

Interpretation for this slice must remain qualitative and one-row-vs-locked-baseline only:

- if neutralizing the selected row produces directionally worse candidate evidence versus the locked baseline, the row may be described as `additive` for this frozen slice only
- if neutralizing the selected row produces no clear directional change, the row may be described as `neutral`
- if neutralizing the selected row produces directionally improved candidate evidence versus the locked baseline, the row may be described as `adverse` for this frozen slice only
- if evidence is mixed or insufficient, the row must be described as `inconclusive`
- if provenance, selector, effective-config, or gate discipline breaks, the row must be described as `invalid`

These labels are descriptive outputs for this frozen single-slice run only.
They are not general causal proof, not a ranking rule, and not implementation or promotion authority.

This packet defines no numeric cutoff and no ranking rule.

### Gates required

- `python -m ruff check src/core/strategy/decision.py tests/utils/test_decision_edge.py`
- `python -m pytest -q tests/utils/test_decision_edge.py tests/utils/test_decision_gates_contract.py tests/utils/test_decision.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/governance/test_config_authority_hash_contract.py`
- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
- `python scripts/run_skill.py --skill backtest_run --manifest dev --dry-run`
- `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev --dry-run`
- repo-local acknowledgment that `.github/skills/feature_parity_check.json` remains conditional and non-execution-gating for this slice because no feature-computation surface is in scope
- manual provenance check that baseline summary + metrics + config source align with the frozen execution inputs above
- manual effective-config check that the only intentional config diff is neutralization of `gates.cooldown_bars`, while active `cooldown_remaining` masking remains an explicit slice-local derivative-state effect only

### Stop Conditions

- scope drift to any row other than `Cooldown gate seam`
- any requirement to add a new CLI, runner, env-var, or config-authority surface
- any default-behavior change without explicit internal request
- inability to bind candidate execution to the locked baseline provenance
- inability to record Base SHA, baseline hashes, or resolved effective-config hash in the manifest
- any gate failure
- baseline effective `gates.cooldown_bars` already equals `0`, making the admitted seam dormant in the locked baseline
- any evidence that the effective-config diff escapes `gates.cooldown_bars`
- any evidence that runtime state masking escaped the single explicit opt-in path
- any attempt to rank multiple rows or turn the descriptive label into a direct action

### Output required

- one executed single-row candidate-vs-baseline comparison for `Cooldown gate seam`
- one descriptive classification using the locked Phase 5 vocabulary
- one report at `results/research/feature_attribution_v1/reports/fa_v1_cooldown_20260331_01.md`
- one manifest at `results/research/feature_attribution_v1/manifests/fa_v1_cooldown_20260331_01.json`

The manifest must contain at minimum:

- `run_id`
- `base_sha`
- `executed_at_utc`
- `selected_row_label`
- `mode`
- `baseline_summary_ref`
- `baseline_summary_sha256`
- `baseline_metrics_ref`
- `baseline_metrics_sha256`
- `baseline_effective_config_sha256`
- `resolved_effective_config_ref`
- `resolved_effective_config_sha256`
- `baseline_effective_cooldown_bars`
- `candidate_effective_cooldown_bars`
- `effective_config_delta_scope`
- `derived_state_delta_scope`
- `classification`
- `locked_metric_snapshot_baseline`
- `locked_metric_snapshot_candidate`
- `locked_metric_delta_summary`
- `gate_results`

## Notes

This packet authorizes only the third identification slice.

It does not authorize:

- identifying all features in one batch
- running additional rows without a separate later packet
- introducing a generic attribution framework
- turning the descriptive result into implementation, removal, tuning, or promotion authority
