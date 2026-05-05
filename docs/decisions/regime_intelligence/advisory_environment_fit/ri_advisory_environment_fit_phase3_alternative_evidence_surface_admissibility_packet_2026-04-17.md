# RI advisory environment-fit Phase 3 alternative evidence surface admissibility packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / next-surface decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only decision about whether the roadmap may continue after the current capture-v2 surface was exhausted for same-surface exact-label-authority work; no runtime/config/test/results regeneration.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide whether the only admissible continuation is a materially different evidence surface, define what that surface must provide, and specify whether the lane should close if no such surface can be justified cleanly.
- **Candidate:** `RI advisory environment-fit Phase 3 alternative evidence surface admissibility`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_packet_2026-04-17.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - any new authority-recovery attempt on current capture-v2 rows
  - any runtime integration
  - any transition promotion
  - any Phase 4 opening
  - any new evidence-bundle or artifact generation
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_packet_2026-04-17.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_2026-04-17.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_packet_2026-04-17.md docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_2026-04-17.md`

### Allowed evidence inputs

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_dirty_research_exact_label_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/join_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/label_authority_audit.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/boundary_manifest.json`

### Required decision questions

The memo must answer at minimum:

1. has the current capture-v2 surface been fully exhausted for same-surface Phase 3 authority-bearing continuation?
2. is a materially different evidence surface now the only admissible route if the roadmap is to continue?
3. what exact properties must any new surface satisfy before renewed deterministic baseline or authority-bearing discussion is admissible?
4. if no such surface can be identified cleanly from the lane's current constraints, should the lane close instead of drifting?

### Required boundary statements

The memo must state explicitly that:

- the current capture-v2 surface remains closed for same-surface exact-label-authority continuation
- `exact_label_authority = false` remains authoritative on that surface
- `phase4_opening = false` remains authoritative
- a new surface must not rely on dirty-research heuristic labels as authority
- a new surface must not reopen runtime authority, transition promotion, or default changes by implication

### Stop Conditions

- any wording that treats the current capture-v2 surface as still partially open for authority recovery
- any wording that treats local exact-authority overlap as sufficient basis for renewed same-surface continuation
- any wording that opens Phase 4 or runtime readiness from this decision alone
- any wording that authorizes artifact generation or implementation from this packet alone

## Bottom line

This packet authorizes one docs-only decision about whether the roadmap may continue only via a materially different evidence surface.
It does not authorize another recovery attempt, Phase 4, runtime integration, or new evidence generation.
