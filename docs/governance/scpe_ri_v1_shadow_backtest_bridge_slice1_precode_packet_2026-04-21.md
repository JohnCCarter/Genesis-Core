# SCPE RI V1 shadow-backtest bridge slice1 pre-code packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / planning-only / no authorization`

This document is a pre-code planning packet only. It does not authorize execution, artifact generation, code changes, config changes, test changes, runtime instrumentation, or implementation of any RI-only shadow-backtest slice. Any runnable slice requires a separate packet, fresh scope approval, separate risk/path classification, and separate verification.

## Future packet scaffold (planning-only, non-executable placeholder)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk (current packet only):** `LOW` — why: this packet itself is a docs-only pre-code definition artifact; it must remain narrower than execution planning, narrower than admissibility for a runnable slice, and narrower than any implementation authority
- **Required Path (current packet only):** `Quick`
- **Objective:** define exactly one future bounded RI-only shadow-backtest evidence-capture slice on the already visible generic shadow seam, while keeping the slice no-code in shape and fail-closed by default
- **Candidate:** `future RI-only shadow-backtest bridge evidence-capture slice1`
- **Base SHA:** `00e429ab`

The scaffold below is a non-executable planning placeholder only. It contains no approved commands, selectors, gates, implementation scope, readiness claim, or authorization for future work.

### Scope

- **Scope IN:** one docs-only pre-code packet that selects exactly one RI-only shadow-backtest hypothesis, defines the exact future subject boundary, defines the exact future artifact envelope, defines what remains fixed, and defines the prove-or-stop falsification condition for a later separately authorized runnable slice
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; all code/config/test/runtime changes; all runtime instrumentation; all champion/default mutation; all config-authority mutation; all paper/live coupling; all readiness/cutover/promotion framing; all execution approval
- **Expected changed files:** `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_precode_packet_2026-04-21.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that treats this packet as execution approval
- any wording that treats the existing generic seam as already verified launch authority
- any wording that pre-approves the future runnable slice as `Quick`
- any wording that authorizes code/config/test/runtime changes for the future slice
- any wording that introduces paper-shadow, runtime instrumentation, behavior change, readiness, cutover, or promotion authority

## Purpose

This packet answers one narrow question only:

- what is the first exact bounded RI-only shadow-backtest slice that may be considered later on the already visible generic shadow seam, if work continues?

This packet is **planning-only governance**.

It does **not**:

- authorize a runnable slice
- authorize execution
- authorize artifact generation
- authorize code changes
- authorize config changes
- authorize test changes
- authorize runtime instrumentation
- authorize paper-shadow work
- authorize readiness, cutover, or promotion

## Governing basis

This packet is downstream of the following tracked artifacts:

- `docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md`
- `docs/governance/scpe_ri_v1_runtime_integration_roadmap_2026-04-20.md`
- `docs/governance/scpe_ri_v1_runtime_integration_seam_inventory_2026-04-20.md`
- `docs/governance/scpe_ri_v1_shadow_backtest_packet_boundary_2026-04-20.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

Carried-forward meaning:

1. the bounded SCPE RI research lane is closed and grants no inherited runtime/integration approval
2. the shadow-backtest seam is the smallest currently visible implementation-adjacent seam in the repository snapshot
3. the generic shadow seam already exists in tracked repository state, but that seam visibility does **not** by itself create execution authority
4. the RI evidence-capture lane must remain RI-only and bounded to a fixed RI carrier rather than mixing legacy and RI evidence surfaces
5. the nearest fixed RI bridge is a backtest-only runtime bridge, not promotion evidence

## Existing generic seam premise

The existing generic shadow seam is treated here as a premise for a future **prove-or-stop** check, not as execution authority established by this packet.

The repository already shows the following generic seam surfaces:

- `scripts/run/run_backtest.py`
  - supports `--intelligence-shadow-out`
  - supports `--decision-rows-out`
  - wires passive hooks into the backtest engine
- `src/core/backtest/intelligence_shadow.py`
  - records deterministic shadow events
  - derives advisory-only parameter sets
  - emits non-authoritative summary + ledger-linked artifacts
- `src/core/backtest/engine.py`
  - exposes passive `evaluation_hook(result, meta, candles)` composition

This packet does **not** claim that those surfaces are already sufficient for RI-specific execution. It defines only the exact future question to test later under separate approval.

## 1) Exact slice hypothesis

The exact first RI-only shadow-backtest hypothesis is:

- **The already visible generic shadow-backtest seam may be sufficient to produce deterministic, non-authoritative RI shadow evidence on one fixed RI runtime-bridge subject without any Python, config, test, runtime, or paper-path changes.**

This is a prove-or-stop hypothesis.

If the future slice requires any code/config/test/runtime change to succeed, the slice must stop as `BLOCKED` rather than expanding scope in place.

## 2) Exact future subject boundary

The exact future RI-only subject is fixed as follows:

### Exact config-source anchor

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

This file is cited as:

- `strategy_family = ri`
- `authority_mode = regime_module`
- backtest-only runtime bridge
- not a champion
- not promotion evidence

### Exact observational context

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`

### Exact slice shape

The future runnable slice, if separately authorized later, must remain:

- RI-only
- opt-in
- observational only
- non-authoritative
- no-code in intended shape
- bounded to exactly the subject above

## 3) Hypothetical future writable surfaces if separately authorized later

If a separately authorized runnable slice is approved later, writable surfaces may be limited to predefined research artifacts and at most one future execution summary.

The exact future writable surfaces may only be:

1. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson`
2. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson`
3. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`
4. `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`
5. `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`

If any additional file changes are required — or if any code/config/test/runtime changes are required — the future slice must stop and be marked `BLOCKED` rather than expanding scope.

## 4) What remains fixed

The future slice must keep the following fixed:

- the exact RI bridge config anchor named above
- `strategy_family = ri`
- `multi_timeframe.regime_intelligence.authority_mode = regime_module`
- `multi_timeframe.regime_intelligence.clarity_score.enabled = false`
- symbol/timeframe/date window named above
- opt-in activation only
- no champion/default/config-authority mutation
- no runtime instrumentation
- no paper-shadow coupling
- no behavior change
- no readiness/cutover/promotion framing

## 5) Exact future artifacts to prove or falsify the slice

If a separately authorized runnable slice is approved later, it should produce only the following evidence classes:

### A. Control-vs-shadow decision-row evidence

- `control_decision_rows.ndjson`
- `shadow_decision_rows.ndjson`

Purpose:

- prove that the RI-only shadow path does not introduce decision drift on the fixed subject

### B. Shadow summary evidence

- `shadow_summary.json`

Purpose:

- prove that the existing generic seam can emit deterministic non-authoritative RI shadow output on the fixed subject

### C. Ledger persistence evidence

- deterministic ledger root under `artifacts/intelligence_shadow/.../research_ledger/`

Purpose:

- prove that the RI-only slice can persist bounded shadow evidence without entering runtime-config authority

### D. Execution closeout summary

- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`

Purpose:

- record whether the prove-or-stop hypothesis passed or failed
- remain research-only and non-authoritative

## 6) Exact falsification condition

The future slice is falsified and must stop if any of the following is true:

1. the fixed RI subject cannot be exercised on the existing generic seam without Python code changes
2. the fixed RI subject cannot be exercised without config changes, champion/default mutation, or config-authority mutation
3. the fixed RI subject requires runtime instrumentation or paper-path coupling
4. `control_decision_rows.ndjson` and `shadow_decision_rows.ndjson` do not preserve row identity / action / size / reasons parity on the fixed subject
5. `shadow_summary.json` does not remain observational and non-authoritative
6. any output is required outside the predefined future writable surfaces

## 7) Expected research-only output boundary

The future slice, if separately authorized later, is expected to emit only:

- bounded control-vs-shadow decision-row evidence
- bounded shadow summary evidence
- bounded ledger persistence evidence
- one research-only execution summary

Those outputs would be sufficient only for:

- RI shadow evidence capture
- parity/no-drift assessment on the fixed subject
- later governance interpretation

Those outputs would **not** be sufficient for:

- runtime authority
- runtime instrumentation approval
- paper-shadow approval
- behavior-change approval
- readiness opening
- cutover opening
- promotion opening

## Authority boundary

This packet itself is a docs-only `LOW` / `Quick` planning artifact.

Risk classification and required path for any future runnable RI-only slice are explicitly deferred to a separate authorization step and must not be pre-approved here.

Nothing in this packet changes or reinterprets runtime authority, family rules, champion/default authority, or the closed status of runtime-observability, paper-shadow, readiness, cutover, or promotion surfaces.

## Bottom line

The first exact RI-only shadow-backtest slice is now defined, but only at pre-code level:

- it would be a **no-code, prove-or-stop evidence-capture slice** if separately authorized later
- it is anchored to the fixed RI bridge `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- it is bounded to `tBTCUSD`, `3h`, `2024-01-02 -> 2024-12-31`
- it may only write bounded non-authoritative research artifacts if separately authorized later
- it must stop as `BLOCKED` if any code/config/test/runtime widening is needed

Nothing in this packet authorizes execution, artifact generation, implementation, runtime instrumentation, paper coupling, readiness, cutover, or promotion.
