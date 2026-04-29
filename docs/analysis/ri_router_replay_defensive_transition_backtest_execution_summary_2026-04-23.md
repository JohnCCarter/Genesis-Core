# RI router replay defensive-transition paired backtest execution summary

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `executed / bounded / no observed divergence`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records one already-authorized bounded paired execution and must remain execution-reporting only, without reopening runtime integration, paper coupling, readiness, cutover, or promotion scope.
- **Required Path:** `Quick`
- **Objective:** record exact launch-state evidence, exact commands run, bounded artifact materialization, and the observed paired-outcome facts for the authorized defensive-transition baseline-vs-candidate backtest surface.
- **Candidate:** `defensive-transition paired backtest execution summary`
- **Authorization basis:** `docs/decisions/ri_router_replay_defensive_transition_backtest_launch_authorization_packet_2026-04-23.md`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Execution reporting only`
- `RI-only / observational-only`
- `No runtime/paper/readiness/cutover/promotion reopening`
- `Claim only actually observed run evidence`
- `No blanket clean-worktree claim`
- `No zero-filesystem-interaction claim`

### Skill Usage

- **Applied repo-local skill:** `backtest_run`
  - **Reason:** canonical env/flag discipline for the exact authorized `run_backtest.py` pair.
- **Applied repo-local skill:** `genesis_backtest_verify`
  - **Reason:** deterministic paired-artifact verification discipline using exact hashes and line counts for the emitted decision-row files.

### Scope

- **Scope IN:**
  - one docs-only execution summary for the exact authorized baseline/candidate run pair
  - one working-contract re-anchor from execution authorization to post-run diagnosis
  - exact launch-state snapshot, exact commands, observed output artifacts, and observed paired outcome
- **Scope OUT:**
  - no code/test/config/script edits
  - no alternate run window or alternate subject
  - no runtime/paper/readiness/promotion conclusion
  - no claim that unsaved result payloads were materialized
  - no widening beyond the exact suppressed-write surface
- **Expected changed files:**
  - `docs/analysis/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Exact authorization and launch snapshot

Authorization source:

- `docs/decisions/ri_router_replay_defensive_transition_backtest_launch_authorization_packet_2026-04-23.md`

Observed launch-state facts:

- launch `HEAD`: `efdce46b`
- exact baseline bridge path remained `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- exact candidate bridge path remained `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json`
- exact baseline bridge SHA256 remained `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`
- exact candidate bridge SHA256 remained `EF7661A673C3BFC89C1D60168163F4651EDA99D5937DD2163F5B666AD8ED51F7`
- known unrelated tracked diff at launch: `data/DATA_FORMAT.md`
- no current diff at launch touched the paired bridge files, `scripts/run/run_backtest.py`, `src/core/backtest/engine.py`, or `src/core/config/authority.py`

Therefore the launch-authorization packet remained active for the governed paired surface at execution time.

## Exact commands executed

### Shared environment

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_FAST_HASH=0`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`

### Baseline run

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; $env:GENESIS_PRECOMPUTE_CACHE_WRITE='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --warmup 120 --data-source-policy frozen_first --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson --decision-rows-format ndjson --fast-window --precompute-features --no-save`

Observed top-line result from stdout:

- Total Return: `6.40%`
- Total Trades: `118`
- Win Rate: `58.5%`
- Sharpe Ratio: `0.261`
- Max Drawdown: `1.43%`
- Profit Factor: `2.27`
- Score: `0.3567`

### Candidate run

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; $env:GENESIS_PRECOMPUTE_CACHE_WRITE='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --warmup 120 --data-source-policy frozen_first --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json --decision-rows-out results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson --decision-rows-format ndjson --fast-window --precompute-features --no-save`

Observed top-line result from stdout:

- Total Return: `6.40%`
- Total Trades: `118`
- Win Rate: `58.5%`
- Sharpe Ratio: `0.261`
- Max Drawdown: `1.43%`
- Profit Factor: `2.27`
- Score: `0.3567`

## Decision-row outcome

Observed decision-row artifacts:

- `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`
- `results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson`

Observed paired facts:

- baseline SHA256: `D75471906D9C82E981B51D7281F41A7F1CA71DC00779751C707872CEECF9D804`
- candidate SHA256: `D75471906D9C82E981B51D7281F41A7F1CA71DC00779751C707872CEECF9D804`
- identical hashes: `true`
- baseline lines: `2793`
- candidate lines: `2793`

Interpretation:

- the bounded candidate run did **not** produce row-level divergence on this exact subject/window
- no observed decision-row drift was emitted between baseline and candidate under the exact authorized suppressed-write surface
- the currently materialized `research_defensive_transition_override` candidate therefore remains behavior-equivalent on this specific paired execution, even after becoming runnable

## Bounded artifact materialization observed

Observed explicit output artifacts:

- `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`
- `results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson`

Observed containment facts:

- both bounded decision-row files were materialized at the exact authorized paths
- `git` reported no newly tracked or modified governed files after the run
- this summary does **not** claim zero filesystem interaction; it records only the observed explicit outputs and relies on the authorization basis for the narrower claim that cache writes on miss were suppressed for the exact command surface

## Execution-mode note

Observed execution-mode evidence for the authorized run pair:

- stdout mode line showed `GENESIS_FAST_WINDOW=1 GENESIS_PRECOMPUTE_FEATURES=1 GENESIS_RANDOM_SEED=42 DATA_SOURCE_POLICY=frozen_first`
- both executed commands explicitly passed `--fast-window --precompute-features`
- both executed commands explicitly set `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, even though that flag is not echoed in the runner mode line
- this slice intentionally used `--no-save`, so no full result artifact is claimed here under the bounded surface

## Final conclusion

For the exact authorized defensive-transition paired backtest subject:

- launch authorization remained active for the governed paired surface at execution time
- one bounded baseline run and one bounded candidate run both completed successfully
- observed top-line metrics were identical across the pair
- emitted decision rows were bit-for-bit identical across the pair
- no observed divergence was emitted on this exact `tBTCUSD` / `3h` / `2024-01-02 -> 2024-12-31` window

This execution is therefore **green as bounded execution evidence for this exact RI-only observational surface only**.

It is **not** runtime-default evidence, paper evidence, readiness evidence, cutover evidence, or promotion evidence.

The next smallest admissible step is a separate diagnostic slice that explains why the now-runnable candidate still emits no row-level divergence on this frozen paired surface.
