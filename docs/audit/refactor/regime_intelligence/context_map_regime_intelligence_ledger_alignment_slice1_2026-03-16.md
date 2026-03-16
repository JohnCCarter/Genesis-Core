## Context Map

### Files to Modify

| File                                                                                                               | Purpose                                                                                                              | Changes Needed                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/intelligence/regime/contracts.py`                                                                        | Existing public contract surface for migrated RI pure-analysis outputs                                               | Extend the existing contract surface with a minimal pre-alignment contract for current RI observability/evidence shape instead of creating new helper modules |
| `tests/core/intelligence/regime/test_contracts.py`                                                                 | Locks contract serialization/payload shape                                                                           | Add tests for the new pre-alignment contract shape and deterministic serialization                                                                            |
| `tests/backtest/test_regime_shadow_artifacts.py`                                                                   | Existing RI evidence artifact contract (`clarity_histogram.json`, `clarity_quantiles.json`, `shadow_samples.ndjson`) | Add or tighten assertions that the contract-facing evidence shape stays aligned with existing artifact naming/payload expectations                            |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_ledger_alignment_slice1_2026-03-16.md`    | Slice-local context map                                                                                              | Capture active scope and dependencies                                                                                                                         |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_ledger_alignment_slice1_2026-03-16.md` | Governance packet                                                                                                    | Lock scope, constraints, gates, and stop conditions before implementation                                                                                     |

### Dependencies (may need updates)

| File                                       | Relationship                                                                                                                           |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/backtest/test_evaluate_pipeline.py` | Holds the existing runtime observability/authority contract that the pre-alignment contract must mirror without modifying runtime code |
| `src/core/strategy/evaluate.py`            | Produces the current `meta.observability.shadow_regime` shape that the pre-alignment contract is allowed to describe but not modify    |
| `src/core/strategy/regime_intelligence.py` | Current runtime compatibility layer; must remain untouched in this slice                                                               |
| `src/core/strategy/decision_sizing.py`     | Consumes runtime-owned risk-state logic; explicit scope-out boundary for this slice                                                    |
| `src/core/research_ledger/models.py`       | Future prerequisite dependency only; not present in the feature worktree and therefore excluded from slice-1 implementation scope      |

### Test Files

| Test                                                                                                               | Coverage                                                                                  |
| ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `tests/core/intelligence/regime/test_contracts.py`                                                                 | Contract serialization and legacy-shape preservation                                      |
| `tests/backtest/test_regime_shadow_artifacts.py`                                                                   | RI evidence artifact and sample payload contract                                          |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_regime_observer_preserves_default_parity` | Strongest parity lock for the shadow observability surface referenced by the new contract |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`        | Existing authority-mode source invariant that the new contract must not contradict        |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                | Deterministic backtest baseline for high-sensitivity evaluate path                        |
| `tests/governance/test_pipeline_fast_hash_guard.py`                                                                | Pipeline component order hash invariant                                                   |

### Reference Patterns

| File                                                                                         | Pattern                                                                                                                         |
| -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/intelligence/regime/contracts.py`                                                  | Existing contract objects expose deterministic payload conversion methods instead of introducing free-floating helper functions |
| `tests/backtest/test_regime_shadow_artifacts.py`                                             | Existing RI evidence file naming and payload shape that tranche 4 should reference rather than redesign                         |
| `docs/audit/refactor/decision/command_packet_decision_fib_gating_split_slice4_2026-03-12.md` | Current repo pattern for high-sensitivity no-behavior-change refactor packet structure                                          |

### Risk Assessment

- [x] Breaking changes to public API
- [ ] Database migrations needed
- [ ] Configuration changes required

### Notes

- This slice is only justified if it uses the existing contract surface in `contracts.py` and does not create extra helper layers.
- Avoid creating new helper modules/files under `src/core/intelligence/regime/` unless a concrete, named consumer cannot be served by the current contract module.
- The feature worktree currently lacks `src/core/research_ledger/**` and `tests/core/research_ledger/**`; true ledger-native integration is therefore a later prerequisite-enabled slice, not part of slice 1.
- `compute_risk_state_multiplier(...)` and other runtime sizing behavior remain explicitly out of scope.
