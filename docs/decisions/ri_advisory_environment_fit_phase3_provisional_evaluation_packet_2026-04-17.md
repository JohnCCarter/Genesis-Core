# RI advisory environment-fit Phase 3 provisional evaluation packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded exploratory proxy evaluation / results-only / default unchanged`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded research-only exploratory proxy evaluation on already captured RI evidence with outputs confined to `results/**`; no runtime/default/authority changes.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** test whether the RI selector surface shows any bounded exploratory structure against explicitly provisional realized-outcome proxies, without claiming Phase 2 supportive/hostile fidelity.
- **Candidate:** `RI advisory environment-fit Phase 3 provisional evaluation`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`

### Scope

- **Scope IN:**
  - `docs/decisions/ri_advisory_environment_fit_phase3_provisional_evaluation_packet_2026-04-17.md`
  - one bounded research script under `tmp/`
  - one results directory under `results/research/ri_advisory_environment_fit/`
  - one deterministic evaluation memo under `docs/analysis/`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - runtime authority changes
  - default behavior changes
  - any exact Phase 2 supportive/hostile claim
  - any contradiction-year validation claim presented as Phase 2-faithful
  - any full role-map or `market_fit_score` claim
  - ML/model work
- **Expected changed files:**
  - this packet
  - one `tmp/` script
  - one `docs/analysis/` memo
  - results artifacts confined to one new result subdirectory
- **Max files touched:** `8`

### Fixed evidence source

- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- label-gap boundary source:
  - `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- provisional boundary SSOT:
  - `docs/analysis/ri_advisory_environment_fit_phase3_provisional_evaluation_admissibility_2026-04-17.md`

The label-gap memo is a governance boundary source only.
It is not a runtime input, generated data dependency, or score input surface for this slice.

### Allowed score-like outputs

This slice may emit only exploratory, explicitly provisional diagnostics such as:

- `decision_reliability_rank`
- `transition_proxy_rank`
- bucketed exploratory summaries against provisional realized-outcome proxies

These outputs are not labels, not runtime signals, and not Phase 2 supportive/hostile claims.

### Allowed scoring-time inputs

Only the already-audited selector subset may be consumed:

- `ri_clarity_score`
- `ri_clarity_raw`
- `bars_since_regime_change`
- `proba_edge`
- `conf_overall`
- `decision_size`
- `htf_regime`
- `zone`
- `action`
- `side`

### Allowed provisional realized-outcome proxies

Only the following raw realized-outcome columns may be used for exploratory evaluation surfaces in this slice:

- `mfe_16_atr`
- `continuation_score`
- `fwd_16_atr`

These fields are proxies only.
They must not be renamed, bucketed, or claimed as exact supportive/hostile labels.
They are only provisional, descriptive observation surfaces for exploratory RI-selector evaluation.
They must not be mapped, signed, thresholded, or aggregated into supportive/hostile label substitutes, Phase 2 equivalence, or contradiction-year proof.

### Explicitly forbidden realized-outcome shortcuts

- raw `total_pnl` sign as a supportive/hostile substitute
- any reconstruction of `pnl_delta`
- any synthetic `active_uplift_cohort_membership`
- any contradiction-year pass/fail claim presented as Phase 2-faithful evaluation

### Required outputs

- one selector-consumption artifact showing the exact consumed input columns
- one provisional-proxy artifact showing the exact realized-outcome proxies used
- one allowlist manifest recording `selector_fields_used` and `proxy_fields_used`, with explicit subset checks against the packet allowlists
- one exploratory year-by-year bucket summary
- one memo stating whether the provisional diagnostics show any bounded structure worth further research
- one explicit statement that the slice did not evaluate the exact Phase 2 supportive/hostile contract

### Gates required

- `pre-commit run --files <packet> <tmp script> <analysis memo>`
- `pytest tests/backtest/test_runner_direct_includes_merged_config.py`
- `pytest tests/backtest/test_backtest_engine.py::test_engine_run_skip_champion_merge_does_not_load_champion`
- `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- bounded execution of the provisional-evaluation script itself
- bounded smoke/assert proof that `selector_fields_used` and `proxy_fields_used` are subsets of the packet allowlists

### Stop Conditions

- any attempt to rename exploratory proxies as supportive/hostile labels
- any use of `total_pnl` sign as a label shortcut
- any need for reconstructed `pnl_delta`, synthetic `active_uplift_cohort_membership`, or other derived label authority to continue the slice, in which case the run must stop as `BLOCKED_PROXY_AUTHORITY_DRIFT`
- any claim that the slice validated the Phase 2 failure taxonomy
- any runtime-facing recommendation, candidate-promotion framing, or contradiction-year-proof claim
- any attempt to move logic into runtime code
- any output write outside approved `tmp/`, `results/`, or docs surfaces
- any touch to `src/**`, `tests/**`, `config/**`, or runtime defaults/config semantics
- any need to touch `src/core/**`, `config/**`, or shared production-near evaluation helpers, which requires a new packet and pre-code review

## Bottom line

This packet proposes one narrow next step only:

- perform exploratory proxy evaluation on the RI selector surface while remaining explicit that the exact Phase 2 label contract is still unresolved

It does not authorize label substitution, contradiction-year proof, or runtime-facing score implementation.
