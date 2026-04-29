# RI advisory environment-fit Phase 3 materially different surface inventory packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / current-state surface inventory decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only inventory/admissibility decision about whether any already materialized repository surface is materially different enough to reopen deterministic RI advisory-baseline work after the current capture-v2 surface failed exact-label authority; no runtime/config/test/results/artifact mutation.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide whether the repository already contains any materially different evidence surface candidate that could honestly reopen deterministic RI advisory-baseline work after same-surface authority failure, or whether lane-close is the required fallback under the current repository state.
- **Candidate:** `RI advisory environment-fit Phase 3 materially different surface inventory`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** no suitable existing skill; no skill-based process claim is made in this packet.

### Scope

- **Scope IN:**
  - `docs/decisions/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_packet_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**` modifications
  - `results/**` modifications
  - `artifacts/**` modifications
  - any new evidence generation
  - any hypothetical future surface design
  - any same-surface authority-recovery attempt
  - any runtime integration
  - any Phase 4 opening
  - any score implementation
- **Expected changed files:**
  - `docs/decisions/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_packet_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_2026-04-17.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_packet_2026-04-17.md docs/analysis/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_2026-04-17.md`

### Allowed evidence inputs

#### Candidate-surface evidence

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_strategy_family_bridge_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_bundle_surface_reliability_opening_2026-04-17.md`
- `artifacts/research_ledger/artifacts/ART-2026-0001.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/materialized_exact_label_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/manifest.json`

#### Provenance / index aids only

- `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`
- `tmp/ri_advisory_environment_fit_reliability_exact_label_authority_preflight_20260417.py`

These provenance aids may support origin tracing only.
They must not be treated as candidate evidence surfaces by themselves.

### Required decision questions

The memo must answer at minimum:

1. does the repository already contain any candidate surface that is materially different from the exhausted capture-v2 row surface for authority-bearing continuation?
2. for each plausible already materialized candidate, does it satisfy:
   - co-resident RI observability and authority
   - deterministic exact join completeness
   - RI-only / advisory-only boundaries
   - contradiction-year usefulness?
3. if no currently materialized candidate satisfies those conditions cleanly, is lane-close now the required fallback under the current repository state?
4. if one candidate survives, what is the narrowest next governed question — without authorizing implementation from this packet alone?

### Required boundary statements

The memo must state explicitly that:

- only already materialized repository-local surfaces may be evaluated; no hypothetical future surface counts in this inventory
- `tmp/**` scripts and research-ledger records are provenance/index aids only and are not admissible evidence surfaces by themselves
- repackaging or re-describing the current bundle/capture-v2 surface does not make it materially different for the already closed authority question
- no legacy or cross-family comparison surface may be reframed as RI-native authority without a separate explicit governance exception
- if no candidate survives, lane-close is required only under the current repository state and current constraints, not as a permanent impossibility claim
- this packet does not authorize implementation, new artifacts, Phase 4, runtime readiness, or baseline reopening

### Stop Conditions

- any wording that reopens same-surface continuation on the exhausted capture-v2 row surface
- any wording that treats bundle/capture-v2 repackaging as materially different for the already closed question
- any wording that treats `tmp/**` or ledger metadata as a candidate evidence surface by itself
- any wording that upgrades a legacy/cross-family authority chain into RI-native authority without explicit exception
- any wording that authorizes implementation, new evidence generation, Phase 4, score implementation, or runtime readiness from this packet alone
- any wording that states lane-close as permanent impossibility instead of a current-state fallback

## Bottom line

This packet authorizes one docs-only inventory/admissibility decision about already materialized candidate surfaces and nothing more.
It does not authorize new artifacts, new captures, same-surface recovery work, Phase 4, runtime integration, or baseline implementation.
