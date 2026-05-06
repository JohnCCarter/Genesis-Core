# Regime-independent drift residual hypothesis — packet

Date: 2026-04-02
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical residual snapshot / frozen as docs-only gap / no active packet authority`

> Current status note:
>
> - HISTORICAL 2026-05-05: this file records the bounded packet that froze `regime_independent_drift` as a residual docs-only gap on `feature/ri-role-map-implementation-2026-03-24`, not an active packet authority on `feature/next-slice-2026-05-05`.
> - Its historical closeout role is reflected in `docs/analysis/diagnostics/regime_independent_drift_artifact_gap_2026-04-02.md` and in the current top status note of `handoff.md`.
> - Preserve this file as historical residual-governance provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: the residual class `regime_independent_drift` can easily be overclaimed by confusing temporal stability with a resolved drift mechanism; this slice must remain observational and fail closed on unsupported causal language.
- **Required Path:** `Quick`
- **Objective:** Freeze the next admissible lane for the residual class `regime_independent_drift` by documenting what the current locked artifact surface already supports, what it still cannot attest, and what minimum future evidence would be needed before stronger drift claims become admissible.
- **Candidate:** `baseline_current` residual drift lane
- **Base SHA:** `4fc74408`

### Scope

- **Scope IN:**
  - `docs/decisions/diagnostic_campaigns/regime_independent_drift_residual_packet_2026-04-02.md`
  - `docs/analysis/diagnostics/regime_independent_drift_artifact_gap_2026-04-02.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all files under `scripts/`
  - all files under `results/`
  - any runtime/config authority changes
  - any new backtest or trace reruns
  - any edits to locked Phase 9–14 artifacts
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/regime_independent_drift_residual_packet_2026-04-02.md`
  - `docs/analysis/diagnostics/regime_independent_drift_artifact_gap_2026-04-02.md`
- **Max files touched:** `2`

### Constraints

- docs-only; no code changes
- no new evidence claims beyond the currently locked artifact surface
- no weakening of the current Phase 9 `edge is not state-dependent` conclusion
- no weakening of the current Phase 11 `stable` conclusion
- `UNATTESTED` must remain distinct from `REJECTED`
- this slice may define the next admissible drift lane, but may not pretend that lane is already implemented

### Packet-authorized source surface

The memo may cite only these already locked artifact facts:

- `phase9_state_isolation/state_edge_matrix.json`
- `phase10_edge_origin_isolation/execution_attribution.json`
- `phase10_edge_origin_isolation/selection_attribution.json`
- `phase11_edge_stability/edge_stability.json`
- `phase13_edge_classification/edge_classification.json`
- `EDGE_ORIGIN_REPORT.md`

### Required memo outcomes

The memo is complete only if it does all of the following:

1. states exactly why `regime_independent_drift` remains `UNATTESTED`
2. distinguishes clearly between:
   - what Phase 9 already ruled out
   - what Phase 11 already supports
   - what Phase 10 still limits
3. explains why temporal stability is not the same thing as an attested drift mechanism
4. lists what minimum future evidence would be needed before stronger drift claims become admissible
5. defines the next admissible lane in one of two forms:
   - a continued docs-only closeout if the user wants to keep the class unresolved, or
   - a future stricter evidence lane if the user wants to resolve the class

### Stop conditions

- any need to touch `src/`, `tests/`, `config/`, `scripts/`, or `results/`
- any claim that `regime_independent_drift` is already supported or rejected on the current surface
- any claim that Phase 11 temporal/bootstrap stability alone proves a drift mechanism
- any softening of the locked Phase 9 or Phase 14 wording
- any widening beyond the locked artifact set above

### Output required

- one docs-only governance packet
- one short analysis memo freezing the current drift gap and the next admissible lane

## Bottom line

This slice does not try to solve `regime_independent_drift`.
It freezes the exact reason the class remains unresolved and defines the smallest safe next step.
