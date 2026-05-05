# Execution proxy evidence implementation — packet

Date: 2026-04-02
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / implementation / no-runtime-authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: this slice expands read-only research analysis over locked traces and can overclaim execution authority if proxy-path semantics are vague; runtime behavior must remain unchanged.
- **Required Path:** `Lite`
- **Objective:** Implement a separate read-only execution-proxy analysis lane that derives deterministic proxy price-path evidence from already attested trace-row price context without modifying runtime strategy code, locked Phase 10 outputs, or trace-production logic.
- **Candidate:** `baseline_current` execution-proxy evidence lane
- **Base SHA:** `5661f025`

### Scope

- **Scope IN:**
  - `docs/decisions/diagnostic_campaigns/execution_proxy_evidence_impl_packet_2026-04-02.md`
  - `scripts/analyze/execution_proxy_evidence.py`
  - `tests/backtest/test_execution_proxy_evidence.py`
- **Scope OUT:**
  - all files under `src/`
  - all files under `config/`
  - all files under `results/`
  - any runtime/config authority changes
  - any edits to locked Phase 10–14 artifacts
  - any trace regeneration or backtest reruns
  - any mutation of `scripts/analyze/edge_origin_isolation.py`
  - any mutation of `tests/backtest/test_edge_origin_isolation.py`
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/execution_proxy_evidence_impl_packet_2026-04-02.md`
  - `scripts/analyze/execution_proxy_evidence.py`
  - `tests/backtest/test_execution_proxy_evidence.py`
- **Max files touched:** `3`

### Constraints

- no runtime behavior change
- no edits to locked report/classification artifacts
- the new lane must remain observational only and must not claim realized fill quality, slippage, or latency authority
- this lane produces proxy price-path evidence only from authorized trace-row fields; it does not attest realized execution price, slippage, latency, queue position, or causal support/rejection of execution inefficiency
- this tooling produces deterministic proxy evidence from attested trace observations only; it does not assert realized execution fills or execution authority
- proxy calculations may use only packet-attested fields already present on locked traces
- if a required proxy field is missing, the script must fail closed rather than infer from unstated assumptions
- default repository behavior must remain unchanged; this lane is additive and invoked explicitly

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

### Authorized proxy outputs

The new script may compute only deterministic proxy surfaces such as:

- proxy entry price from the joined entry row price
- proxy exit price from the exactly resolved exit row price
- proxy holding-window min/max price path over the inclusive entry-to-exit bar window using only attested row-price observations
- proxy MAE/MFE measured against the proxy entry price and the observed side
- fixed-horizon proxy exit summaries for packet-declared horizons using the same row-price surface

The script must not emit or imply:

- realized execution price attestation
- slippage attestation
- latency attestation
- queue-position attestation
- causal proof that execution_inefficiency is supported or rejected

### Gates required

- file-scoped `pre-commit` on changed files
- targeted pytest for the new test file
- CLI smoke test for the new script
- determinism replay for the new script outputs
- `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Skill Usage

- Repo-local skill anchor applied for artifact-discipline posture:
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skill usage here is governance-only and does not replace the declared gates.

### Stop Conditions

- scope drift outside the three files above
- any need to modify runtime code or locked artifacts
- any proxy calculation that requires unattested OHLC/high-low or realized fill fields
- determinism mismatch across same-input replays
- any wording that upgrades proxy evidence into execution authority

### Output required

- implementation diff for the new script and tests
- validation report with exact selectors run
- explicit residual-risk note that proxy execution evidence is still weaker than realized fill evidence

## Bottom line

This slice does not solve `execution_inefficiency` conclusively.
It adds the smallest admissible execution-proxy lane that can reduce uncertainty without touching runtime or rewriting the locked Phase 10 surface.
