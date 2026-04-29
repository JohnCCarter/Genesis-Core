# FA v2 — adaptation-off controlled intervention packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / research / controlled-intervention`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/*`
- **Category:** `obs`
- **Risk:** `HIGH` — why: this task touches the high-sensitivity canonical decision route inside `src/core/strategy/decision_gates.py`, intentionally changes candidate-selection behavior under an explicit research-only switch, and then re-runs canonical backtests plus full attribution classification.
- **Required Path:** `Full`
- **Objective:** Remove the runtime monopoly of `thresholds.signal_adaptation` over `thresholds.entry_conf_overall` and `thresholds.regime_proba` under an explicit research-only hard-off switch, then run a deterministic adaptation-off baseline and reclassify all previously admitted Feature Attribution units on that exposed decision surface.
- **Candidate:** `Signal-adaptation threshold cluster`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** `docs/governance/fa_v2_adaptation_off_controlled_intervention_packet_2026-03-31.md`; `src/core/strategy/decision_gates.py`; targeted tests proving default behavior is unchanged when the switch is absent and that base thresholds become authoritative when the switch is explicitly disabled; deterministic canonical backtest execution using `GenesisPipeline.setup_environment(seed=42)` + `GenesisPipeline.create_engine(...)` + `BacktestEngine.run(...)`; effective-config snapshot and diff proof for every governed run; new research artifacts under `results/research/fa_v2_adaptation_off/` only.
- **Scope OUT:** no edits under `config/strategy/champions/**`; no edits to `src/core/strategy/decision.py`; no redesign of candidate selection, sizing, HTF/LTF structure, or fib logic; no Optuna; no parameter tuning; no structural refactor; no new CLI surface; no new env-var surface; no modification of default champion config; no artifact writes outside `results/research/fa_v2_adaptation_off/`.
- **Expected changed files:** this packet; `src/core/strategy/decision_gates.py`; targeted test file(s); `results/research/fa_v2_adaptation_off/summary.md`; `results/research/fa_v2_adaptation_off/delta_metrics.json`; `results/research/fa_v2_adaptation_off/attribution_classification.json`; `results/research/fa_v2_adaptation_off/shadowing_status.md`
- **Max files touched:** `8`

### Controlled intervention design

The smallest admissible intervention is:

- support `thresholds.signal_adaptation.enabled = false` in `src/core/strategy/decision_gates.py::select_candidate`
- when absent, behavior remains identical to today (`enabled` defaults to active)
- when explicitly `false`, `signal_adaptation` is completely bypassed in candidate selection
- when explicitly `false`, candidate selection must use:
  - base `thresholds.entry_conf_overall`
  - base `thresholds.regime_proba`
- no blending, fallback, or partial zone contribution is allowed once `enabled = false`

This switch is research-only and default-off from an authority perspective:

- default runtime behavior remains unchanged because the new leaf is absent in the baseline config source
- the intervention is activated only in execution-time override configs used for FA v2 research runs
- no champion/default/runtime promotion is in scope

### Skill Usage

- Repo-local SPEC anchors for this controlled intervention are:
  - `.github/skills/backtest_run.json` — canonical backtest discipline anchor only
  - `.github/skills/feature_parity_check.json` — default-behavior / parity anchor only
  - `.github/skills/ri_off_parity_artifact_check.json` — artifact-integrity anchor only
- These anchors do **not** replace determinism replay, pipeline invariant checks, config-authority verification, or effective-config diff proof.

### Schema and canonicalization contingency

- The planned path assumes the new nested leaf `thresholds.signal_adaptation.enabled` is already admissible through the existing runtime validation / canonicalization surface.
- Stop if `ConfigAuthority.validate(...)` or canonical runtime dumping drops, rejects, or silently rewrites this leaf.
- If that stop occurs, scope may expand only minimally to the exact schema / canonicalization file(s) required to preserve the leaf, and no broader redesign is authorized under this packet.

### Override provenance lock

- Every governed execution under this packet must record:
  - base SHA
  - baseline config source
  - override source
  - effective-config snapshot
  - effective-config diff snapshot
  - output root `results/research/fa_v2_adaptation_off/`
- Dirty working tree state must be treated as provenance-sensitive and must not be left implicit in the report artifacts.

### Execution plan boundary

The deterministic run sequence for this packet is:

1. Reproduce `baseline_current` on the current executable route using the canonical pipeline/engine path and current `merged_config`.
2. Run `adaptation_off` with the same config, data, timeframe, dates, seed, and execution path, with the only intended effective-config delta being `thresholds.signal_adaptation.enabled = false`.
3. Re-run attribution over the same admitted units and same metric set, now relative to the `adaptation_off` baseline.
4. Record whether base thresholds and regime thresholds are now observable, and whether a new dominant controller appears.

### Admitted-unit rerun boundary

The rerun scope remains exactly the admitted v1 units:

- `Base entry confidence seam`
- `Regime probability threshold cluster`
- `Signal-adaptation threshold cluster`
- `Minimum-edge gate seam`
- `Hysteresis gate seam`
- `Cooldown gate seam`
- `Regime sizing multiplier cluster`
- `HTF regime sizing multiplier cluster`
- `Volatility sizing cluster`
- `HTF block seam`
- `LTF override cluster`

The reclassification vocabulary for output artifacts is fixed to:

- `driver edge`
- `neutral`
- `harmful`
- `mixed`
- `cannot isolate`

### Gates required

- file diagnostics on touched source/test/artifact files
- `python -m ruff check src/core/strategy/decision_gates.py tests/integration/test_golden_trace_runtime_semantics.py`
- `python -m pytest -q tests/integration/test_golden_trace_runtime_semantics.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/governance/test_config_authority_hash_contract.py`
- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
- deterministic backtest comparison: `baseline_current` vs `adaptation_off`
- effective-config proof that the only intended baseline-vs-intervention diff is `thresholds.signal_adaptation.enabled = false`
- quantified comparison of the v2 vs v1 classification surfaces across the same admitted units, explicitly reporting whether the surface is identical, partially shifted, or materially different
- shadowing proof in `shadowing_status.md`

### Stop Conditions

- any need to touch `config/strategy/champions/**`
- any need to broaden beyond candidate-selection threshold ownership for the intervention itself
- any residual signal-adaptation influence on threshold selection when `enabled = false`
- any fallback/blending behavior when `enabled = false`
- any default behavior drift when the new switch is absent
- any failure of runtime validation or canonical dumping to preserve `thresholds.signal_adaptation.enabled` as an explicit effective-config leaf
- inability to prove deterministic current baseline and adaptation-off baseline from the same canonical path
- any need to modify sizing logic, HTF/LTF structure, or fib semantics to complete the task

### Output required

- code-level hard-off intervention behind explicit research-only switch
- deterministic `baseline_current` vs `adaptation_off` comparison
- full rerun classification artifacts under `results/research/fa_v2_adaptation_off/`
- effective-config snapshot + diff evidence for baseline and adaptation-off runs
- concise implementation report with residual risks and exact gates/outcomes

## Notes

This packet authorizes a controlled intervention only.
It does not authorize optimization, retuning, redesign, promotion, or champion mutation.
