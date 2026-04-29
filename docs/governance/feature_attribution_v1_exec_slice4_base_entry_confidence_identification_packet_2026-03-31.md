# Feature Attribution v1 — execution slice 4 packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / execution-slice / single-row only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `HIGH` — why: this slice reviews an admitted threshold seam in the high-sensitivity canonical strategy route and must avoid accidentally broadening into the separately admitted signal-adaptation threshold cluster.
- **Required Path:** `Full`
- **Objective:** Resolve whether `Base entry confidence seam` can be executed as an independent single-row Feature Attribution v1 slice against the locked baseline, or whether it must be stopped as `invalid` because the seam is shadowed by the separately admitted signal-adaptation cluster in the canonical route.
- **Candidate:** `Base entry confidence seam`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** this execution packet; one explicit single-row governance assessment for `Base entry confidence seam` only; locked baseline provenance from `results/research/fib_baseline_backtest_v1/summary.md` and `results/research/fib_baseline_backtest_v1/metrics.json`; code-evidence review of `src/core/strategy/decision_gates.py::select_candidate`, `src/core/strategy/evaluate.py`, and `src/core/strategy/features_asof.py`; one human-readable report under `results/research/feature_attribution_v1/reports/`; one machine-readable manifest under `results/research/feature_attribution_v1/manifests/`.
- **Scope OUT:** no source-code changes; no tests added/edited; no candidate backtest unless seam independence is first proven; no new CLI surface; no new env-var surface; no runner expansion; no execution of any row other than `Base entry confidence seam`; no cluster execution; no multi-row ranking; no promotion/cutover semantics; no edits under `config/strategy/champions/**`; no fib reopening; no artifacts outside the explicitly named report/manifest outputs.
- **Expected changed files:** `docs/governance/feature_attribution_v1_exec_slice4_base_entry_confidence_identification_packet_2026-03-31.md`, `results/research/feature_attribution_v1/reports/fa_v1_base_entry_conf_20260331_01.md`, `results/research/feature_attribution_v1/manifests/fa_v1_base_entry_conf_20260331_01.json`
- **Max files touched:** `3`

### Frozen execution inputs

| Field                   | Value                                                     |
| ----------------------- | --------------------------------------------------------- |
| `run_id`                | `fa_v1_base_entry_conf_20260331_01`                       |
| `selected_row_label`    | `Base entry confidence seam`                              |
| `mode`                  | `neutralize`                                              |
| `symbol`                | `tBTCUSD`                                                 |
| `timeframe`             | `3h`                                                      |
| `baseline_summary_ref`  | `results/research/fib_baseline_backtest_v1/summary.md`    |
| `baseline_metrics_ref`  | `results/research/fib_baseline_backtest_v1/metrics.json`  |
| `config_source`         | `config/strategy/champions/tBTCUSD_3h.json:merged_config` |
| `GENESIS_MODE_EXPLICIT` | `0`                                                       |
| `GENESIS_FAST_HASH`     | `0`                                                       |
| `GENESIS_RANDOM_SEED`   | `42`                                                      |

### Preconditions

- execute only at Base SHA `68537da2`
- stop if the checked-out HEAD does not resolve to `68537da2` at execution time
- stop if `results/research/fib_baseline_backtest_v1/summary.md` or `results/research/fib_baseline_backtest_v1/metrics.json` cannot be hash-locked in the manifest
- stop if the resolved effective config from `config/strategy/champions/tBTCUSD_3h.json:merged_config` cannot be hash-locked in the manifest
- stop if the locked baseline effective config enables `thresholds.signal_adaptation` with zone-specific `entry_conf_overall` thresholds and the canonical route still provides `current_atr` plus `atr_percentiles`, because the admitted base-threshold seam is then shadowed by the separately admitted signal-adaptation cluster
- stop unless the locked baseline artifacts can be proven to derive from the same authoritative effective config as the resolved `config/strategy/champions/tBTCUSD_3h.json:merged_config`; if that equivalence cannot be proven, the slice is `invalid` and must not run

### Skill Usage

- Repo-local SPEC anchors remain supporting evidence only for this `HIGH` / `Full` assessment slice.
- Relevant SPEC anchors:
  - `.github/skills/feature_parity_check.json` — parity/default-off discipline reference only
  - `.github/skills/ri_off_parity_artifact_check.json` — artifact-integrity discipline for report/manifest recording
- These anchors do **not** replace the locked code-evidence review of the canonical route or the golden-trace test evidence.

### Evidence route

This slice must use the existing canonical evidence route only.

Required citations for this slice:

- `src/core/strategy/decision_gates.py::select_candidate`
- `src/core/strategy/evaluate.py` state assembly for `current_atr` and `atr_percentiles`
- `src/core/strategy/features_asof.py` ATR percentile production
- `config/strategy/champions/tBTCUSD_3h.json:merged_config`
- `tests/integration/test_golden_trace_runtime_semantics.py::test_signal_adaptation_zone_overrides_base_thresholds`
- `tests/integration/test_golden_trace_runtime_semantics.py::test_signal_adaptation_missing_percentiles_locks_low_zone`

No new runtime path, CLI flag, or implementation surface may be introduced for this slice.

### Classification boundary

The output label for this slice must remain descriptive-only and must use the locked Phase 5 vocabulary only:

- `additive`
- `neutral`
- `adverse`
- `inconclusive`
- `invalid`

For this slice specifically:

- if the base-threshold seam cannot be isolated from the separately admitted signal-adaptation cluster in the locked baseline, the row must be described as `invalid`

### Gates required

- `python -m pytest -q tests/integration/test_golden_trace_runtime_semantics.py::test_signal_adaptation_zone_overrides_base_thresholds tests/integration/test_golden_trace_runtime_semantics.py::test_signal_adaptation_missing_percentiles_locks_low_zone`
- manual provenance check that baseline summary + metrics + config source align with the frozen execution inputs above
- manual evidence review that canonical `evaluate_pipeline` provides `current_atr` and `atr_percentiles`
- manual evidence review that `select_candidate` uses zone `entry_conf_overall` to override `cfg.thresholds.entry_conf_overall` when adaptation is active

### Stop Conditions

- scope drift to any row other than `Base entry confidence seam`
- any requirement to neutralize `thresholds.signal_adaptation.*`
- any requirement to add a new CLI, runner, env-var, or config-authority surface
- inability to bind the assessment to the locked baseline provenance
- inability to record Base SHA, baseline hashes, or resolved effective-config hash in the manifest
- any gate failure
- locked baseline still shows a live signal-adaptation cluster that shadows `cfg.thresholds.entry_conf_overall` in the canonical route
- any attempt to rank multiple rows or turn the descriptive label into a direct action

### Output required

- one governance-safe resolution for `Base entry confidence seam`
- one descriptive classification using the locked Phase 5 vocabulary
- one report at `results/research/feature_attribution_v1/reports/fa_v1_base_entry_conf_20260331_01.md`
- one manifest at `results/research/feature_attribution_v1/manifests/fa_v1_base_entry_conf_20260331_01.json`

## Notes

This packet authorizes only the fourth identification slice.

It does not authorize:

- implementing a base-threshold neutralization
- re-scoping the signal-adaptation cluster
- introducing a generic attribution framework
- turning the descriptive result into implementation, removal, tuning, or promotion authority
