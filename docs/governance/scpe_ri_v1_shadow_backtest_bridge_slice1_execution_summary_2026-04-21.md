# SCPE RI V1 shadow-backtest bridge slice1 execution summary

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `executed / bounded / observational-only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records the outcome of one already-authorized bounded control/shadow execution and must remain execution-reporting only, without reopening runtime, paper, readiness, cutover, or promotion scope.
- **Required Path:** `Quick`
- **Objective:** record exact launch-state evidence, exact commands run, parity outcome, bounded artifact materialization, and the machine-readable shadow-summary facts emitted by the authorized SCPE RI V1 bridge slice1 execution.
- **Candidate:** `shadow-backtest bridge slice1 execution summary`
- **Authorization basis:** `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_final_launch_authorization_packet_2026-04-21.md`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Execution reporting only`
- `Observational-only / RI-only`
- `No runtime/paper/readiness/cutover/promotion reopening`
- `Claim only actually observed run evidence`
- `Treat engine execution_mode path as code-path evidence only under --no-save`

### Skill Usage

- **Applied repo-local skill:** `backtest_run`
  - **Reason:** canonical command/env discipline for the bounded `run_backtest.py` execution.
- **Applied repo-local skill:** `genesis_backtest_verify`
  - **Observed execution:** `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run_skill.py --skill genesis_backtest_verify --manifest stable --dry-run` → `PASS`
- **Applied repo-local skill:** `shadow_error_rate_check`
  - **Observed execution:** `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run_skill.py --skill shadow_error_rate_check --manifest dev --dry-run` → `PASS`

### Scope

- **Scope IN:**
  - one docs-only execution summary for the exact authorized control/shadow run pair
  - exact launch-state snapshot
  - exact run commands and observed artifacts
  - exact parity and containment conclusions
- **Scope OUT:**
  - no code/test/config/script edits
  - no alternate run
  - no runtime/paper/promotion conclusion
  - no counterfactual claims about unsaved result payloads
- **Expected changed files:** `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`
- **Max files touched:** `1`

## Exact authorization and launch snapshot

Authorization source:

- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_final_launch_authorization_packet_2026-04-21.md`

Immediate pre-launch self-revocation checks observed green:

- `git status --short` returned no file lines
- launch `HEAD` was `6686db17`
- exact anchor path remained `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- exact anchor SHA256 remained `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`
- `scripts/run/run_backtest.py --help` still exposed:
  - `--config-file`
  - `--decision-rows-out`
  - `--decision-rows-format`
  - `--intelligence-shadow-out`
  - `--no-save`
  - `--fast-window`
  - `--precompute-features`

Therefore the final authorization packet remained active at launch time.

## Exact commands executed

### Shared environment

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_FAST_HASH=0`

### Control run

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson --decision-rows-format ndjson --fast-window --precompute-features --no-save`

Observed top-line result from stdout:

- Total Return: `2.99%`
- Total Trades: `118`
- Win Rate: `56.8%`
- Sharpe Ratio: `0.230`
- Max Drawdown: `2.18%`
- Profit Factor: `1.93`
- Score: `0.3041`

### Shadow run

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson --decision-rows-format ndjson --intelligence-shadow-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json --fast-window --precompute-features --no-save`

Observed top-line result from stdout:

- Total Return: `2.99%`
- Total Trades: `118`
- Win Rate: `56.8%`
- Sharpe Ratio: `0.230`
- Max Drawdown: `2.18%`
- Profit Factor: `1.93`
- Score: `0.3041`

## Decision-row parity result

Observed decision-row artifacts:

- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson`

Observed parity facts:

- control SHA256: `A5574010E08F7CE1CB744F8F135380F65B3174D24BB67BC162D2B7C0E215F582`
- shadow SHA256: `A5574010E08F7CE1CB744F8F135380F65B3174D24BB67BC162D2B7C0E215F582`
- identical hashes: `true`
- control lines: `2793`
- shadow lines: `2793`

Interpretation:

- the bounded shadow run preserved decision-row output parity for this exact execution
- no decision-row drift was observed on the emitted control/shadow artifacts

## Machine-readable shadow summary observed

Observed summary artifact:

- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`

Observed fields from the emitted summary:

- `shadow_status`: `completed`
- `decision_drift_observed`: `false`
- `advisory_only`: `true`
- `summary_path`: `results\intelligence_shadow\tBTCUSD_3h_ri_shadow_bridge_slice1_20260421\shadow_summary.json`
- `ledger_root`: `C:\Users\fa06662\Projects\Genesis-Core\artifacts\intelligence_shadow\tBTCUSD_3h_ri_shadow_bridge_slice1_20260421\research_ledger`
- backtest bars processed: `2793`
- warmup bars: `120`
- seed: `42`
- git hash: `6686db17e471248b9d006d0b4db3a0c811aa8b58`
- derived strategy family: `ri`
- strategy family source: `family_registry_v1`
- top advisory parameter set id: `champion-shadow-b758397b23051467`
- derived parameter count: `12`
- captured events: `2793`
- collected events: `2793`
- normalized events: `2793`
- evaluations: `2793`
- parameter recommendations: `1`
- ledger entity ids count: `2793`

Interpretation:

- the emitted shadow summary stayed advisory-only
- the machine-readable summary reports no decision drift
- the emitted summary carried the reviewed bounded telemetry expected from `src/core/backtest/intelligence_shadow.py`

## Bounded containment observed

Observed materialized writable surfaces:

- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`
- `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`

Observed ledger-root facts:

- ledger root exists: `true`
- ledger file count: `2796`
- sample files:
  - `artifacts/ART-2024-0001.json`
  - `artifacts/ART-2024-0002.json`
  - `artifacts/ART-2024-0003.json`
  - `artifacts/ART-2024-0004.json`
  - `artifacts/ART-2024-0005.json`
  - `artifacts/ART-2024-0006.json`
  - `artifacts/ART-2024-0007.json`
  - `artifacts/ART-2024-0008.json`

Interpretation:

- the authorized writable surfaces materialized as expected
- no additional out-of-scope writable path was observed in the reviewed execution evidence
- the earlier `config/__init__.py` containment issue did not recur on this slice

## Execution-mode note

`src/core/backtest/engine.py` does expose `backtest_info.execution_mode` in full result payloads.
However, this slice was intentionally run with `--no-save`, so this summary treats execution-mode confirmation as follows:

- observed run evidence: stdout mode line showed `GENESIS_FAST_WINDOW=1 GENESIS_PRECOMPUTE_FEATURES=1 GENESIS_RANDOM_SEED=42`
- observed CLI evidence: both authorized commands explicitly passed `--fast-window --precompute-features`
- code-path evidence only: `backtest_info.execution_mode` exists in engine results, but no full result artifact was claimed here under the bounded no-save surface

## Final conclusion

For the exact authorized SCPE RI V1 shadow-backtest bridge slice1 subject:

- launch authorization remained valid at execution time
- one bounded control run and one bounded shadow run both completed successfully
- emitted decision rows were bit-for-bit identical across control and shadow
- emitted shadow summary reported `decision_drift_observed=false` and remained advisory-only
- the reviewed bounded results/artifacts surfaces materialized as expected

This execution is therefore **prove-or-stop green for this exact RI-only observational slice1 surface only**.

It is **not** runtime evidence, paper-shadow approval, readiness evidence, cutover evidence, or promotion evidence.
