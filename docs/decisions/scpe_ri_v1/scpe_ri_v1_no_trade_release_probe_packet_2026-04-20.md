# SCPE RI V1 no-trade release probe packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `active / bounded release-probe slice / research-only`
Skills used: `python_engineering`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — observational-only, summary-only, non-authoritative release-probe over unchanged replay outputs and prior audit artifacts; no runtime/config/default/replay-root behavior change.
- **Required Path:** `Full`
- **Objective:** probe whether blocked exits from `RI_no_trade_policy` already sit inside the descriptive state envelope of successful releases from no-trade, using frozen replay outputs only.
- **Candidate:** `SCPE RI V1 no-trade release probe`
- **Base SHA:** `c73f61a1`

### Scope

- **Scope IN:**
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_no_trade_release_probe_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_probe_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
  - `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - `tmp/**`
  - `results/research/**`
  - any runtime integration
  - any replay-router logic changes
  - any threshold changes
  - any change to replay recommendation state or semantics
  - any `.gitignore` relaxation
- **Expected changed files:**
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_no_trade_release_probe_packet_2026-04-20.md`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_probe_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
  - `results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
- **Max files touched:** `4`

### Gates required

- `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_no_trade_release_probe_packet_2026-04-20.md docs/analysis/scpe_ri_v1/scpe_ri_v1_no_trade_release_probe_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_release_probe.py results/evaluation/scpe_ri_v1_no_trade_release_probe_2026-04-20.json`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
- explicit first smoke run of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_probe.py`
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_release_probe.py` with stable output hash proof
- explicit replay-root immutability proof that `results/research/scpe_v1_ri/**` is unchanged before vs after both probe runs
- explicit proof that `scripts/analyze/scpe_ri_v1_no_trade_release_probe.py` does not import from `src/core/**`

### Stop Conditions

- Scope drift outside summary-only release-probe work
- Any need to regenerate or modify replay-root artifacts
- Any need to import from `src/core/**`
- Any attempt to interpret the probe as runtime-readiness or causal performance evidence
- Any attempt to treat heuristic release-envelope matches as approved semantics changes

### Output required

- one tracked release-probe script under `scripts/analyze/`
- one observational-only, summary-only, non-authoritative probe artifact under `results/evaluation/`
- one implementation report with exact commands and outcomes

## Probe framing

This slice is observational-only, summary-only, and non-authoritative. It does not alter replay semantics or recommendation state.

This probe is descriptive and observational only. It measures how many blocked `no_trade` release attempts fall inside the frozen `successful_exit_from_no_trade` cohort's observed categorical and numeric support envelope; it does not establish permissibility, routing defect, threshold change, or recommendation-state change.

The probe uses descriptive support envelopes derived from the frozen `successful_exit_from_no_trade` cohort only. These envelopes are heuristic evidence-shaping aids, not authority surfaces, and they must not be used directly as router thresholds.

The prior no-trade / min-dwell audit artifact is used only as a frozen count-consistency cross-check for the blocked/successful cohort sizes; it is not a policy authority surface and must not be used as proof of router correctness.

Inside-envelope means descriptive overlap only, not “should have released”.

## Probe method

- categorical envelope = observed bucket membership present in the frozen successful-release cohort
- numeric envelope = observed min/max numeric range plus robust descriptive summaries from the frozen successful-release cohort
- overlap is descriptive only and must not be interpreted as a policy defect judgment or a recommendation update

## Cohort definitions

- `blocked_exit_from_no_trade`
  - `previous_policy = RI_no_trade_policy`
  - `selected_policy = RI_no_trade_policy`
  - `switch_proposed = true`
  - `switch_blocked = true`
  - `switch_reason = switch_blocked_by_min_dwell`
- `successful_exit_from_no_trade`
  - `previous_policy = RI_no_trade_policy`
  - `selected_policy != RI_no_trade_policy`

## Probe questions

The probe artifact must answer at minimum:

- What categorical state buckets appear in the successful no-trade release cohort?
- How many blocked no-trade exits already sit inside that categorical support envelope?
- How many blocked no-trade exits also sit inside the observed min/max numeric envelope of successful exits?
- How many blocked no-trade exits are at or above the successful-release medians for clarity, confidence, and edge?
- Do the results support a future packeted semantics-revision test, without claiming that such a revision would improve outcomes?

## Non-claims explicitly forbidden

The probe artifact may **not** claim any of the following:

- runtime readiness
- live-execution improvement
- backtest-integrated edge improvement
- approval for router threshold changes
- approval for router semantics changes
- causal performance improvement
