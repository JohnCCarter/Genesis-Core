# SCPE RI V1 no-trade / min-dwell audit packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `active / bounded audit slice / research-only`
Skills used: `python_engineering`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — observational-only, summary-only, non-authoritative audit over unchanged replay outputs and diagnostics; no runtime/config/default/replay-root behavior change.
- **Required Path:** `Full`
- **Objective:** isolate the `RI_no_trade_policy` / `min_dwell` bottleneck by quantifying no-trade lock episodes, blocked exit attempts from no-trade, and descriptive state differences between blocked and successful exits using existing replay outputs only.
- **Candidate:** `SCPE RI V1 no-trade min-dwell audit`
- **Base SHA:** `9c145fbd`

### Scope

- **Scope IN:**
  - `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
  - `results/evaluation/scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json`
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
  - any change to the replay-root recommendation or semantics
  - any `.gitignore` relaxation
- **Expected changed files:**
  - `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
  - `results/evaluation/scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json`
- **Max files touched:** `4`

### Gates required

- `pre-commit run --files docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_packet_2026-04-20.md docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py results/evaluation/scpe_ri_v1_no_trade_min_dwell_audit_2026-04-20.json`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
- explicit first script smoke run evidence for `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py`
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py` with stable output hash proof
- explicit proof that `results/research/scpe_v1_ri/**` is unchanged before vs after both audit runs
- explicit proof that `scripts/analyze/scpe_ri_v1_no_trade_min_dwell_audit.py` does not import from `src/core/**`

### Stop Conditions

- Scope drift outside summary-only audit work
- Any need to regenerate or modify replay-root artifacts
- Any need to import from `src/core/**`
- Any attempt to reinterpret the audit as runtime-readiness or causal performance evidence
- Any discovery that the audit requires router logic changes rather than read-only analysis

### Output required

- one tracked audit script under `scripts/analyze/`
- one observational-only, summary-only, non-authoritative audit artifact under `results/evaluation/`
- one implementation report with exact commands and outcomes

## Audit questions

This slice evaluates whether observed no-trade persistence is concentrated around min-dwell-blocked exit attempts, and compares descriptive state differences between blocked exits from no-trade and successful exits from no-trade, using frozen replay outputs only. The slice is summary-only, observational, and non-authoritative; it does not alter replay semantics or recommendation state.

## Cohort definitions

- `blocked_exit_from_no_trade`
  - current selected policy remains `RI_no_trade_policy`
  - previous policy is `RI_no_trade_policy`
  - `switch_proposed = true`
  - `switch_blocked = true`
  - `switch_reason = switch_blocked_by_min_dwell`
- `successful_exit_from_no_trade`
  - previous policy is `RI_no_trade_policy`
  - current selected policy is not `RI_no_trade_policy`

All bucket differences in this slice are descriptive only. They must not introduce thresholds, pass/fail judgments, or recommendation updates.

The audit artifact must answer at minimum:

- How many no-trade segments exist, and what are their dwell-length statistics?
- Among rows with `previous_policy = RI_no_trade_policy`, how many are blocked exit attempts vs successful exits vs quiet stays?
- How often is `switch_blocked_by_min_dwell` the blocker when the system is sitting in no-trade?
- What state differences appear between blocked no-trade exits and successful releases from no-trade?
- Is no-trade lock-in concentrated in specific confidence / clarity / edge / transition buckets?

## Non-claims explicitly forbidden

The audit artifact may **not** claim any of the following:

- runtime readiness
- live-execution improvement
- backtest-integrated edge improvement
- approval for threshold changes
- approval for router policy changes
- causal performance improvement
