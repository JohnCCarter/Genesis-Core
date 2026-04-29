## Context Map

### Review intent

This slice performs a formal execution review of the already defined `RI P1 OFF parity governed rerun` execution plan.

It does **not** start the rerun. It evaluates whether execution may be approved next.

### Reviewed execution-plan provenance

| Item                           | Verified value                                                                                  | Status                        |
| ------------------------------ | ----------------------------------------------------------------------------------------------- | ----------------------------- |
| Reviewed branch                | `feature/regime-intelligence-cutover-analysis-v1`                                               | verified from local git state |
| Reviewed short SHA             | `1c2f38ad`                                                                                      | verified from local git state |
| Reviewed full SHA              | `1c2f38ad88723034b819b7844c69d138a7702086`                                                      | verified from local git state |
| Reviewed execution-plan packet | `docs/decisions/regime_intelligence/p1_off_parity/regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md` | present                       |

### Baseline Provenance Status

| Field                                      | Current review finding                                 | Execution impact                                                |
| ------------------------------------------ | ------------------------------------------------------ | --------------------------------------------------------------- |
| `window_spec_id`                           | `ri_p1_off_parity_v1`                                  | review target locked                                            |
| Expected canonical baseline reference path | `results/evaluation/ri_p1_off_parity_v1_baseline.json` | path is defined                                                 |
| Tracked approved baseline artifact present | `no / not verified from tracked repository state`      | blocks execution approval                                       |
| Verified baseline approval anchor present  | `not verified`                                         | blocks execution approval                                       |
| March sign-off docs present                | `yes`                                                  | supporting attestation only, not sufficient baseline provenance |
| Local/ignored evidence present             | `yes` (`logs/skill_runs.jsonl`)                        | insufficient as sole provenance source                          |
| Synthetic local FAIL artifact present      | `yes` (`ri_p1_off_parity_v1_ri-20260303-003.json`)     | must not be used as baseline/candidate/sign-off evidence        |

### Canonical artifact contract review

| Contract item                        | Review finding                                         | Status                                  |
| ------------------------------------ | ------------------------------------------------------ | --------------------------------------- |
| Canonical parity artifact path       | `results/evaluation/ri_p1_off_parity_v1_<run_id>.json` | defined and aligned with DoD            |
| Canonical baseline reference path    | `results/evaluation/ri_p1_off_parity_v1_baseline.json` | defined as reserved reference path only |
| Canonical vs supplemental separation | preserved                                              | acceptable                              |
| Required metadata bundle             | fully enumerated in execution plan                     | acceptable                              |
| `size_tolerance=1e-12`               | explicitly included                                    | acceptable                              |
| `mode=OFF`                           | explicitly included                                    | acceptable                              |

### Gate bundle review

| Gate area                  | Review finding             | Status     |
| -------------------------- | -------------------------- | ---------- |
| pre-commit / lint          | named                      | acceptable |
| smoke                      | named                      | acceptable |
| determinism replay         | named                      | acceptable |
| feature cache invariance   | named with concrete files  | acceptable |
| pipeline invariant         | named with exact selector  | acceptable |
| evaluate/source invariants | named with exact selectors | acceptable |
| comparator selectors       | named with exact selectors | acceptable |
| decision-row selector      | named with exact selector  | acceptable |
| skill checks               | named with exact commands  | acceptable |

### Execution-review result path

The execution plan is structurally complete enough for governance review, but execution remains blocked until baseline provenance is verified for `window_spec_id=ri_p1_off_parity_v1`.

### Non-negotiable review boundaries

- No execution approval without verified baseline provenance
- No rerun start in this slice
- No writes to canonical or supplemental evidence paths in this slice
- No reuse of `ri_p1_off_parity_v1_ri-20260303-003.json`
- No approval based solely on local/ignored evidence or on March sign-off docs without a verified baseline anchor
