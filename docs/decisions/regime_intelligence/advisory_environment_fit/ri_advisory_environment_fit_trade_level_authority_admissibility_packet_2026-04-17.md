# RI advisory environment-fit trade-level authority admissibility packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / lane-pivot admissibility decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only decision about whether RI advisory work may pivot from exhausted exact row-level authority recovery to a new trade-level-authority / entry-row-scoring lane; no runtime/config/test/results/artifact mutation.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide whether a new research lane may define authority primarily at the trade-outcome level while preserving entry rows as the scoring surface, allowing explicit partial coverage and probabilistic mapping, without pretending to recover the old exact row-level authority contract.
- **Candidate:** `RI advisory environment-fit trade-level authority admissibility`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** no suitable existing skill; no skill-based process claim is made in this packet.

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - `artifacts/**`
  - any exact-row-level authority recovery attempt
  - any trade-level label implementation
  - any probabilistic mapping implementation
  - any deterministic baseline implementation
  - any ML/model work
  - any runtime integration
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_packet_2026-04-17.md docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_trade_level_authority_admissibility_2026-04-17.md`

### Allowed evidence inputs

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_provisional_evaluation_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_bundle_surface_reliability_opening_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_packet_2026-04-17.md`
- `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_evidence_capture_v2_packet_2026-04-17.md`

### Required decision questions

The memo must answer at minimum:

1. is the exact row-level authority-recovery path now sufficiently exhausted that a new lane question is required rather than another same-surface continuation?
2. is it admissible in principle to define authority primarily at the trade-outcome level while keeping entry rows as the pre-entry scoring surface?
3. may probabilistic or partial mapping be considered in a later lane without pretending to recover the old exact Phase 2 row-level contract?
4. what exact boundaries must remain non-negotiable if that new lane opens?
5. what is the narrowest next governed step if the pivot is admissible?

### Required boundary statements

The memo must state explicitly that:

- `NOT_RECOVERED` remains authoritative for the old exact row-level authority question
- the new lane, if opened, is a new research question and not a continuation claiming to have repaired the old exact contract
- trade outcomes may become the primary authority surface only if entry rows remain the scoring-time surface
- explicit partial coverage and uncertainty are allowed only if they are reported honestly and not reframed as complete authority
- ML remains out of scope until a deterministic baseline exists in the new lane
- `2025` remains a mandatory contradiction-year check
- this packet does not authorize implementation, runtime integration, Phase 4, or score promotion

### Stop Conditions

- any wording that claims the old exact row-level authority problem has been solved
- any wording that treats probabilistic mapping as equivalent to exact Phase-2-faithful row labels
- any wording that removes entry rows from the scoring-time surface altogether
- any wording that opens ML before a deterministic baseline exists
- any wording that weakens the `2025` contradiction-year requirement
- any wording that authorizes implementation, runtime integration, or baseline scoring from this packet alone

## Bottom line

This packet authorizes one docs-only admissibility decision about opening a new trade-level-authority RI research lane and nothing more.
It does not authorize implementation, ML, runtime changes, or a relabeling of the old exact row-level authority failure as success.
