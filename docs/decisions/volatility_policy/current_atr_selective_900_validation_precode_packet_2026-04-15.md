# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — read-only research slice that replay-validates one already-identified threshold candidate without changing `src/`, runtime defaults, or authority surfaces
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** Run a dedicated replay validation for the research candidate `current_atr >= 900` to determine whether it remains a better bounded compromise than the existing `763.415054` seam when compared directly against the locked `0.90` and `1.00` anchors on 2024 and 2025.
- **Candidate:** `current_atr selective 900 validation`
- **Base SHA:** `8e23ddb45d08784e8a8a340f83334f5842505e0e`

## Scope

- **Scope IN:**
  - `docs/decisions/volatility_policy/current_atr_selective_900_validation_precode_packet_2026-04-15.md`
  - `tmp/current_atr_selective_900_validation_20260415.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/closeout.md`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - runtime defaults / authority / schema surfaces
  - champion configs
  - optimizer / paper / live execution paths
  - docs outside this packet unless strictly required for evidence
  - validation-generated runtime/artifact writes anywhere outside the approved `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/` output root
- **Expected changed files:**
  - `docs/decisions/volatility_policy/current_atr_selective_900_validation_precode_packet_2026-04-15.md`
  - `tmp/current_atr_selective_900_validation_20260415.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/closeout.md`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`
- **Max files touched:** `6`

## Skill usage

- **Repo-local skill specs to apply:**
  - `.github/skills/python_engineering.json`
  - `.github/skills/genesis_backtest_verify.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- **Why these skills apply:**
  - the slice adds a small Python research/orchestration script
  - the evidence path depends on deterministic backtest replay and controlled artifact generation
  - the candidate validation must preserve explicit artifact-field and row-drift discipline rather than loose narrative-only reporting
- **Not needed for this slice:**
  - `.github/skills/config_authority_lifecycle_check.json` is not a primary skill because this slice must not alter authority/config surfaces

## Planned behavior

- Add one research-only script under `tmp/` that:
  - loads the existing locked anchors from these exact research artifacts:
    - baseline `0.90`: `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`
    - selective `763.415054`: `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_current_atr_selective_vol_mult_cfg.json`
    - always `1.00`: `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_100_vol_thr_75_cfg.json`
  - clones the current selective config into a `current_atr >= 900` candidate **in memory only** before writing a single approved reproducibility config artifact into the approved output folder
  - replays exactly four variants on the canonical windows:
    - baseline `0.90`
    - selective `763.415054`
    - candidate `900`
    - always `1.00`
  - uses the same symbol/timeframe and canonical mode flags as the prior slices:
    - symbol `tBTCUSD`
    - timeframe `3h`
    - years `2024` and `2025`
    - `GENESIS_FAST_WINDOW=1`
    - `GENESIS_PRECOMPUTE_FEATURES=1`
    - `GENESIS_MODE_EXPLICIT=1`
    - `GENESIS_FAST_HASH=0`
- The script may import existing repo code read-only (for example `GenesisPipeline`, `ConfigAuthority`, metric/scoring helpers), but it must not modify or monkeypatch runtime modules.
- The script must construct the `900` candidate config as a transient in-memory dict copy, then write exactly one packet-approved reproducibility config JSON to the approved output folder.
- The script must not call config write/persist/save/apply/atomic-write helpers, and must not mutate runtime authority surfaces.
- The script must not call result-writing helpers that emit standard uncontrolled artifacts (for example `TradeLogger.save_all` or CLI paths that write `results/backtests/` / `results/trades/`).
- The script must keep artifact writes confined to the dedicated approved output folder `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/`.
- The approved output directory itself may be created if absent, but once created the allowlist remains strict: no file other than the four packet-approved files may be created, modified, or deleted inside that folder or anywhere else in the watched mutable surfaces.
- The script must take a pre/post containment snapshot over at least these paths:
  - the approved output folder above
  - `results/`
  - `logs/`
  - `config/runtime.json`
  - `logs/config_audit.jsonl`
  - `.nonce_tracker.json`
  - `dev.overrides.local.json`
  - optionally any additional mutable output/state path the implementation probes for side effects
- The script must use an allowlist-style containment verdict: only the four approved files in the approved output folder may be created or modified by the validation run.
- The script must fail closed if the pre/post containment diff shows any create, modify, or delete event outside the approved output folder.
- For each year, capture at minimum:
  - score
  - return
  - max drawdown
  - profit factor
  - trade count
  - changed row counts versus baseline `0.90`
  - changed row counts versus selective `763.415054`
  - changed row counts versus always-`1.00`
  - action-drift counts (must remain visible, even if zero)
  - score-capture versus the full `0.90 -> 1.00` lift
- Produce exactly these four approved artifacts in the dedicated output folder:
  - `manifest.json`
  - `replay_summary.json`
  - `closeout.md`
  - `candidate_900_cfg.json`
- `manifest.json` must record at minimum:
  - base SHA
  - exact script command line
  - effective env values for `GENESIS_FAST_WINDOW`, `GENESIS_PRECOMPUTE_FEATURES`, `GENESIS_MODE_EXPLICIT`, and `GENESIS_FAST_HASH`
  - exact anchor source paths for baseline `0.90`, selective `763.415054`, and always-`1.00`
  - approved output folder
  - the exact list of written files
  - containment pre/post snapshot summary and verdict
- `closeout.md` must state plainly whether `900` looks more bounded on 2025 without giving back too much of the 2024 lift, and whether it clears the bar to become the next serious research candidate.

## Evidence basis for this slice

- The existing selective runtime seam is already implemented and governance-approved.
- The robustness sweep already identified `900` as the strongest balanced next threshold candidate on the locked 2024/2025 comparison surface.
- Prior sweep artifact source to cite directly in the dedicated validation outputs:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/sweep_summary.json`
- Observed sweep summary to validate directly:
  - 2024:
    - baseline `0.90`: score `0.4398`
    - selective `763.415054`: score `0.4463`
    - candidate `900`: score `0.4507`
    - always-`1.00`: score `0.4481`
  - 2025:
    - baseline `0.90`: score `0.1944`
    - selective `763.415054`: score `0.2027`
    - candidate `900`: score `0.1988`
    - always-`1.00`: score `0.2027`
- Current interpretation to validate:
  - `900` keeps a material share of the 2024 uplift
  - while becoming more bounded than `763.415054` / always-`1.00` on 2025
- This slice exists to convert that sweep observation into a dedicated candidate-level replay note before opening the broader good/bad-environment research lane.

## Gates required

- `pre-commit run --files docs/decisions/volatility_policy/current_atr_selective_900_validation_precode_packet_2026-04-15.md tmp/current_atr_selective_900_validation_20260415.py`
- `python tmp/current_atr_selective_900_validation_20260415.py --symbol tBTCUSD --timeframe 3h --years 2024 2025 --output-dir results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15 --manifest-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/manifest.json --summary-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json --closeout-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/closeout.md --config-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json --threshold 900`
- `python -m pytest tests/backtest/test_compare_backtest_results.py::test_compare_ri_p1_off_parity_rows_pass_order_insensitive tests/backtest/test_compare_backtest_results.py::test_build_ri_p1_off_parity_artifact_required_fields`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- proof from `manifest.json` that the containment snapshot saw no create / modify / delete event outside the approved output folder across the watched mutable paths
- explicit output note stating that the validation is research efficacy evidence only and does not change default behavior

## Stop Conditions

- any need to edit `src/`, `tests/`, or `config/`
- any uncontrolled artifact write outside the approved research output root
- any need to persist candidate configs to disk outside the approved output folder or to mutate runtime authority state
- any need to broaden from one candidate threshold into a fresh grid/sweep
- determinism / invariance gate failure
- evidence that the dedicated validation cannot be produced without broader orchestration changes

## Output required

- **Implementation Report** — delivered in chat only, not as a repo file
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/manifest.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/closeout.md`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`

## Evidence wording discipline

- This slice is observational replay research only.
- Any `900` recommendation remains a research candidate and not a deployment/default recommendation.
- No result in this slice may be described as causal proof or production readiness.
- If `900` fails to hold the expected 2024/2025 trade-off on dedicated validation, the closeout must say so plainly rather than defend the candidate out of sunk-cost loyalty.
