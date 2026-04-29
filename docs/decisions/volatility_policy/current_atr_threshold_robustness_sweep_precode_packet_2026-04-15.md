# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — read-only research slice that replays existing runtime behavior across additive threshold variants without changing `src/`, runtime defaults, or authority surfaces
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** Run a bounded robustness sweep over higher `current_atr` thresholds to test whether the already-implemented selective high-vol multiplier seam can preserve most of the 2024 uplift while filtering the near-always-`1.00` behavior seen on 2025.
- **Candidate:** `current_atr threshold robustness sweep`
- **Base SHA:** `8e23ddb45d08784e8a8a340f83334f5842505e0e`

## Scope

- **Scope IN:**
  - `docs/decisions/volatility_policy/current_atr_threshold_robustness_sweep_precode_packet_2026-04-15.md`
  - `tmp/current_atr_threshold_robustness_sweep_20260415.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/sweep_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/closeout.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - runtime defaults / authority / schema surfaces
  - champion configs
  - optimizer / paper / live execution paths
  - docs outside this packet unless strictly required for evidence
  - sweep-generated runtime/artifact writes anywhere outside the approved `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/` output root
- **Expected changed files:**
  - `docs/decisions/volatility_policy/current_atr_threshold_robustness_sweep_precode_packet_2026-04-15.md`
  - `tmp/current_atr_threshold_robustness_sweep_20260415.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/sweep_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/closeout.md`
- **Max files touched:** `5`

## Skill usage

- **Repo-local skill specs to apply:**
  - `.github/skills/python_engineering.json`
  - `.github/skills/genesis_backtest_verify.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- **Why these skills apply:**
  - the slice adds a small Python research/orchestration script
  - the evidence path depends on deterministic backtest replay and controlled artifact generation
  - the sweep summary must preserve explicit row-drift / parity-style artifact discipline instead of loose narrative-only reporting
- **Not needed for this slice:**
  - `.github/skills/config_authority_lifecycle_check.json` is not a primary skill because this slice must not alter authority/config surfaces

## Planned behavior

- Add one research-only script under `tmp/` that:
  - loads the existing locked anchors from the current research folder
  - clones the current selective config into higher-threshold candidates **in memory only**
  - replays a bounded threshold set on the canonical windows:
    - `763.415054` (existing selective anchor)
    - `800`
    - `850`
    - `900`
    - `950`
    - `1000`
  - uses the same symbol/timeframe and canonical mode flags as the prior slice:
    - symbol `tBTCUSD`
    - timeframe `3h`
    - years `2024` and `2025`
    - `GENESIS_FAST_WINDOW=1`
    - `GENESIS_PRECOMPUTE_FEATURES=1`
    - `GENESIS_MODE_EXPLICIT=1`
    - `GENESIS_FAST_HASH=0`
- The script may import existing repo code read-only (for example `GenesisPipeline`, `ConfigAuthority`, metric/scoring helpers), but it must not modify or monkeypatch runtime modules.
- The script must construct candidate configs as transient in-memory dict copies only.
- The script must not call config write/persist/save/apply/atomic-write helpers, and must not mutate runtime authority surfaces.
- The script must not call result-writing helpers that emit standard uncontrolled artifacts (for example `TradeLogger.save_all` or CLI paths that write `results/backtests/` / `results/trades/`).
- The script must keep artifact writes confined to the dedicated approved output folder `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/`.
- The script must take a pre/post containment snapshot over at least these paths:
  - the approved output folder above
  - `results/`
  - `logs/`
  - `config/runtime.json`
  - `logs/config_audit.jsonl`
  - `.nonce_tracker.json`
  - `dev.overrides.local.json`
  - optionally any additional mutable output/state path the implementation probes for side effects
- The script must use an allowlist-style containment verdict: only the three approved files in the approved output folder may be created or modified by the sweep.
- The script must fail closed if the pre/post containment diff shows any create, modify, or delete event outside the approved output folder.
- For each threshold and year, capture at minimum:
  - score
  - return
  - max drawdown
  - profit factor
  - trade count
  - changed row counts versus baseline `0.90`
  - changed row counts versus existing selective `763.415054`
  - changed row counts versus always-`1.00`
  - action-drift counts (must remain visible, even if zero)
- Produce exactly these three approved artifacts in the dedicated output folder:
  - `manifest.json`
  - `sweep_summary.json`
  - `closeout.md`
- `manifest.json` must record at minimum:
  - base SHA
  - exact script command line
  - effective env values for `GENESIS_FAST_WINDOW`, `GENESIS_PRECOMPUTE_FEATURES`, `GENESIS_MODE_EXPLICIT`, and `GENESIS_FAST_HASH`
  - approved output folder
  - the exact list of written files
  - containment pre/post snapshot summary and verdict
- `closeout.md` must state whether any higher threshold looks more bounded on 2025 without giving back too much of the 2024 lift.

## Evidence basis for this slice

- The existing selective runtime seam is already implemented and governance-approved.
- 2024 result summary from the prior slice:
  - baseline `0.90`: score `0.4398`
  - selective `763.415054`: score `0.4463`
  - always-`1.00`: score `0.4481`
- 2025 result summary from the prior slice:
  - baseline `0.90`: score `0.1944`
  - selective `763.415054`: score `0.2027`
  - always-`1.00`: score `0.2027`
- Current interpretation to stress-test:
  - `763.415054` is promising on 2024
  - but not selective enough on 2025 because it behaves almost the same as always-`1.00`
- This slice exists to test whether a higher `current_atr` cutoff can narrow activation while remaining meaningfully useful on 2024.

## Gates required

- `pre-commit run --files docs/decisions/volatility_policy/current_atr_threshold_robustness_sweep_precode_packet_2026-04-15.md tmp/current_atr_threshold_robustness_sweep_20260415.py`
- `python tmp/current_atr_threshold_robustness_sweep_20260415.py --symbol tBTCUSD --timeframe 3h --thresholds 763.415054 800 850 900 950 1000 --years 2024 2025 --output-dir results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15 --manifest-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/manifest.json --summary-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/sweep_summary.json --closeout-out results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/closeout.md`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- proof from `manifest.json` that the containment snapshot saw no create / modify / delete event outside the approved output folder across the watched mutable paths
- explicit output note stating that the sweep is research efficacy evidence only and does not change default behavior

## Stop Conditions

- any need to edit `src/`, `tests/`, or `config/`
- any uncontrolled artifact write outside the approved research output root
- any need to persist candidate configs to disk outside the approved output folder or to mutate runtime authority state
- any need to use runtime-only fields that are unavailable through the existing replay surface
- determinism / invariance gate failure
- evidence that the threshold sweep cannot be produced without broader orchestration changes

## Output required

- **Implementation Report** — delivered in chat only, not as a repo file
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/manifest.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/sweep_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_threshold_robustness_2026-04-15/closeout.md`

## Evidence wording discipline

- This slice is observational replay research only.
- Any threshold recommendation remains a research candidate and not a deployment/default recommendation.
- No result in this slice may be described as causal proof or production readiness.
- If no threshold clearly improves the 2024/2025 trade-off, the closeout must say so plainly rather than force a winner.
