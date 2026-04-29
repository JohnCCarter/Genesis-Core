## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `tooling`
- **Risk:** `MED` — why: archive/triage slice touches one fresh candidate config path plus its local result/storage artifacts; must preserve traceability while leaving canonical RI baselines and control surfaces untouched
- **Required Path:** `Full`
- **Objective:** Archive only the rejected `slice4 fresh` RI candidate artifacts from 2026-03-24 while keeping the active non-fresh slice-4 baseline, canonical family baselines, and the legacy control run in-place.
- **Candidate:** `slice4 fresh 2026-03-24 candidate config`
- **Base evidence SHA:** `835c9ed46b9fdeb7584e2a07dc88d4d3f6f3cac9`
- **Default constraint:** `NO BEHAVIOR CHANGE`
- active runtime/config authority, optimizer discovery, and challenger selection semantics must remain unchanged
- classification is limited to archive disposition for this candidate history: rejected for promotion due to reproduced plateau evidence; this packet does not change runtime strategy behavior, active optimizer authority, or canonical challenger selection

### Skill Usage

- repo-local skill reference: `.github/skills/repo_clean_refactor.json`
- usage status: `införd` skill already present in repository; this slice follows its additive-only cleanup, inventory-first, and no-behavior-change discipline

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_candidate_archive_slice4_fresh_rejected_2026-03-24.md`
  - new archive manifest under `archive/2026-03-24/ri_candidate_slice4_fresh_rejected/`
  - move `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_fresh_20260324_v1.yaml`
  - move `results/hparam_search/run_20260324_132609/`
  - move `results/hparam_search/storage/ri_challenger_family_slice4_3h_2024_fresh_20260324_v1.db`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`
  - `results/hparam_search/run_20260324_132334/`
  - `results/hparam_search/storage/optuna_tBTCUSD_3h_explore_validate_2024_2025_v2.db`
  - `archive/2026-03-24/ri_candidate_slice5_fresh_rejected/**`
  - any champion/default/promotion semantics
- **Expected changed files:**
  - 2 markdown files
  - 1 moved candidate config
  - 1 moved run directory
  - 1 moved storage DB file
- **Max files touched:** `5` logical paths plus moved directory contents

### Classification intent

- `slice4 fresh 2026-03-24 candidate config` -> `rejected`
  - reason: the fresh candidate config reproduced the same plateau score (`0.28077646648091525`) seen in the parallel fresh challenger evidence and is not promotable; canonical slice-4 family definition remains the non-fresh config in-place for traceability.

### Evidence summary

- `results/hparam_search/run_20260324_132609/run_meta.json` points only to:
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_fresh_20260324_v1.yaml`
  - `results/hparam_search/run_20260324_132609/`
  - `results/hparam_search/storage/ri_challenger_family_slice4_3h_2024_fresh_20260324_v1.db`
- run metadata records:
  - `best_value: 0.28077646648091525`
  - `study_name: ri_challenger_family_slice4_3h_2024_fresh_20260324_v1`
  - validation enabled with top-5 validation directory under `results/hparam_search/run_20260324_132609/validation`
- repo search has not surfaced any canonical runtime/config authority path that requires the fresh slice-4 candidate path to remain active outside the candidate config, its run directory, and its storage DB.
- dependency/discovery check completed for the moved fresh-candidate paths and identifiers; no active automation, glob-visible selector, or runtime-facing reference requiring the pre-archive locations was found, and the active non-fresh slice-4 baseline plus `results/hparam_search/run_20260324_132334/` remained in place.

### Gates required

- verify exact paths exist before move
- verify canonical active reference paths remain present after move
- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_candidate_archive_slice4_fresh_rejected_2026-03-24.md archive/2026-03-24/ri_candidate_slice4_fresh_rejected/README.md`
- `get_errors` on changed markdown files
- targeted repo search for exact dependencies on:
  - `tBTCUSD_3h_ri_challenger_family_slice4_2024_fresh_20260324_v1.yaml`
  - `ri_challenger_family_slice4_3h_2024_fresh_20260324_v1`
  - `run_20260324_132609`
  - `ri_challenger_family_slice4_3h_2024_fresh_20260324_v1.db`
  - discovery/glob usage over `config/optimizer/3h/ri_challenger_family_v1/*.yaml`
- targeted selectors after move:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/governance/test_pipeline_fast_hash_guard.py`
  - `tests/utils/test_feature_cache.py`

### Stop Conditions

- any canonical non-fresh RI slice file would need to be moved
- any path under `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**` would need editing
- any external reference requires the fresh slice-4 candidate path to remain active
- any active automation, batch discovery, manifest flow, or replay process depends on the fresh slice-4 candidate path or glob-visible presence under `config/optimizer/3h/ri_challenger_family_v1/`
- archive manifest cannot clearly state `rejected` and the preserved active surfaces
- move would cross outside repository root

### Output required

- **Implementation Report**
- exact archived paths
- exact kept-active paths
- classification summary (`rejected`)
- validation outcomes for manifest/packet files
