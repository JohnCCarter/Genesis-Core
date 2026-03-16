# Command Packet — regime intelligence ledger alignment slice 1

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: current branch `feature/regime-intelligence-layer-migration` mapped by `docs/governance_mode.md` (`feature/* -> RESEARCH`)
- **Risk:** `MED` — why: planned scope is limited to the existing RI contract module plus contract-facing tests, but it prepares a future alignment for a strategy/runtime observability surface and therefore still carries contract-drift risk
- **Required Path:** `Full`
- **Objective:** Perform a no-behavior-change first pre-alignment slice for Regime Intelligence by extending the existing `src/core/intelligence/regime/contracts.py` contract surface to describe the current RI observability/evidence shape in a deterministic, reusable form, while preserving all runtime behavior and deferring true ledger-native integration until the feature worktree contains the required ledger substrate.
- **Candidate:** `regime intelligence ledger alignment slice 1`
- **Base SHA:** `2a214b6e46c72ef36cacffc0b0be1274473976dc`

### Scope

- **Scope IN:**
  - `src/core/intelligence/regime/contracts.py`
  - `tests/core/intelligence/regime/test_contracts.py`
  - `tests/backtest/test_regime_shadow_artifacts.py`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_ledger_alignment_slice1_2026-03-16.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_ledger_alignment_slice1_2026-03-16.md`
- **Scope OUT:**
  - `src/core/strategy/evaluate.py`
  - `src/core/strategy/regime_intelligence.py`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/intelligence/regime/clarity.py`
  - `src/core/intelligence/regime/authority.py`
  - `src/core/intelligence/regime/htf.py`
  - `src/core/research_ledger/**`
  - `tests/core/research_ledger/**`
  - all `config/**`
  - all `src/core/backtest/**`
  - all `src/core/optimizer/**`
  - runtime sizing/risk-state behavior
  - authority resolution semantics
  - shadow-regime decision authority semantics
  - new helper modules/files under `src/core/intelligence/regime/` unless governance re-approves due to proven unmet contract need
- **Expected changed files:** `5`
- **Max files touched:** `5`

### Context map

- `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_ledger_alignment_slice1_2026-03-16.md`

### Skill Usage

- `repo_clean_refactor` — governs the no-behavior-change, scope-locked, high-sensitivity structure/alignment slice and requires minimal, reversible diffs plus explicit gate evidence.
- No feature-parity skill is claimed for this slice because the target is ledger-alignment of RI observability/evidence contracts, not feature computation changes.

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Reuse the existing `src/core/intelligence/regime/contracts.py` module; do not create a new helper file merely to hold mapping glue.
- Any new contract type or method must serve a concrete, named consumer in this slice:
  - `tests/core/intelligence/regime/test_contracts.py`
  - `tests/backtest/test_regime_shadow_artifacts.py`
  - parity/invariant selectors that lock the current runtime observability shape
- Preserve `meta.observability.shadow_regime` key set, nested shape, semantics, and public consumers unchanged by treating it as a described external contract, not an implementation target, in this slice.
- Preserve artifact generation behavior in `tests/backtest/test_regime_shadow_artifacts.py` unchanged:
  - `clarity_histogram.json`
  - `clarity_quantiles.json`
  - `shadow_samples.ndjson`
- This slice may add pre-alignment contract descriptions only; it must not:
  - change action/regime/size decisions
  - change authority-mode resolution
  - change runtime payload assembly
  - change UI payload contracts
  - require new config keys
  - import or depend on missing ledger modules in the target worktree
- If the design requires more than one new contract object plus tightly related serialization methods in `contracts.py`, stop and re-review the design before implementation.
- Do not introduce new helper functions inside `src/core/intelligence/regime/contracts.py` unless they are methods on the contract object itself and serve a concrete, named consumer in this slice.

### Planned implementation

1. Extend `src/core/intelligence/regime/contracts.py` with the minimum pre-alignment contract shape needed to represent the current RI observability/evidence surface deterministically.
2. Add deterministic serialization tests in `tests/core/intelligence/regime/test_contracts.py` that lock the new contract payload shape.
3. Extend `tests/backtest/test_regime_shadow_artifacts.py` to lock the mapping between existing RI evidence artifacts and the new pre-alignment contract shape.
4. Run parity/invariant selectors that prove the runtime observability surface remains unchanged.
5. Run the full gate stack.
6. Request Opus post-diff audit before any commit-ready claim.

### Gates required

- `pre-commit run --all-files`
- `black --check src/core/intelligence/regime/contracts.py tests/core/intelligence/regime/test_contracts.py tests/backtest/test_regime_shadow_artifacts.py`
- `ruff check src/core/intelligence/regime/contracts.py tests/core/intelligence/regime/test_contracts.py tests/backtest/test_regime_shadow_artifacts.py`
- `pytest tests/governance/test_import_smoke_backtest_optuna.py -q`
- Focused selectors:
  - `tests/core/intelligence/regime/test_contracts.py`
  - `tests/backtest/test_regime_shadow_artifacts.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_regime_observer_preserves_default_parity`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
- Required invariants:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Any scope drift outside the listed files
- Any proposal to create new regime helper modules/files without a concrete, named consumer that cannot be served by `contracts.py`
- Any proposal to add helper-only functions inside `contracts.py` without a direct slice-1 consumer
- Any drift in `meta.observability.shadow_regime` key set, payload shape, or semantics
- Any change to action, regime, confidence, authority-mode, or size outputs
- Any change to evidence file names, write conditions, or payload shape in `test_regime_shadow_artifacts` flow
- Any new config semantics or environment-variable semantics
- Any attempt to import or depend on absent `research_ledger` worktree modules
- Determinism replay regression
- Pipeline invariant regression
- Touching unrelated high-sensitivity modules without explicit re-approval

### Output required

- **Implementation Report** with exact files changed, exact commands run, and pass/fail outcomes
- **PR evidence template** / READY_FOR_REVIEW evidence after post-diff audit

### Residual risks

- The biggest risk is accidental introduction of “nice-looking” adapter layers that do not add concrete value; this slice must stay contract-first and minimal.
- Because true ledger substrate is absent in the feature worktree, this slice must stop at pre-alignment and avoid pretending that ledger-native integration is already implemented.
- If the contract cannot stay small and obviously tied to current evidence/observability surfaces, this slice should be narrowed again rather than expanded.

### Pre-review request for Opus

Please verify:

1. whether this reduced pre-alignment scope is now tight enough for slice 1,
2. whether the selected parity/invariant gates are sufficient without `evaluate.py` in scope,
3. whether the helper-minimization constraint is strong enough,
4. whether the absence of worktree-local `research_ledger` substrate is now handled correctly.
