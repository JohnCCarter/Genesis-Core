# current_atr 900 vs 1435 policy handoff — 2026-04-16

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only synthesis of already generated research artifacts; no replay, no runtime/config changes, no artifact regeneration
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** capture a deployment-policy handoff comparing the already packeted `current_atr >= 900` and `current_atr >= 1435.209570` candidates using existing evidence only, while preserving the execution-basis caveats needed for later review
- **Candidate:** `current_atr 900 vs 1435 policy handoff`
- **Base SHA:** `5596a904ffd5c96b4f0638c2d025c1eee2f6387e`

### Scope

- **Scope IN:**
  - `docs/governance/current_atr_900_vs_1435_policy_handoff_2026-04-16.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `tmp/**`
  - `results/**`
  - `config/**`
  - `.github/skills/**`
  - any replay script, runtime default, config-authority path, or artifact payload
- **Expected changed files:**
  - `docs/governance/current_atr_900_vs_1435_policy_handoff_2026-04-16.md`
- **Max files touched:** `1`

### Gates required

- `pre-commit run --files docs/governance/current_atr_900_vs_1435_policy_handoff_2026-04-16.md`

### Stop Conditions

- any need to rerun replay or regenerate artifacts
- any need to edit `src/`, `tests/`, `tmp/`, `results/`, or `config/`
- any attempt to convert research evidence into a runtime/default recommendation
- any wording that hides the mixed execution-basis caveat between the cited slices

### Output required

- `docs/governance/current_atr_900_vs_1435_policy_handoff_2026-04-16.md`
- **Implementation Report** — delivered in chat only

## Purpose

This handoff exists because the repository now has three relevant current-ATR evidence slices, but no single governance note that states plainly how `900` and `1435.209570` compare as candidate policy directions:

- dedicated validation of `current_atr >= 900`
- discovery-to-freeze environment profiling for `900`
- dedicated policy validation of `current_atr >= 1435.209570`

The goal here is not to reopen replay or to pick a runtime default.
The goal is to leave a clean review handoff for any later, separate deployment-policy packet.

## Evidence basis

### Locked sources

- `900` dedicated validation:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/closeout.md`
- `900` environment profile:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/closeout.md`
- `1435` policy validation:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/replay_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/closeout.md`
  - `docs/governance/current_atr_1435_policy_validation_packet_2026-04-16.md`

### Execution-basis caveat

- The `900` dedicated validation and `900` environment-profile artifacts were generated on `8e23ddb45d08784e8a8a340f83334f5842505e0e`.
- The `1435` policy-validation artifacts were generated on the explicitly rebased execution basis `2ee708c9a85a1f3b14dd597b8e2155c5847e91c5`.
- The later docs-only remediation commit `5596a904ffd5c96b4f0638c2d025c1eee2f6387e` preserved that distinction; it did not regenerate replay outputs.

This handoff must therefore be read as a synthesis of already generated packet conclusions, not as a single same-basis rerun across all cited artifacts.

## Comparison snapshot

### Discovery-aligned 2024 window

| Candidate | Score | Total PnL | Return | Max DD | PF | Override-active rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline `0.90` | `0.4398` | `281.5344` | `2.82%` | `1.76%` | `2.51` | `0` |
| candidate `900` | `0.4507` | `318.4374` | `3.18%` | `1.80%` | `2.59` | `83` |
| candidate `1435.209570` | `0.4474` | `296.6194` | `2.97%` | `1.76%` | `2.56` | `24` |

Observations:

- `900` is stronger than `1435` on 2024 score and total PnL.
- `1435` remains above baseline while using a much narrower active set than `900`.
- `1435` improves max drawdown slightly relative to `900`, but gives back part of the 2024 uplift that made `900` attractive.

### Blind 2025 window

| Candidate | Score | Total PnL | Return | Max DD | PF | Override-active rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline `0.90` | `0.1944` | `-165.6252` | `-1.66%` | `3.41%` | `1.52` | `0` |
| candidate `900` | `0.1988` | `-172.7078` | `-1.73%` | `3.71%` | `1.53` | `155` |
| candidate `1435.209570` | `0.2018` | `-151.2325` | `-1.51%` | `3.46%` | `1.55` | `42` |

Observations:

- `1435` is stronger than `900` on the blind 2025 score and total PnL.
- `1435` is materially narrower than `900` on active-set size (`42` vs `155`).
- `900` remains above baseline on score, but it gives up selectivity and underperforms `1435` on the blind window.

### Drift and selectivity notes

- Both candidate slices reported zero action drift and zero reason drift in their direct comparisons; the observed differences are size/activation effects, not new action patterns.
- `1435` is a strict subset style candidate relative to `900` in the cited validation output:
  - 2024 shared active rows: `24`, `900`-only: `59`, `1435`-only: `0`
  - 2025 shared active rows: `42`, `900`-only: `113`, `1435`-only: `0`

## Policy reading

This is the narrowest defensible synthesis from the cited evidence:

1. `900` remains the stronger bounded candidate on the discovery-aligned 2024 window.
2. `1435` remains the stronger and narrower candidate on the blind 2025 window.
3. Neither candidate dominates the other across both windows strongly enough to justify default promotion from this handoff alone.
4. The trade-off is now explicit:
   - prefer `900` if the review criterion is stronger retained 2024 uplift while staying bounded relative to the broader selective seam
   - prefer `1435.209570` if the review criterion is narrower activation with better blind-window behavior

## Recommended governance stance

- Keep both candidates in research status.
- Do **not** describe this handoff as a deployment decision.
- Do **not** describe `1435` as the same-basis continuation of the original packet draft; preserve the rebased execution-basis wording.
- If a later runtime proposal is opened, it should be a separate packeted slice with default unchanged and an explicit review criterion for why `900` or `1435` is being trialed first.

## Suggested next packet, if needed later

If the repo wants to move beyond research-only comparison, the next explicit packet should answer only one question:

> Under a guarded, default-off rollout criterion, which candidate should be trialed first: the stronger 2024 bounded candidate (`900`) or the narrower blind-window candidate (`1435.209570`)?

That future slice should remain separate from this handoff and should not reuse this file as proof of runtime readiness.

## Evidence discipline

- This note is observational replay research synthesis only.
- It does not change runtime defaults.
- It does not regenerate artifacts.
- It does not recommend direct deployment.
