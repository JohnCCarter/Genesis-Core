# Execution proxy missingness-cause slice — packet

Date: 2026-04-14
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / implementation / no-runtime-authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: this slice deepens read-only execution evidence over locked traces; the primary risk is over-interpreting proxy missingness as execution authority. Runtime/default behavior must remain unchanged.
- **Required Path:** `Lite`
- **Objective:** Add deterministic read-only missingness-pattern diagnostics for incomplete execution-proxy windows so incomplete cohorts can be separated by observed trace-coverage pattern without changing runtime strategy code, trace production, or locked research artifacts.
- **Candidate:** `baseline_current` execution proxy missingness-cause evidence lane
- **Base SHA:** `8e23ddb4`

### Scope

- **Scope IN:**
  - `docs/decisions/diagnostic_campaigns/execution_proxy_missingness_cause_packet_2026-04-14.md`
  - `scripts/analyze/execution_proxy_evidence.py`
  - `tests/backtest/test_execution_proxy_evidence.py`
- **Scope OUT:**
  - all files under `src/`
  - all files under `config/`
  - all files under `results/`
  - all files under `tmp/`
  - any runtime/config authority changes
  - any edits to locked Phase 10–14 artifacts
  - any trace regeneration or backtest reruns as part of the diff itself
  - `scripts/analyze/edge_origin_isolation.py`
  - `tests/backtest/test_edge_origin_isolation.py`
  - `config/strategy/champions/**`
  - `.github/workflows/champion-freeze-guard.yml`
  - family-rule / promotion / readiness / comparison surfaces
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/execution_proxy_missingness_cause_packet_2026-04-14.md`
  - `scripts/analyze/execution_proxy_evidence.py`
  - `tests/backtest/test_execution_proxy_evidence.py`
- **Max files touched:** `3`

### Constraints

- no runtime behavior change
- no edits to locked report/classification artifacts
- the lane must remain observational only and must not claim realized fill quality, slippage, latency, queue position, or venue authority
- the new diagnostics may classify coverage/missingness patterns only from packet-attested fields already present on locked traces
- default repository behavior must remain unchanged; this lane is additive and invoked explicitly
- missingness-pattern labels must fail closed to descriptive proxy-missingness classes; no inferred market microstructure claims without attested evidence
- if an input fact needed for classification is absent, the script must emit an observational omission/boundary class rather than infer unstated execution semantics
- these classes are observational trace-coverage labels only. They describe where proxy-price rows are absent relative to the requested proxy window and the available trace boundary, and do not imply realized execution quality, slippage, latency, liquidity, venue behavior, or any other unattested market mechanism.

### Packet-authorized source surface

The implementation may rely only on already attested trace fields used read-only:

- `trade_signatures.entry_timestamp`
- `trade_signatures.exit_timestamp`
- `trade_signatures.side`
- `trade_signatures.size`
- `trade_signatures.pnl`
- `trace_rows.bar_index`
- `trace_rows.timestamp`
- `trace_rows.fib_phase.ltf_debug.price`

### Authorized outputs

The updated script may emit only deterministic observational diagnostics such as:

- whether the proxy window reaches the final trace bar
- whether missing proxy-price bars include the exit bar
- whether missing proxy-price bars are boundary-like or interior-like
- summary counts of missingness-pattern classes over the same proxy population

The script must not emit or imply:

- realized execution price attestation
- slippage or latency attestation
- causal proof that execution inefficiency is supported or rejected
- claims about venue behavior beyond coverage/missingness structure

### Gates required

- file-scoped `pre-commit` on changed files
- targeted `pytest` for `tests/backtest/test_execution_proxy_evidence.py`
- CLI smoke test for `scripts/analyze/execution_proxy_evidence.py`
- determinism replay via `audit_execution_proxy_determinism.json.match = true`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`

### Skill usage

- repo-local governance specs reviewed:
  - `.github/skills/python_engineering.json`
  - `.github/skills/ri_off_parity_artifact_check.json` (discipline reference only; not a replacement for packet gates)
  - `.github/skills/feature_parity_check.json` (discipline reference only; not a replacement for packet gates)

### Stop Conditions

- scope drift outside the three files above
- any need to touch runtime-default authority or family/champion surfaces
- any wording that upgrades proxy diagnostics into execution authority
- determinism mismatch across same-input replays
- any classification rule that depends on unattested fields or speculative market-state inference

### Output required

- implementation diff for the proxy script and tests
- validation report with exact commands/selectors run
- residual-risk note clarifying that cause classes still describe proxy missingness only

## Bottom line

This slice should answer a narrower question than the prior partition read: whether the positive execution-like signal sits in boundary-like missingness, interior missingness, or mixed incomplete cohorts. It must do so without changing runtime code or overstating proxy evidence into execution authority.
