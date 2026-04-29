# RI slice4 fresh rejected archive

- **Mode:** `RESEARCH`
- **Date:** `2026-03-24`
- **Candidate:** `slice4 fresh 2026-03-24 candidate config`
- **Disposition:** `rejected`
- **Reason:** reproduced plateau evidence at `0.28077646648091525` and did not provide promotable separation.
- **Constraint:** `NO BEHAVIOR CHANGE`

## Provenance summary

- **Run ID:** `run_20260324_132609`
- **Study name:** `ri_challenger_family_slice4_3h_2024_fresh_20260324_v1`
- **Best value:** `0.28077646648091525`
- **Validation carried with run:** `results/hparam_search/run_20260324_132609/validation/`
- **Evidence anchor:** `results/hparam_search/run_20260324_132609/run_meta.json` recorded the candidate config path and DB path before archival.
- **Dependency/discovery result:** no active automation, glob-visible selector, or runtime-facing reference requiring the pre-archive candidate locations was found; the active non-fresh slice-4 baseline and `results/hparam_search/run_20260324_132334/` remained in place.

## Archived path mapping

- Config
  - old: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_fresh_20260324_v1.yaml`
  - new: `archive/2026-03-24/ri_candidate_slice4_fresh_rejected/config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_fresh_20260324_v1.yaml`
- Run directory
  - old: `results/hparam_search/run_20260324_132609/`
  - new: `archive/2026-03-24/ri_candidate_slice4_fresh_rejected/results/hparam_search/run_20260324_132609/`
- Storage DB
  - old: `results/hparam_search/storage/ri_challenger_family_slice4_3h_2024_fresh_20260324_v1.db`
  - new: `archive/2026-03-24/ri_candidate_slice4_fresh_rejected/results/hparam_search/storage/ri_challenger_family_slice4_3h_2024_fresh_20260324_v1.db`

## Kept active in-place

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice5_2024_v1.yaml`
- `results/hparam_search/run_20260324_132334/`
- `archive/2026-03-24/ri_candidate_slice5_fresh_rejected/`

## Notes

This archive records a single-candidate disposition only. It does not alter runtime behavior, active optimizer authority, or canonical challenger-selection surfaces.
