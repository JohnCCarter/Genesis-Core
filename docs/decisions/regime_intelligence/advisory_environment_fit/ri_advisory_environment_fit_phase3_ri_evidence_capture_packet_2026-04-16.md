# RI advisory environment-fit Phase 3 RI evidence-capture packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / bounded obs slice / fixed RI carrier / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded tmp-script capture on a fixed RI research carrier with approved research artifacts only; no `src/**`, `tests/**`, or `config/**` mutation.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** materialize a deterministic row-level RI evidence table for `2024` and `2025` on one fixed RI carrier, using only already exposed pre-entry RI observability plus a narrow raw-outcome join for later research use.
- **Candidate:** `RI advisory environment-fit Phase 3 evidence capture`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Repo skills invoked:** `python_engineering`, `genesis_backtest_verify`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_ri_evidence_capture_packet_2026-04-16.md`
  - `tmp/ri_advisory_environment_fit_capture_20260416.py`
  - `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/manifest.json`
  - `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/capture_summary.json`
  - `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/entry_rows.ndjson`
  - `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/closeout.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**` changes
  - any runtime/default/authority/family/admission change
  - any advisory score implementation
  - any label construction inside the capture slice
  - any ML/model work
  - any artifact write outside the approved output directory
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_ri_evidence_capture_packet_2026-04-16.md`
  - `tmp/ri_advisory_environment_fit_capture_20260416.py`
  - approved result artifacts under `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/`
- **Max files touched:** `6`

### Fixed evidence carrier

- **Carrier config:** `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- **Carrier discipline:** read-only
- **Carrier hash rule:** hash the carrier file before and after the run and record both hashes in `manifest.json`
- **Fail-closed rule:** if the capture requires carrier mutation, clarity backfill, config patching, or any `src/**` / `tests/**` change, the slice is inadmissible and must stop

### Years and surface discipline

- **Years:** `2024`, `2025`
- **Family:** `ri` only
- **Surface:** fixed runtime-valid RI bridge only
- **Not allowed:** legacy-family blending, threshold sweep, alternate carriers, or promotion framing

### Allowed pre-entry evidence columns

The evidence table may contain only already exposed pre-entry / entry-time observability fields from the fixed RI carrier surface, including:

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

If `ri_clarity_*` is absent on the carrier/runtime payload, the slice may only record that absence.
It may not reconstruct, simulate, or infer the missing clarity values.

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_ri_evidence_capture_packet_2026-04-16.md tmp/ri_advisory_environment_fit_capture_20260416.py`
- `pytest tests/backtest/test_regime_shadow_artifacts.py`
- `pytest tests/utils/test_decision_sizing.py::test_apply_sizing_composes_active_multipliers_and_exports_ri_state`
- `pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- bounded capture execution itself

### Stop Conditions

- any need to modify `src/**`, `tests/**`, or the carrier config
- any output write outside the approved results directory
- any ambiguous or non-deterministic join between capture rows and realized positions
- any attempt to derive labels or scores inside this slice
- any attempt to backfill missing `ri_clarity_*`
- any cache/log/config/runtime side effect outside the approved artifacts

### Output required

- one governance packet
- one bounded tmp capture script
- one manifest with carrier hashes and containment evidence
- one summary JSON with join assertions and field-coverage counts
- one NDJSON evidence table
- one closeout note stating what was captured, what remained absent, and what the next admissible step is

## Purpose

This slice answers one narrow question only:

> Can Genesis materialize a clean, fixed-carrier RI evidence table for later advisory research without pretending that labels or a deterministic baseline already exist?

The slice is therefore observational and infrastructural.
It is meant to create an admissible RI evidence surface — not to solve the advisory problem in one jump.

## Bottom line

This packet authorizes one bounded RI evidence-capture slice and nothing more.
If the fixed carrier does not expose some desired ingredients — especially `ri_clarity_*` — the slice must record that honestly and stop short of reconstruction or score authoring.
