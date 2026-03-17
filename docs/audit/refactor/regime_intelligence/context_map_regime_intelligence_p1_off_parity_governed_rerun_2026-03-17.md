## Context Map

### Slice intent

This slice defines the governance contract for a future `RI P1 OFF parity governed rerun`.

It does **not** execute the rerun. It prepares a reproducible evidence chain so that a later execution slice can restore sign-off evidence under the frozen spec `ri_p1_off_parity_v1`.

### Frozen anchors that must remain unchanged

| Anchor                                                   | Why it matters                                                                 |
| -------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `docs/ideas/REGIME_INTELLIGENCE_DOD_P1_P2_2026-02-27.md` | locks the P1 OFF parity contract, required fields, and frozen window semantics |
| `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`   | canonical machine-readable parity artifact location must remain normative      |
| `tools/compare_backtest_results.py`                      | comparator contract and artifact field semantics                               |
| `scripts/run/run_backtest.py`                            | decision-row capture path for future candidate generation                      |
| `.github/skills/ri_off_parity_artifact_check.json`       | repo-specific RI artifact validation anchor                                    |

### Current evidence state inherited from the analysis slice

| Evidence anchor                                               | Current state                                      | Implication for governed rerun                       |
| ------------------------------------------------------------- | -------------------------------------------------- | ---------------------------------------------------- |
| `results/evaluation/ri_p1_off_parity_v1_ri-20260303-003.json` | synthetic/local test `FAIL`, not sign-off evidence | must not be reused as baseline or candidate evidence |
| `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md`                  | documents March PASS chain                         | useful human attestation, not sufficient alone       |
| `logs/skill_runs.jsonl`                                       | local-only PASS clue for `run_id=c8c3b77cd2c1`     | not tracked; cannot serve as sole provenance         |
| GitHub Actions run `22663511442`                              | retained only `bandit-report`                      | no CI-retained parity artifact bundle exists         |

### Planned artifact role map for future execution

| Role                                 | Planned path                                                                                        | Role type                                                    | Required status before sign-off                          |
| ------------------------------------ | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------- |
| Canonical parity artifact            | `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`                                              | normative / canonical                                        | must exist and satisfy frozen P1 OFF contract            |
| Explicit baseline artifact reference | `results/evaluation/ri_p1_off_parity_v1_baseline.json`                                              | normative reference path used by canonical artifact metadata | must be explicitly defined and approved before execution |
| Supplemental baseline rows evidence  | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_baseline_rows_<run_id>.json`  | supplemental governance evidence                             | must hash-link to approved baseline input                |
| Supplemental candidate rows evidence | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_<run_id>.json` | supplemental governance evidence                             | must hash-link to generated candidate input              |
| Supplemental rerun manifest          | `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_manifest_<run_id>.json`       | supplemental governance evidence                             | must reference canonical artifact path and SHA256        |

### Reviewable input requirements for future execution

- explicit `symbol`, `timeframe`, `start_utc`, `end_utc`
- explicit baseline approval anchor
- explicit candidate generation command/path
- explicit runtime config source
- explicit compare-tool path
- explicit branch + `git_sha`
- explicit environment freeze note including `GENESIS_FAST_HASH=0`
- reviewable input files that are not retained only under ignored paths

### Missing prerequisites before execution may begin

| Missing prerequisite                        | Why it matters                                                      |
| ------------------------------------------- | ------------------------------------------------------------------- |
| approved baseline provenance anchor         | without it, the rerun cannot claim a valid governance baseline      |
| explicit candidate input retention plan     | without it, PASS/FAIL cannot be replayed independently              |
| canonical vs supplemental SHA-link contract | prevents audit drift between generated output and retained evidence |
| full gate bundle definition                 | sign-off rerun must include more than artifact generation alone     |

### Non-negotiable boundaries

- No runtime logic changes
- No default-cutover
- No champion or config authority changes
- No execution in this prep slice
- No replacement of the canonical artifact location
- No ignored-only evidence chain for future sign-off
