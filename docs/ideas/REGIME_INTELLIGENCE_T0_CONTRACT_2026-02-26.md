# REGIME INTELLIGENCE T0 CONTRACT (Docs-only)

Date: 2026-02-26
Category: `docs`

## 1) Commit contract

### Scope IN

- `docs/ideas/REGIME_INTELLIGENCE_T0_CONTRACT_2026-02-26.md`
- `docs/ideas/REGIME_INTELLIGENCE_DESIGN_2026-02-23.md` (read-only context in this tranche)
- `docs/Genesis-Core-Regime-Intelligence-V1-Design-Document.md` (read-only context in this tranche)

### Scope OUT

- All files outside `docs/**`
- All behavior-sensitive code paths under `src/**`
- Runtime/config authority paths and any execution logic

### Constraints

- **NO BEHAVIOR CHANGE**
- Docs-only tranche; no runtime, API, strategy, optimizer, or backtest semantics may change.

## 2) SSOT decisions (locked for T0/T1)

1. **Runtime SSOT for T0/T1** is `runtime.regime_unified`.
2. `regime.py` is **shadow-only in T1** (non-authoritative observer path), and must not become authority in T0/T1.
3. Any future authority migration requires explicit contract exception and parity proof.

## 3) Label mapping contract

- Canonical regime labels and mapping must be explicitly documented and stable.
- Mapping changes are treated as behavior-sensitive and are out-of-scope for this docs-only tranche.
- Any proposed label remap must include:
  - default-off rollout strategy,
  - OFF-parity evidence,
  - deterministic replay confirmation.

## 4) Flag/version strategy

- Any behavior-changing path must be behind explicit **flag/version**.
- **Default remains OFF**.
- **OFF parity is mandatory** before enabling/rolling out any changed behavior.

## 5) DD/risk precedence policy lock (docs-level)

- Decision/default precedence remains locked at docs level for T0:
  - DD/risk precedence order is unchanged,
  - no reinterpretation of risk defaults,
  - no hidden drift in sizing/guards via documentation wording.

## 6) Skills-first policy note

- Relevant repo skills must be invoked before implementation in non-doc tranches.
- `feature_parity_check` is a **policy attestation** skill in current repo state; expected
  outcome is `STOP`/`no_steps` and is **not** interpreted as gate failure.
- If a suitable skill is missing, it is marked **`föreslagen`** until added and verified.
- This T0 artifact does **not** claim new skill coverage as `införd`.

## 7) Status discipline

- Use **`föreslagen`** for not-yet-implemented process/tooling changes.
- Use **`införd`** only after verified implementation in this repository.

## 8) Required PRE/POST gates (exact commands)

### PRE gates

1. `pre-commit run --files docs/ideas/REGIME_INTELLIGENCE_DESIGN_2026-02-23.md docs/Genesis-Core-Regime-Intelligence-V1-Design-Document.md docs/ideas/REGIME_INTELLIGENCE_T0_CONTRACT_2026-02-26.md`
2. `pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
4. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
5. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### POST gates

1. `pre-commit run --files docs/ideas/REGIME_INTELLIGENCE_DESIGN_2026-02-23.md docs/Genesis-Core-Regime-Intelligence-V1-Design-Document.md docs/ideas/REGIME_INTELLIGENCE_T0_CONTRACT_2026-02-26.md`
2. `pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
4. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
5. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

## 9) Done criteria for this tranche

- PRE gates pass.
- Contract file exists with this locked content.
- POST gates pass.
- Staged diff remains within Scope IN.
- Commit message includes Category / Why / What / Gate results.
