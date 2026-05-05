# SCPE RI V1 router diagnostics packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `active / bounded diagnostics slice / research-only`
Skills used: `python_engineering`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — summary-only diagnostics over existing frozen replay outputs; no runtime/config/default/replay-root behavior change.
- **Risk:** `MED` — observational-only, summary-only, non-authoritative diagnostics over existing frozen replay outputs; no runtime/config/default/replay-root behavior change.
- **Required Path:** `Full`
- **Objective:** materialize one bounded diagnostic surface that explains why the SCPE RI V1 replay still lands on `NEEDS_REVISION`, focusing on policy distinctness evidence, switch-block decomposition, and veto/no-trade dominance using existing replay outputs only.
- **Candidate:** `SCPE RI V1 router diagnostics`
- **Base SHA:** `92a47512`

### Scope

- **Scope IN:**
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_diagnostics_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_diagnostics_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_router_diagnostics.py`
  - `results/evaluation/scpe_ri_v1_router_diagnostics_2026-04-20.json`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - `tmp/**`
  - `results/research/**`
  - any runtime integration
  - any backtest execution integration
  - any cross-family routing
  - any replay-router logic changes
  - any change to `recommendation = NEEDS_REVISION` in the existing replay outputs
  - any `.gitignore` relaxation
- **Expected changed files:**
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_router_diagnostics_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_diagnostics_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_router_diagnostics.py`
  - `results/evaluation/scpe_ri_v1_router_diagnostics_2026-04-20.json`
- **Max files touched:** `4`

### Gates required

- `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_router_diagnostics_packet_2026-04-20.md docs/analysis/scpe_ri_v1/scpe_ri_v1_router_diagnostics_report_2026-04-20.md scripts/analyze/scpe_ri_v1_router_diagnostics.py results/evaluation/scpe_ri_v1_router_diagnostics_2026-04-20.json`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_router_diagnostics.py`
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_router_diagnostics.py` with stable output hash proof for the diagnostics artifact
- explicit proof that `results/research/scpe_v1_ri/**` is unchanged before vs after both diagnostics runs
- explicit proof that `scripts/analyze/scpe_ri_v1_router_diagnostics.py` does not import from `src/core/**`

### Stop Conditions

- Scope drift outside summary-only diagnostics
- Any need to edit or regenerate `results/research/scpe_v1_ri/**`
- Any need to import from `src/core/**`
- Any attempt to reinterpret observational diagnostics as runtime-readiness or causal performance evidence
- Any attempt to reinterpret observational diagnostics as runtime-readiness or causal performance evidence
- Any attempt to change, reinterpret, or upgrade the replay-root `NEEDS_REVISION`, policy semantics, selector semantics, or routing thresholds
- Any discovery that the diagnostics require replay-router logic changes instead of read-only analysis
- Missing, drifted, or inconsistent required fields in replay artifacts; the script must fail closed rather than infer or backfill

### Output required

- one tracked diagnostics script under `scripts/analyze/`
- one observational-only, summary-only, non-authoritative diagnostics artifact under `results/evaluation/`
- one implementation report with exact commands and outcomes

## Slice rationale

The replay has already proven determinism and preserved routing parity, but the roadmap still has two unresolved research questions:

1. Is policy distinctness materially weak because the defensive policy is under-supported?
2. Are blocked switches and no-trade outcomes primarily caused by explicit router stability controls, by downstream veto, or by the router selecting no-trade directly?

This slice exists to answer those questions without changing replay outputs or widening scope beyond diagnostics.

The diagnostics artifact is observational-only, summary-only, and non-authoritative. It must not replace the replay-root artifacts, and it must not be used to change router policy, router thresholds, or recommendation state.

## Diagnostics questions

The diagnostics artifact must answer at minimum:

- How many rows, trades, and veto interventions occur per selected policy?
- How often is `RI_no_trade_policy` selected directly versus no-trade being forced by downstream veto on another policy?
- What fraction of blocked switches come from `min_dwell`, `confidence_below_threshold`, or other explicit switch reasons?
- Does the defensive policy show distinct state characteristics even if its sample is sparse?
- Is veto dominance concentrated in specific policies or states?

## Non-claims explicitly forbidden

The diagnostics artifact may **not** claim any of the following:

- runtime readiness
- live-execution improvement
- backtest-integrated edge improvement
- cross-family superiority
- causal performance improvement
- approval for router threshold changes
