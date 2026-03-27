# Legacy + RI research agent handoff

Date: 2026-03-27
Status: tracked / handoff reference
Lane: `run_intent: research_experiment`

## Read these first

1. `docs/governance/research_experiment_guardrail_v1_2026-03-27.md`
2. `docs/governance/legacy_ri_coordination_full_research_roadmap_2026-03-27.md`
3. `docs/governance/legacy_ri_research_phase0_baseline_2026-03-27.md`
4. `docs/governance/legacy_ri_research_phase1_experiment_map_2026-03-27.md`
5. `docs/governance/legacy_ri_research_return_to_experiment_map_selection_2026-03-27.md`

## Current state

- Legacy and RI remain separate strategy families.
- RI local retuning surfaces were already treated as exhausted at baseline lock.
- A bounded RI regime-calibration code experiment was executed and classified `degradation`.
- A bounded RI balanced-conflict decision experiment was executed and classified `degradation`.
- A bounded RI objective probe using the existing scoring surface was executed and classified `plateau`.
- Further RI slice iteration is paused for the current parameterization chain.

## Current conclusion

- The current RI formulation is locally exhausted for the presently opened line of inquiry.
- Do not open another RI slice from the current parameterization chain.

## Current next hypothesis class

- `B. Legacy internal next-hypothesis experiments`

## Why this is the next class

- It is orthogonal to the recent RI slices.
- It tests a different family instead of another RI-local mutation.
- It preserves family separation.
- It avoids opening coordination or router work before Legacy has been assessed on its own terms.

## What is not admissible now

- no new RI slice from the current chain
- no cross-family coordination opening yet
- no router opening yet
- no comparison, readiness, or promotion work
- no runtime default mutation

## Next admissible step

- Create one docs-only class-opening artifact for `B. Legacy internal next-hypothesis experiments`.
- That step must define the Legacy class only and must not open a concrete Legacy slice in the same move.
