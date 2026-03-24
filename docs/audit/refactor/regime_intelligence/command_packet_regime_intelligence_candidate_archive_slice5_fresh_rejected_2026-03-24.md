## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `tooling`
- **Risk:** `MED` — why: archive/triage slice touches one fresh candidate config path plus its local result/storage artifacts; must preserve traceability while leaving canonical RI baselines and legacy control surfaces untouched
- **Objective:** Archive only the rejected `slice5 fresh` RI candidate artifacts from 2026-03-24 while keeping canonical family baselines, the legacy control run, and the canonical slice-5 config path active in-place.
- **Default constraint:** `NO BEHAVIOR CHANGE`
- active runtime/config authority, optimizer discovery, and challenger selection semantics must remain unchanged
- classification is limited to archive disposition for this candidate history: rejected for promotion due to reproduced plateau evidence; this packet does not change runtime strategy behavior, active optimizer authority, or canonical challenger selection

### Skill Usage

- repo-local skill reference: `.github/skills/repo_clean_refactor.json`
- usage status: `införd` skill already present in repository; this slice follows its additive-only cleanup, inventory-first, and no-behavior-change discipline

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_candidate_archive_slice5_fresh_rejected_2026-03-24.md`
  - new archive manifest under `archive/2026-03-24/ri_candidate_slice5_fresh_rejected/`
  - move `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_fresh_20260324_v1.yaml`
  - move `results/hparam_search/run_20260324_140103/`
  - move `results/hparam_search/storage/ri_challenger_family_slice5_3h_2024_fresh_20260324_v1.db`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_fresh_20260324_v1.yaml`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`
  - `results/hparam_search/run_20260324_132609/`
  - `results/hparam_search/run_20260324_132334/`
  - `results/hparam_search/storage/ri_challenger_family_slice4_3h_2024_fresh_20260324_v1.db`
  - `results/hparam_search/storage/optuna_tBTCUSD_3h_explore_validate_2024_2025_v2.db`
  - any champion/default/promotion semantics
- **Expected changed files:**
  - 2 markdown files
  - 1 moved candidate config
  - 1 moved run directory
  - 1 moved storage DB file
- **Max files touched:** `5` logical paths plus moved directory contents

### Classification intent

- `slice5 fresh 2026-03-24 candidate config` -> `rejected`
  - reason: the fresh candidate config reproduced the slice-4 plateau (`0.28077646648091525`), did not improve separation, and is not promotable; canonical slice-5 family definition remains the non-fresh config in-place for traceability.

### Evidence summary

- The fresh candidate config's run metadata points only to:
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_fresh_20260324_v1.yaml`
  - `results/hparam_search/run_20260324_140103/`
  - `results/hparam_search/storage/ri_challenger_family_slice5_3h_2024_fresh_20260324_v1.db`
- Repo search found no active documentation or canonical config surfaces depending on the fresh slice-5 path outside:
  - the fresh config itself
  - its run directory contents
  - the archive command packet being added here

### Gates required

- verify exact paths exist before move
- verify canonical active reference paths remain present after move
- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_candidate_archive_slice5_fresh_rejected_2026-03-24.md archive/2026-03-24/ri_candidate_slice5_fresh_rejected/README.md`
- `get_errors` on changed markdown files

### Stop Conditions

- any canonical non-fresh RI slice file would need to be moved
- any path under `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**` would need editing
- any external reference requires the fresh slice-5 candidate path to remain active
- archive manifest cannot clearly state `rejected` and the preserved active surfaces
- move would cross outside repository root

### Output required

- **Implementation Report**
- exact archived paths
- exact kept-active paths
- classification summary (`rejected`)
- validation outcomes for manifest/packet files
