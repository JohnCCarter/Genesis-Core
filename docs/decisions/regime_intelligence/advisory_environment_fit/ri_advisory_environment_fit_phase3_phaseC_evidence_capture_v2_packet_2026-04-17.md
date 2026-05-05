# RI advisory environment-fit Phase 3 phaseC evidence capture v2 packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / bounded obs slice / non-runtime evidence bundle / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded tmp-script capture on a frozen non-runtime evidence bundle with approved results only; no `src/**`, `tests/**`, `config/**`, or `artifacts/**` mutation.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** materialize a deterministic row-level RI evidence table for `2024` and `2025` using the frozen Phase C evidence bundle as the research-only config source.
- **Candidate:** `RI advisory environment-fit Phase 3 evidence capture v2`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_evidence_capture_v2_packet_2026-04-17.md`
  - `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
  - `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/closeout.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**` mutation
  - any runtime/default/authority/family/admission change
  - any label construction or baseline implementation
  - any ML/model work
  - any write outside the approved results directory
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_evidence_capture_v2_packet_2026-04-17.md`
  - `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`
  - approved result artifacts under `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/`
- **Max files touched:** `6`

### Fixed evidence source

- **Bundle path:** `artifacts/bundles/ri_advisory_environment_fit/phase3_phasec_evidence_freeze_2026-04-17/phaseC_oos_evidence_bundle.json`
- **Ledger path:** `artifacts/research_ledger/artifacts/ART-2026-0001.json`
- **Config source:** `non_runtime_evidence_bundle`
- **Bundle discipline:** read-only
- **Bundle hash rule:** hash the bundle before and after the run and record both hashes in `manifest.json`
- **Fail-closed rule:** if capture requires mutating the bundle, ledger record, or any `artifacts/**` file, the slice is inadmissible and must stop

### Execution discipline

- Use `bundle.evidence_payload.merged_config` directly as research/backtest input
- Do not route the bundle payload through `ConfigAuthority.validate`
- If `meta.skip_champion_merge` is absent, inject only that flag in memory and record that it was injected
- Do not write the injected config anywhere on disk

### Years and surface discipline

- **Years:** `2024`, `2025`
- **Family:** `ri` only
- **Surface:** frozen Phase C evidence bundle only
- **Not allowed:** legacy-family blending, threshold sweep, alternate donors, promotion framing, runtime-valid carrier creation

### Allowed pre-entry evidence columns

The evidence table may contain only already exposed pre-entry / entry-time observability fields from the evidence-bundle-driven RI surface, including:

- join metadata: `year`, `join_key`, `position_id`, `entry_time`, `exit_time`, `side`
- regime context: authoritative regime, shadow regime, mismatch, `authority_mode`, `authority_mode_source`, `htf_regime`
- RI state: `ri_flag_enabled`, `ri_version`, `ri_clarity_enabled`, `ri_clarity_score`, `ri_clarity_raw`, `ri_risk_state_*`, `bars_since_regime_change`, `last_regime`
- decision/probability context: `action`, `proba_*`, `conf_*`, `decision_size`
- bounded context helpers already present in payloads: `zone`, `current_atr_used`, `atr_period_used`

### Allowed raw outcome columns

The evidence table may include only the following raw realized outcome columns, and only as raw evidence:

- `total_pnl`
- `total_size`
- `total_commission`
- `entry_atr`
- `fwd_4_atr`
- `fwd_8_atr`
- `fwd_16_atr`
- `mfe_16_atr`
- `mae_16_atr`
- `continuation_score`

These columns are allowed **only** as raw realized evidence.
They must not be converted into labels, scores, buckets, runtime inputs, or backfilled features in this slice.

### Deterministic join contract

The script must use one explicit deterministic join key:

- `join_key = normalize(entry_time) + "|" + side`

Required assertions:

1. every realized position row must map to exactly one captured entry row
2. duplicate position join keys must fail the run
3. duplicate capture join keys must fail the run
4. unmatched realized positions must be reported and fail the run
5. extra captured entry rows with no realized position may be reported in summary, but must not be silently coalesced into realized evidence rows

### Explicit non-authorizations

This packet does **not** authorize:

- advisory score implementation
- supportive / hostile / transition label construction
- runtime or shadow authority changes
- clarity reconstruction or synthetic backfill when `ri_clarity_*` is absent
- any claim of promotion readiness
- any persisted mutation of bundle payload or ledger metadata

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_evidence_capture_v2_packet_2026-04-17.md tmp/ri_advisory_environment_fit_capture_v2_20260417.py`
- `pytest tests/backtest/test_regime_shadow_artifacts.py`
- `pytest tests/utils/test_decision_sizing.py::test_apply_sizing_composes_active_multipliers_and_exports_ri_state`
- `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `pytest tests/backtest/test_backtest_engine.py::test_engine_run_skip_champion_merge_does_not_load_champion`
- `pytest tests/backtest/test_runner_direct_includes_merged_config.py`
- `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- bounded capture execution itself

### Stop Conditions

- any need to mutate bundle payload or ledger record
- any need to inject `strategy_family` into donor payload
- any output write outside the approved results directory
- any ambiguous or non-deterministic join between capture rows and realized positions
- any attempt to derive labels or scores inside this slice
- any cache/log/config/runtime side effect outside the approved results directory and previously allowed repo surfaces

### Output required

- one governance packet
- one bounded tmp capture script
- one manifest with bundle hashes and containment evidence
- one summary JSON with join assertions and field-coverage counts
- one NDJSON evidence table
- one closeout note stating what was captured, what remained absent, and what the next admissible step is

## Purpose

This slice answers one narrow question only:

> Can Genesis materialize a clean, evidence-bundle-driven RI evidence table for later advisory research without pretending that labels or a deterministic baseline already exist?

The slice is observational and infrastructural.
It is meant to create a richer admissible RI evidence surface — not to solve the advisory problem in one jump.

## Bottom line

This packet authorizes one bounded RI evidence-capture v2 slice and nothing more.
If the frozen evidence bundle still fails to expose the desired ingredients cleanly, the slice must record that honestly and stop short of label or baseline authoring.
