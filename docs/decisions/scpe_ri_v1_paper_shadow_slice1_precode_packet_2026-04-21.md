# SCPE RI V1 paper-shadow slice1 pre-code packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded paper-shadow bridge / dry-run-only / default-off / no order authority`

This document defines the next bounded implementation-adjacent slice after the completed runtime-observability lane.
It remains in `RESEARCH`, preserves `NO BEHAVIOR CHANGE`, and stays explicitly below paper approval, live-paper execution, runtime-config/default authority, readiness, cutover, and promotion semantics.
It is `precode-only / candidate-only` and does **not** by itself authorize implementation, operations, readiness, promotion, or live-paper use.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `HIGH` — bounded paper-runner work remains dry-run-only and observational, but it is adjacent to execution-path code and therefore must be treated as operationally sensitive even without order authority.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** allow `scripts/paper_trading_runner.py` to explicitly request the already-existing `meta["observability"]["scpe_ri_v1"]` payload in dry-run mode only and emit a bounded runner-side observational summary, without changing order submission, runtime-config/default authority, or live-paper semantics.
- **Candidate:** `SCPE RI paper-shadow slice1 runner bridge`
- **Base SHA:** `56e680ec`

### Skill Usage

- Repo-local `paper_runner_ops` applies to this execution-adjacent runner surface as fail-fast and drift-discipline guardrail, even though this slice remains dry-run-only and below operations approval.
- Repo-local `python_engineering` applies to the future bounded Python implementation and test work.
- `repo_clean_refactor` may be used only as future scope/minimal-diff discipline.
- No exact repo-local skill matches governance-packet authoring itself; any dedicated governance-packet skill remains `föreslagen`, not `införd`.

### Done criteria

- the paper runner exposes one explicit default-OFF CLI opt-in for SCPE RI paper-shadow
- the opt-in is accepted only in dry-run mode and is rejected fail-fast for `--live-paper`
- without the opt-in, outbound `/strategy/evaluate` payloads remain unchanged
- with the opt-in, the runner may request only `state["observability"]["scpe_ri_v1"] = true`
- the runner may consume/log only the already allowlisted RI observability fields
- no order submission path, quarantine path, watchdog path, runtime-config/default-authority path, or live-paper semantics change
- all listed gates pass and the implementation report records exact outcomes

### Scope

- **Scope IN:**
  - `docs/decisions/scpe_ri_v1_paper_shadow_slice1_precode_packet_2026-04-21.md`
  - `scripts/paper_trading_runner.py`
  - `tests/integration/test_paper_trading_runner.py`
  - `docs/analysis/scpe_ri_v1_paper_shadow_slice1_implementation_report_2026-04-21.md`
- **Scope OUT:**
  - all edits under `src/**`, `config/**`, `results/**`, `artifacts/**`
  - `tests/backtest/**` edits
  - `tests/integration/test_ui_endpoints.py` edits
  - `docs/paper_trading/runner_deployment.md`
  - `docs/paper_trading/phase3_runbook.md`
  - `scripts/paper_trading_runner.py` live-paper order-submission logic
  - any runtime-config/default-authority surface
  - any paper approval, live-paper approval, readiness, cutover, launch, deployment, or promotion semantics
- **Expected changed files:**
  - `docs/decisions/scpe_ri_v1_paper_shadow_slice1_precode_packet_2026-04-21.md`
  - `scripts/paper_trading_runner.py`
  - `tests/integration/test_paper_trading_runner.py`
  - `docs/analysis/scpe_ri_v1_paper_shadow_slice1_implementation_report_2026-04-21.md`
- **Max files touched:** `4`

### Citation-only seam references

The following surfaces may be referenced for seam and operational-boundary reasoning only. They must not be edited and must not be treated as implementation or operational approval:

- `scripts/paper_trading_runner.py`
- `docs/paper_trading/runner_deployment.md`
- `docs/paper_trading/phase3_runbook.md`

### Exact opt-in boundary

The future implementation may expose exactly one explicit CLI flag:

- `--ri-paper-shadow`

If the flag is absent:

- runner behavior must remain unchanged
- the outbound `/strategy/evaluate` request state must remain exactly the existing pipeline state
- no new RI paper-shadow log or summary line may be emitted

If the flag is present:

- the runner must require effective dry-run mode (`--dry-run`, `--live-paper` false)
- the runner must fail fast if `--ri-paper-shadow` is combined with `--live-paper`
- the runner may only request `state["observability"]["scpe_ri_v1"] = true`
- the runner must merge that request opt-in additively without mutating unrelated existing state keys
- if the existing outbound state already contains an `observability` object, the slice must stop and require re-review rather than silently merging ambiguous authority

### Exact consumer boundary

The runner may consume or log only these existing fields from `meta["observability"]["scpe_ri_v1"]`:

- `family_tag`
- `lane`
- `observational_only`
- `decision_input`
- `enabled_via`
- `authority_mode`
- `authority_mode_source`
- `authoritative_regime`
- `shadow_regime`
- `regime_mismatch`

Any future RI paper-shadow summary must remain local to runner-side dry-run observability only, such as local decision-context logging for the runner process.
It must not widen or mutate any outbound request payload, `/paper/submit` payload, persisted runner state schema, or other external surface.

The runner must not derive or influence:

- order side
- order size
- action gating
- quarantine state
- watchdog thresholds
- runtime-config/default-authority semantics
- readiness, promotion, or live-paper behavior

### Allowed implementation work

The future implementation may do only the following:

1. add one default-OFF CLI flag in `scripts/paper_trading_runner.py`
2. add one small helper that merges the RI observability opt-in into the outbound evaluate request state only in dry-run mode
3. add one bounded helper that extracts the already-existing RI payload into additive runner observability/log context only when present
4. add focused integration coverage in `tests/integration/test_paper_trading_runner.py`
5. write one bounded implementation report

### Explicitly forbidden operations

- any support for `--ri-paper-shadow` in `--live-paper` mode
- any change to `/paper/submit` behavior or payloads
- any mutation of quarantine, watchdog, champion verification, or runtime-config/default-authority semantics
- any edit to `src/core/api/strategy.py`, `src/core/strategy/evaluate.py`, or other `src/**` surfaces
- any widening of the RI runtime-observability payload
- any new artifact file schema outside the existing runner log/state surfaces
- any edit to `docs/paper_trading/runner_deployment.md` or `docs/paper_trading/phase3_runbook.md`
- any wording or code path that implies paper approval, live-paper approval, readiness, cutover, launch, deployment, or promotion

### Required gates

1. `pre-commit run --files docs/decisions/scpe_ri_v1_paper_shadow_slice1_precode_packet_2026-04-21.md docs/analysis/scpe_ri_v1_paper_shadow_slice1_implementation_report_2026-04-21.md scripts/paper_trading_runner.py tests/integration/test_paper_trading_runner.py`
2. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/integration/test_paper_trading_runner.py tests/integration/test_paper_trading_runner_candles_window_ordering.py`
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_runtime_observability_default_off_parity tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_runtime_observability_payload_opt_in_shape`
4. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
5. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
6. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- any need to touch `src/**` or server-side runtime payload code
- any drift toward live-paper semantics or order-authority coupling
- any attempt to store RI paper-shadow outputs in runtime-authoritative paths
- any ambiguity in outbound runner state merge involving pre-existing `observability` keys
- any UI/readiness/promotion framing

### Output required

- one reviewable pre-code packet
- one bounded future implementation diff on the exact files above only
- `docs/analysis/scpe_ri_v1_paper_shadow_slice1_implementation_report_2026-04-21.md` with exact gate outcomes and dry-run-only proof

## Why this is the smallest honest next slice

This slice stays later than the now-closed runtime-observability lane but still below live-paper semantics.
It reuses an already-existing RI payload and the already-existing paper-runner evaluate/request seam.
It keeps activation explicit and default-OFF, while treating the execution-adjacent runner path as sensitive enough to forbid order authority drift.

## Bottom line

This packet opens one bounded next step only:

- a dry-run-only, default-OFF, observational SCPE RI paper-shadow bridge slice on the paper runner.

Nothing in this packet authorizes live-paper use, order submission changes, runtime-config/default-authority changes, readiness, cutover, or promotion.
