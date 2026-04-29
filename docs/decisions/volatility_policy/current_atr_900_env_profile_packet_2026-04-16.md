# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — read-only research slice that profiles helpful vs harmful `current_atr >= 900` sizing contexts without changing `src/`, runtime defaults, or authority surfaces
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** Build a narrow good/bad-environment analysis for the already-validated `current_atr >= 900` research candidate by comparing it against the locked `0.90` baseline, using `2024` for discovery and `2025` as freeze-only blind validation for the rules discovered on `2024`.
- **Candidate:** `current_atr 900 environment profile`
- **Base SHA:** `8e23ddb45d08784e8a8a340f83334f5842505e0e`

## Scope

- **Scope IN:**
  - `docs/decisions/volatility_policy/current_atr_900_env_profile_packet_2026-04-16.md`
  - `tmp/current_atr_900_env_profile_20260416.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/closeout.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all files under `.vscode/`
  - runtime defaults / authority / schema surfaces
  - champion configs
  - optimizer / paper / live execution paths
  - docs outside this packet unless strictly required for evidence
  - any write outside `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/`
- **Expected changed files:**
  - `docs/decisions/volatility_policy/current_atr_900_env_profile_packet_2026-04-16.md`
  - `tmp/current_atr_900_env_profile_20260416.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/closeout.md`
- **Max files touched:** `5`

## Skill usage

- **Repo-local skill specs to apply:**
  - `.github/skills/python_engineering.json`
  - `.github/skills/genesis_backtest_verify.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- **Why these skills apply:**
  - the slice adds one small Python research/orchestration script
  - the evidence path depends on deterministic replay and controlled artifact generation
  - the output needs explicit row/feature/rule discipline rather than a narrative-only note
- **Not needed for this slice:**
  - `.github/skills/config_authority_lifecycle_check.json` is not primary because this slice must not alter any config or authority surface

## Planned behavior

- Add one research-only script under `tmp/` that:
  - loads these exact locked config artifacts:
    - baseline `0.90`: `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`
    - candidate `900`: `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`
  - replays baseline and candidate read-only on the canonical windows:
    - discovery window `2024-01-02 .. 2024-12-31`
    - blind-validation window `2025-01-01 .. 2025-12-31`
    - symbol `tBTCUSD`
    - timeframe `3h`
    - `GENESIS_FAST_WINDOW=1`
    - `GENESIS_PRECOMPUTE_FEATURES=1`
    - `GENESIS_MODE_EXPLICIT=1`
    - `GENESIS_FAST_HASH=0`
  - captures entry-available fields only from the decision surface available before order entry
  - matches positions deterministically by `position_id` parity inside each year
  - restricts the analysis population to the active treatment subset where candidate size exceeds baseline size
  - labels each active-treatment position observationally as:
    - `helpful` when candidate PnL delta vs baseline is strictly positive
    - `harmful` when candidate PnL delta vs baseline is strictly negative
    - `flat` when candidate PnL delta is effectively zero within a small tolerance
  - uses `2024` discovery data only to rank simple interpretable rule candidates from entry-time fields such as:
    - `zone`
    - `regime`
    - `htf_regime`
    - `zone_atr`
    - `current_atr_used`
    - `proba_buy`
    - `proba_sell`
    - `proba_edge`
    - `conf_overall`
    - `pre_slope_8_atr`
    - `pre_range_8_atr`
    - `bars_since_regime_change`
    - existing current-bar sizing multipliers exported in decision state
  - freezes candidate rule thresholds from `2024` discovery and applies those same exact rules to the `2025` active-treatment subset without re-tuning
  - uses `2025` only as blind validation for that frozen `2024` rule list; `2025` must not be used to select, adjust, replace, or re-rank rule candidates, and if every frozen rule fails the blind check the result must be explicit `none`
  - reports whether any simple rule keeps materially positive discovery separation while remaining directionally coherent on the blind `2025` set
- The script may import existing repo code read-only (for example `GenesisPipeline`, `ConfigAuthority`, metrics/scoring helpers), but it must not modify or monkeypatch runtime modules.
- The script must not call config write/persist/save/apply helpers, and must not mutate runtime authority surfaces.
- The script must not call helpers that emit uncontrolled backtest/trade artifacts under standard results folders.
- The script must keep all writes confined to the dedicated approved output folder `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/`.
- The approved output directory itself may be created if absent, but once created the allowlist remains strict: no file other than the three packet-approved files may be created, modified, or deleted inside that folder or anywhere else in the watched mutable surfaces.
- The script must take a pre/post containment snapshot over at least:
  - the approved output folder above
  - `results/`
  - `logs/`
  - `cache/`
  - `cache/precomputed/`
  - `config/runtime.json`
  - `logs/config_audit.jsonl`
  - `.nonce_tracker.json`
  - `dev.overrides.local.json`
- The script must use an allowlist-style containment verdict: only `manifest.json`, `env_summary.json`, and `closeout.md` may be created or modified by the run.
- `env_summary.json` must record at minimum:
  - base SHA
  - exact baseline/candidate source paths
  - discovery and validation windows
  - discovery/validation population counts
  - discovery feature rankings
  - a frozen `2024` rule list with exact thresholds/cutpoints used for evaluation
  - frozen rule evaluations on `2024`
  - blind validation of those same exact rules on `2025`
  - a clearly marked recommended next rule candidate, or an explicit `none` result if blind validation is weak
- `closeout.md` must state plainly whether the `900` candidate appears to have any simple, interpretable helpful/harmful environment split that survives blind validation.
- `closeout.md` must also state explicitly that this is observational replay research only, that any helpful/harmful split is associative rather than causal, and that any rule candidate requires a separate packeted policy-validation slice before any runtime proposal.

## Evidence basis for this slice

- Dedicated validation has already established that `current_atr >= 900` is the strongest bounded next candidate among the tested thresholds.
- Exact dedicated validation artifacts to cite:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/closeout.md`
- Locked current interpretation to examine, not assume:
  - `900` improves `2024` versus the existing `763.415054` seam
  - `900` is more bounded than the near-always-`1.00` behavior on `2025`
- This slice exists to move from threshold selection into ex-ante environment profiling before any further runtime-policy proposal.
- `2025` is blind only for the frozen environment rules discovered on `2024`; it is not allowed to participate in rule selection, threshold adjustment, or replacement.

## Gates required

- `pre-commit run --files docs/decisions/volatility_policy/current_atr_900_env_profile_packet_2026-04-16.md tmp/current_atr_900_env_profile_20260416.py`
- `python tmp/current_atr_900_env_profile_20260416.py --symbol tBTCUSD --timeframe 3h --discovery-year 2024 --validation-year 2025 --output-dir results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16 --manifest-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/manifest.json --summary-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json --closeout-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/closeout.md`
- `python -m pytest tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- proof from `manifest.json` that the containment snapshot saw no create / modify / delete event outside the approved output folder across the watched mutable paths
- explicit output note stating that the analysis is observational research only and does not change default behavior

## Stop Conditions

- any need to edit `src/`, `tests/`, or `config/`
- any uncontrolled artifact write outside the approved research output root
- any need to re-tune rules on `2025` after discovery on `2024`
- any feature-cache write outside the approved output files that is not explicitly captured and accepted by the containment allowlist
- any need to use runtime-unavailable or post-exit fields to define the ex-ante rules
- determinism / invariance gate failure
- evidence that no simple interpretable rule survives even a weak blind-validation sanity check

## Output required

- **Implementation Report** — delivered in chat only, not as a repo file
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/manifest.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/closeout.md`

## Evidence wording discipline

- This slice is observational replay research only.
- Any discovered environment split is evidence of association, not causal proof.
- Any recommended rule remains a research candidate until it is replay-validated in a separate packeted policy slice.
- If blind validation on `2025` is weak or contradictory, the closeout must say so plainly rather than force a winner.
