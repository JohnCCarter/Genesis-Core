This report is an observational synthesis only over the locked Phase 7, Phase 9, Phase 10, Phase 11, Phase 12, and Phase 13 artifacts. Phase 6–7 invalidation remains active, and nothing in this report validates signals, authorizes deployment, or upgrades the locked artifact surface into runtime authority.

## Locked conclusion ladder

- **Phase 7 — signal-layer validity**
  - `probability_edge_stats.json` reports `verdict = no edge` on the locked binary audited trade population of 82 trades.
  - `calibration = FAIL`, `gap_monotonicity = NO`, and `statistical_edge = NO`.
  - `directional_accuracy = PASS` is limited to observed executed `LONG_SIGNAL` support and does not reverse the overall `no edge` verdict.

- **Phase 9 — state dependence**
  - `state_edge_matrix.json` reports `final_verdict = edge is not state-dependent`.
  - No packet-authorized state dimension reached `edge_concentrated = YES`.

- **Phase 10 — edge-origin isolation surfaces**
  - `execution_attribution.json` reports `analysis_status = LIMITED_ARTIFACT_SURFACE` and omits price-path-dependent execution attribution under packet guardrails.
  - `selection_attribution.json` reports `selection_surface_status = CONTRAST_AVAILABLE` on the packet-authorized timestamp-level opportunity surface, but stronger selection-causality claims remain unsupported.
  - `counterfactual_matrix.json` records `unit_size_normalization = PASS` and `trade_order_shuffle = PASS`.
  - `path_dependency.json` reports `path_dependency_detected = NO`.

- **Phase 11 — stability**
  - `edge_stability.json` reports `phase11_classification.label = stable`.
  - `temporal_stability_verdict = PASS` and `bootstrap_stability_verdict = PASS`.

- **Phase 12 — minimality**
  - `minimal_system.json` reports `minimal_system_status = IDENTIFIED`.
  - The selected minimal preserved system is `UNIT_SIZE_ORDER_NEUTRAL_SYSTEM`.
  - `size_amplitude_authority` and `path_order_authority` are both `REDUNDANT`, and the tested local authorities remain `NOT_CRITICAL`.

- **Phase 13 — classification**
  - `edge_classification.json` reports `primary_classification_status = IDENTIFIED`.
  - The primary classification is `emergent_system_behavior`.
  - `statistical_artifact` is `REJECTED`.
  - `structural_market_microstructure`, `regime_independent_drift`, and `execution_inefficiency` remain `UNATTESTED`.

## Origin hypothesis

The best-supported origin hypothesis within the packet-authorized artifact surface is **`emergent_system_behavior`**.

This hypothesis is identified because the locked evidence does not support a signal-layer explanation, does not support a state-dependent explanation, does not support a statistical-artifact explanation inside the Phase 11 stability surface, and still preserves positive realized edge after the packet-authorized local removals of size-amplitude authority and path-order authority. Within the locked surface, the observed edge therefore survives as a system-level property of the carried-forward realized trade structure rather than as an attested signal, state pocket, or single local authority.

## Evidence

**Supported evidence**

- Phase 7 rejects signal-layer edge on the locked audited trade population: `verdict = no edge`, with `calibration = FAIL`, `gap_monotonicity = NO`, and `statistical_edge = NO`.
- Phase 9 rejects state concentration as the governing explanation on the packet-authorized state-partition surface: `final_verdict = edge is not state-dependent`.
- Phase 10 packet-authorized controls show that the tested local authorities did not collapse the observed edge:
  - `unit_size_normalization = PASS`
  - `trade_order_shuffle = PASS`
  - `path_dependency_detected = NO`
- Phase 10 selection contrast is now attested on the authorized timestamp-level availability surface:
  - `selection_surface_status = CONTRAST_AVAILABLE`
  - `shared_opportunity_count = 1800`
  - `baseline_only_opportunity_count = 279`
  - `adaptation_off_only_opportunity_count = 345`
- Phase 11 shows the observed baseline edge is stable on the authorized temporal/bootstrap surface:
  - `phase11_classification.label = stable`
  - `temporal_stability_verdict = PASS`
  - `bootstrap_stability_verdict = PASS`
- Phase 12 identifies `UNIT_SIZE_ORDER_NEUTRAL_SYSTEM` as the first packet-authorized minimal preserved system and marks the tested size/path authorities as non-critical to preservation.
- Phase 13 identifies `emergent_system_behavior` as the only packet-authorized supported primary class on the locked evidence matrix.

**Rejected explanations on the locked surface**

- **Signal-layer explanation:** not supported on the Phase 7 audited trade population.
- **State-dependent explanation:** not supported on the Phase 9 state-isolation surface.
- **Statistical artifact:** rejected on the Phase 11 temporal/bootstrap stability surface.

**Constrained surfaces that remain limited**

- `execution_attribution.json` remains `LIMITED_ARTIFACT_SURFACE`, so stronger execution-mechanism attribution is still packet-constrained.
- `selection_attribution.json` now attests `CONTRAST_AVAILABLE` on the timestamp-level availability surface, but stronger selection-membership causality remains packet-constrained.
- `UNATTESTED` is not the same as `REJECTED`; unattested classes remain unresolved because the locked artifact surface does not authorize stronger proof in those directions.

## Falsification attempts

- **Phase 7 signal-edge validation** attempted to falsify the claim that the observed edge came from predictive signal quality.
  - Result: the locked audited-trade verdict is `no edge`, so a signal-layer explanation does not survive the packet-authorized validation surface.

- **Phase 9 state-isolation testing** attempted to falsify the claim that the observed edge was concentrated in packet-authorized state partitions.
  - Result: `final_verdict = edge is not state-dependent`, so a state-pocket explanation does not survive the authorized concentration test.

- **Phase 10 `unit_size_normalization`** challenged whether the packet-authorized size-amplitude surface was required for positive realized edge.
  - Result: `PASS`; the tested local size-amplitude authority did not collapse the observed edge.

- **Phase 10 `trade_order_shuffle`** challenged whether the packet-authorized path-order surface was required for positive realized edge.
  - Result: `PASS`, with `path_dependency_detected = NO`; the tested local path-order authority did not collapse the observed edge.

- **Phase 11 temporal/bootstrap perturbations** challenged whether the observed edge was noise-fragile on the packet-authorized stability surface.
  - Result: both temporal and bootstrap verdicts are `PASS`, so the statistical-artifact explanation is not supported on that locked surface.

- **Phase 12 authority removals** challenged whether the packet-authorized local authorities were necessary for preservation.
  - Result: `UNIT_SIZE_REALIZED_SYSTEM`, `ORDER_NEUTRAL_REALIZED_SYSTEM`, and `UNIT_SIZE_ORDER_NEUTRAL_SYSTEM` all preserve positive realized edge, so the tested local authorities do not survive as critical explanations.

These falsification attempts do **not** prove a complete mechanism. They show only that the packet-authorized alternative explanations above fail to collapse or explain away the observed edge on the locked artifact surface.

## Residual uncertainty

- `execution_inefficiency` remains `UNATTESTED`, not `REJECTED`, because execution attribution remained `LIMITED_ARTIFACT_SURFACE`.
- `regime_independent_drift` remains `UNATTESTED`, not `REJECTED`, because the locked surface supports stability and rejects state dependence but does not directly attribute the residual edge to a drift mechanism after the limited execution/selection surfaces.
- `structural_market_microstructure` remains `UNATTESTED`, not `REJECTED`, because no packet-authorized market-microstructure artifact surface exists in the locked inputs.
- Phase 10 omits price-path-dependent execution counterfactuals and stronger per-trade selection-membership tests, so those mechanism classes remain constrained by artifact availability rather than disproven; the newly attested timestamp-level selection contrast does not by itself upgrade into causal selection authority.
- Phase 11 omits environmental sensitivity probes such as price noise and latency shifts under limited artifact surface, so stability remains scoped to the temporal/bootstrap lane only.
- Phase 12 omits selection-membership, fixed exits, deterministic entry shifts, MAE/MFE or intratrade path authority, signal inversion, and state-pocket ablations, so the minimal preserved system is identified only within the packet-authorized removal set.
- The identified origin hypothesis is therefore the **best-supported** synthesis within the locked artifact surface, not an exclusive causal proof.

## Final verdict

Within the packet-authorized artifact surface, the carried-forward evidence identifies one best-supported origin hypothesis and keeps all constrained surfaces explicitly constrained.

```text
EDGE ORIGIN REPORT STATUS:

- Origin hypothesis identified: YES
- Primary classification: emergent_system_behavior
- Signal-layer explanation supported: NO
- State-dependent explanation supported: NO
- Statistical artifact supported: NO

Verdict:
Edge origin is identified within the packet-authorized artifact surface.
```
