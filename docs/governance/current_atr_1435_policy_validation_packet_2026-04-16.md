# current_atr 1435 policy validation packet — 2026-04-16

## Mode / intent

- Mode: `RESEARCH`
- Category: `tooling`
- Constraint: `NO BEHAVIOR CHANGE`
- Purpose: run a read-only replay validation of the narrowed runtime-implementable policy candidate `current_atr >= 1435.209570` with `high_vol_multiplier_override = 1.0`, compared against baseline `0.90`, the already packeted `900` candidate, and an always-`1.00` anchor.

## Why this slice exists

- The completed observational environment-profile slice for the `900` candidate produced a first frozen discovery rule that survived `2025` freeze-only validation:
  - `zone_atr >= 1435.209570`
- That same signal has an entry-available runtime alias in the recorded artifacts:
  - `current_atr_used >= 1435.209570`
- The next step is not more discovery. The next step is direct replay validation of whether a narrower runtime policy using the existing `current_atr` seam at `1435.209570` behaves credibly when compared with:
  - baseline `0.90`
  - current bounded candidate `900`
  - always-`1.00`

## Scope IN

- `docs/governance/current_atr_1435_policy_validation_packet_2026-04-16.md`
- `tmp/current_atr_1435_policy_validation_20260416.py`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/candidate_1435_cfg.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/replay_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/manifest.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/closeout.md`

## Scope OUT

- `src/**`
- `tests/**`
- `scripts/**`
- `.github/skills/**`
- `.github/agents/**`
- `docs/governance_mode.md`
- `config/runtime.json`
- `config/**` except read-only use of already existing input artifacts explicitly cited in this packet
- `config/strategy/**`
- `logs/**` except existing append-only tooling output that may be produced by validation commands
- env/config-authority paths and semantics
- any runtime default, route, config-authority, backtest engine, optimizer, or strategy logic changes

## Evidence basis

### Rebased execution basis amendment

- This packet is amended to run on clean HEAD `2ee708c9a85a1f3b14dd597b8e2155c5847e91c5`.
- Prior packet pin: `8e23ddb45d08784e8a8a340f83334f5842505e0e`.
- This is not the same execution basis as the original packet draft; results from this run apply to the rebased HEAD above.
- Intervening commits between the prior pin and the rebased HEAD:
  - `f161afe0` — `feat: add execution proxy missingness diagnostics`
  - `2b8c4e69` — `feat: add research-only decision and sizing override seams`
  - `d5264ff4` — `feat: add packeted current-atr research validation tooling`
  - `2ee708c9` — `style: format mcp.json for improved readability`

- Prior candidate config anchor:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`
- Prior dedicated 900 replay-validation skeleton:
  - `tmp/current_atr_selective_900_validation_20260415.py`
- Observational discovery evidence:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/closeout.md`
- HEAD pin for this amended execution basis:
  - `2ee708c9a85a1f3b14dd597b8e2155c5847e91c5`

## Implementation shape

### Relevant repo-local skills

This slice explicitly uses these repo-local skills as governing specs for execution discipline:

- `.github/skills/python_engineering.json`
- `.github/skills/genesis_backtest_verify.json`
- `.github/skills/ri_off_parity_artifact_check.json`

Create one temporary research script:

- `tmp/current_atr_1435_policy_validation_20260416.py`

The script may reuse the structure of the prior `900` replay-validation script, but must remain scoped to this slice.

Before replay starts, the script must verify that `git rev-parse HEAD` resolves to `2ee708c9a85a1f3b14dd597b8e2155c5847e91c5` and fail closed if the working tree is on a different commit.

Before replay starts, the script must also:

- capture `git status --short` preflight state
- fail closed if there are pre-existing modified or untracked paths outside Scope IN
- fail closed if the approved output directory already contains unexpected files

### Required replay variants

The script must build and compare exactly these four variants:

1. `baseline_090`
   - no research override enabled
   - canonical high-vol multiplier remains `0.90`
2. `candidate_900`
   - reuse the prior research seam
   - `current_atr_threshold = 900.0`
   - `high_vol_multiplier_override = 1.0`
3. `candidate_1435`
   - same seam and override mechanism as `candidate_900`
   - `current_atr_threshold = 1435.209570`
   - `high_vol_multiplier_override = 1.0`
4. `always_100`
   - same seam enabled
   - threshold set so the override is always active for the tested rows
   - effective high-vol multiplier = `1.0`

### Required dataset windows

- Discovery-aligned window: `2024-01-02` through `2024-12-31`
- Blind validation window: `2025-01-01` through `2025-12-31`

### Required outputs

Write only the approved files under:

- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/`

Artifacts:

1. `candidate_1435_cfg.json`
   - reproducibility config for the narrowed candidate
2. `replay_summary.json`
   - machine-readable rollup of the four-way comparison across both windows
3. `manifest.json`
   - provenance, command/env details, output allowlist, pre/post containment snapshot, unexpected-events list
4. `closeout.md`
   - human-readable conclusion and recommendation status

Artifact filenames must remain exactly as listed above; do not introduce longer auxiliary filenames in the output folder.

## Allowed mechanics

- In-process Python replay only
- Reuse existing repository code paths and previously generated read-only research artifacts as inputs
- Clone configs in memory or write only the explicitly allowed artifact config
- Capture deterministic comparison summaries, including at minimum:
  - total pnl
  - trade count
  - win rate
  - profit factor when available
  - delta vs baseline
  - delta vs `candidate_900`
  - agreement/disagreement counts on the override activation set, or explicit `not_derivable` with a short reason

## Forbidden mechanics

- no edits under `src/` or `tests/`
- no mutation of checked-in runtime configs
- no default promotion
- no discovery-rule mining beyond evaluating the already frozen `1435.209570` candidate as a runtime policy surrogate
- no parameter sweep expansion
- no new dependency installation

## Containment requirements

The script must record pre/post snapshots and fail closed in the manifest if unexpected mutations occur outside the approved output folder. At minimum include checks for:

- `config/runtime.json`
- `config/strategy/`
- `logs/config_audit.jsonl`
- `cache/`
- the approved output directory for this slice

If cache files change as a normal side effect of read-only replay, they must be recorded explicitly and assessed in the manifest rather than ignored.

No mutation outside the approved output directory is allowed except:

- explicitly recorded append-only changes to `logs/config_audit.jsonl`
- explicitly recorded cache side effects assessed in `manifest.json`

Any other mutated path is a containment failure.

## Validation commands

Use the workspace Python environment and canonical research env flags.

The script must record the exact replay-affecting env values in `manifest.json` and fail closed if any required canonical value is absent. At minimum record:

- `GENESIS_RANDOM_SEED`
- `GENESIS_FAST_WINDOW`
- `GENESIS_PRECOMPUTE_FEATURES`
- `GENESIS_MODE_EXPLICIT`
- `GENESIS_FAST_HASH`
- `SYMBOL_MODE`

### Static / hygiene

- file-scoped `pre-commit` or equivalent Python formatting/lint check covering only:
  - `tmp/current_atr_1435_policy_validation_20260416.py`
  - `docs/governance/current_atr_1435_policy_validation_packet_2026-04-16.md`

### Replay execution

- run `tmp/current_atr_1435_policy_validation_20260416.py`

### Required regression gates

- `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- `tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `tests/backtest/test_backtest_determinism_smoke.py`
- `tests/utils/test_features_asof_cache_key_deterministic.py`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

## Done criteria

This slice is done only if all conditions are met:

1. Packet exists and stays within Scope IN/OUT.
2. The new script runs successfully under canonical env flags.
3. Only the approved artifact files are created for the slice.
4. Containment verdict is explicit in `manifest.json`.
5. Required regression gates pass.
6. `closeout.md` states clearly whether `1435.209570` looks stronger, weaker, or merely narrower than `900`, separately for `2024` and `2025`.
7. Final wording remains research-only and does not recommend a runtime default change.
8. `manifest.json` includes pre/post `git status --short` evidence and exact replay-affecting env values.

## Expected conclusion format

The closeout should answer, plainly:

- Does `candidate_1435` outperform baseline `0.90`?
- Does it improve or degrade versus `candidate_900`?
- Does it merely concentrate uplift into fewer trades?
- Is the result stable enough to justify a later, separate deployment-policy discussion?

Any recommendation must remain one of:

- `retain baseline`
- `retain 900 as stronger bounded candidate`
- `carry 1435 forward as narrower research candidate`

No default/runtime promotion is allowed in this slice.
