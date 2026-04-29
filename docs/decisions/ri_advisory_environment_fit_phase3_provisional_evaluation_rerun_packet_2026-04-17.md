# RI advisory environment-fit Phase 3 provisional evaluation rerun packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded exploratory proxy rerun / results-only / default unchanged`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded research-only rerun of the provisional evaluation on a restored proxy surface; outputs confined to `tmp/`, `results/`, and one memo; no runtime/default/authority changes.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** rerun the bounded exploratory proxy evaluation on the restored Phase C proxy surface to determine whether the RI selector surface shows any bounded year-by-year structure once provisional proxy coverage exists.
- **Candidate:** `RI advisory environment-fit Phase 3 provisional evaluation rerun`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

### Scope

- **Scope IN:**
  - `docs/decisions/ri_advisory_environment_fit_phase3_provisional_evaluation_rerun_packet_2026-04-17.md`
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

- selector source:
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- restored proxy source:
  - `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/materialized_proxy_rows.ndjson`
  - `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/proxy_surface.json`
  - `results/research/ri_advisory_environment_fit/phase3_proxy_coverage_audit_2026-04-17/manifest.json`
- label-boundary source:
  - `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- provisional boundary SSOT:
  - `docs/analysis/ri_advisory_environment_fit_phase3_proxy_coverage_audit_2026-04-17.md`

The label-gap memo is governance boundary context only.
Executable boundary checks for this rerun must come from the restored proxy audit manifest,
not from any standalone `label_surface_audit.json` artifact.

### Join contract

The rerun must materialize one joined exploratory surface by combining:

- selector rows from capture-v2, and
- restored proxy rows from the proxy-coverage audit

Required deterministic join rules:

1. join key must remain `join_key`
2. no fuzzy, fallback, many-to-one, or one-to-many joins are allowed
3. duplicate selector join keys must fail the run
4. duplicate restored-proxy join keys must fail the run
5. selector rows without a restored proxy row may be reported, but must not be silently assigned synthetic proxy values
6. restored proxy rows without a selector row must fail the run
7. joined exploratory row count must exactly equal the restored proxy `materialized_row_count` recorded in `phase3_proxy_coverage_audit_2026-04-17/manifest.json`
8. if any allowlisted proxy field is unexpectedly null after the exact join, the run must stop and record the null-count evidence explicitly rather than continue silently

### Allowed score-like outputs

This slice may emit only exploratory, explicitly provisional diagnostics such as:

- `decision_reliability_rank`
- `transition_proxy_rank`
- bucketed exploratory summaries against restored realized-outcome proxies

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

Only the restored proxy fields may be used for exploratory evaluation surfaces in this slice:

- `mfe_16_atr`
- `continuation_score`
- `fwd_16_atr`

These fields remain proxies only.
They must not be renamed, bucketed, or claimed as exact supportive/hostile labels.
They must not be mapped, signed, thresholded, or aggregated into supportive/hostile label substitutes, Phase 2 equivalence, or contradiction-year proof.

### Explicitly forbidden realized-outcome shortcuts

- raw `total_pnl` sign as a supportive/hostile substitute
- any reconstruction of `pnl_delta`
- any synthetic `active_uplift_cohort_membership`
- any contradiction-year pass/fail claim presented as Phase 2-faithful evaluation

### Required outputs

- one selector-consumption artifact showing the exact consumed input columns
- one provisional-proxy artifact showing the exact restored realized-outcome proxies used
- one allowlist manifest recording `selector_fields_used` and `proxy_fields_used`, with explicit subset checks against the packet allowlists
- one join-audit artifact stating selector rows, restored proxy rows, matched joined rows, unmatched-left, unmatched-right, duplicate-key counts, any coverage shortfall, and null counts per allowlisted proxy field
- one exploratory year-by-year bucket summary
- one memo stating whether the provisional diagnostics now show bounded structure worth further research
- one explicit statement that the slice still did not evaluate the exact Phase 2 supportive/hostile contract

### Gates required

- `pre-commit run --files <packet> <tmp script> <analysis memo>`
- `pytest tests/backtest/test_runner_direct_includes_merged_config.py`
- `pytest tests/backtest/test_backtest_engine.py::test_engine_run_skip_champion_merge_does_not_load_champion`
- `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- bounded execution of the provisional-evaluation rerun script itself
- deterministic replay of the rerun script on identical inputs with stable summary/hash output
- join-audit proof artifact confirming exact fail-closed join counts before any bucket summary is emitted
- bounded smoke/assert proof that `selector_fields_used` and `proxy_fields_used` are subsets of the packet allowlists

### Stop Conditions

- any attempt to rename exploratory proxies as supportive/hostile labels
- any use of `total_pnl` sign as a label shortcut
- any need for reconstructed `pnl_delta`, synthetic `active_uplift_cohort_membership`, or other derived label authority to continue the slice, in which case the run must stop as `BLOCKED_PROXY_AUTHORITY_DRIFT`
- any output text, column name, or conclusion implying that restored proxy fields replace, approximate, or recover the exact Phase 2 label authority
- any claim that the slice validated the Phase 2 failure taxonomy
- any runtime-facing recommendation, candidate-promotion framing, or contradiction-year-proof claim
- any attempt to move logic into runtime code
- any output write outside approved `tmp/`, `results/`, or docs surfaces
- any touch to `src/**`, `tests/**`, `config/**`, or runtime defaults/config semantics
- any need to touch `src/core/**`, `config/**`, or shared production-near evaluation helpers, which requires a new packet and pre-code review
- any manifest evidence that `label_gap_still_blocked` is no longer true on the restored proxy source without a separate admissibility review

## Bottom line

This packet proposes one narrow next step only:

- rerun exploratory proxy evaluation on the RI selector surface now that provisional proxy coverage has been restored under audited observational guardrails

It does not authorize label substitution, contradiction-year proof, or runtime-facing score implementation.
