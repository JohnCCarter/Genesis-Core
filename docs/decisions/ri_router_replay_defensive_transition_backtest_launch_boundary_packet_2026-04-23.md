# RI router replay defensive-transition backtest launch-boundary packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `launch-boundary-refreshed / explicit-suppressed-write-surface / non-authorizing`

This packet defines the exact paired launch-boundary surface for the defensive-transition backtest subject now that both the baseline bridge and the separate candidate bridge artifact exist.

It does **not** authorize execution, code changes, config changes, runtime integration, default changes, family authority, readiness claims, or promotion claims.

Any runnable backtest step still requires a separate follow-up packet with fresh scope approval and explicit launch-time authorization.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet is still docs-only, but it now defines the exact paired baseline/candidate command and output boundary immediately upstream of any later execution decision, so wording must remain strictly fail-closed.
- **Required Path:** `Lite`
- **Objective:** refresh the docs-only paired launch-boundary surface for the exact defensive-transition baseline-vs-candidate backtest subject so that the descriptive command targets, containment evidence, and bounded outputs now match the explicit suppressed-write command surface that uses `GENESIS_PRECOMPUTE_CACHE_WRITE=0`.
- **Candidate:** `defensive-transition paired backtest launch boundary`
- **Base SHA:** `4690e9d8`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Launch-boundary only / non-authorizing`
- `Paired bridge subject only`
- `No runtime/paper/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill Usage

- **Consulted repo-local spec:** `backtest_run`
- **Reason:** the paired command boundary must preserve canonical mode, explicit seed, fixed warmup, and explicit metadata discipline for later reproducible comparison.
- **Consulted repo-local spec:** `genesis_backtest_verify`
- **Reason:** the paired boundary should remain compatible with later deterministic comparison discipline and must not imply hidden artifact creation or secret-bearing outputs.
- **No run-domain skill claimed as executed:** this packet records launch-boundary framing only and does not run any backtest.

### Scope

- **Scope IN:**
  - create one docs-only launch-boundary packet for the exact defensive-transition paired backtest subject
  - name both the baseline and candidate bridge artifacts explicitly
  - define descriptive paired command targets that remain inside current repo-visible CLI support
  - define explicit bounded output targets for a later no-save paired run surface
  - re-anchor `GENESIS_WORKING_CONTRACT.md` to the post-boundary / pre-authorization state
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**` changes
  - no launch authorization
  - no actual baseline run
  - no actual candidate run
  - no compare-summary generation
  - no runtime instrumentation approval
  - no paper-shadow coupling
  - no new env/config/default authority
- **Expected changed files:**
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may treat this boundary packet as launch authorization
- no sentence may treat the candidate bridge artifact as equivalent to execution authority
- no sentence may upgrade descriptive command targets into approval to run
- no sentence may reopen runtime, paper, readiness, cutover, or promotion scope
- no sentence may imply that execution was performed in this packet

### Stop Conditions

- any wording that collapses launch-boundary framing into launch approval
- any wording that widens from the exact paired bridge subject into generic backtest-sweep framing
- any wording that reopens timestamp-driven `TradeLogger` outputs as approved bounded outputs in this slice
- any wording that implies candidate artifact creation already satisfied clean-worktree or launch-authorization requirements
- any need to modify files outside the two scoped docs files

### Output required

- reviewable launch-boundary packet
- explicit exact paired bridge identities
- explicit descriptive paired command targets
- explicit bounded output-surface definition
- explicit remaining blocker statement before launch authorization

## Purpose

This document is a **launch-boundary packet** for the already-selected defensive-transition paired backtest question.

It defines the exact paired run surface that a later launch-authorization packet would need to assess.
It does **not** authorize execution, artifact generation, readiness, promotion, runtime integration, or any broader runtime/integration step.

Fail-closed interpretation:

> This packet defines only the paired launch-boundary surface for a later separately reviewed baseline-vs-candidate backtest step. It does not authorize execution, and it does not treat candidate expressibility as equivalent to launch approval.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/decisions/ri_router_replay_counterfactual_closeout_report_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_bridge_activation_implementation_packet_2026-04-23.md`

Carried-forward meaning from that chain:

1. the exact defensive-transition backtest subject is already fixed to one RI bridge baseline on `tBTCUSD`, `3h`, `2024-01-02 -> 2024-12-31`, warmup `120`
2. setup-only framing never authorized launch by itself
3. the previous candidate-carrier blocker is now closed because a separate candidate bridge artifact exists at a distinct path
4. launch still requires a separate authorization decision even when the paired subject and boundary surface are fully expressible

## Exact paired subject

The only active paired subject in this packet is:

### Baseline bridge

- path: `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- SHA256: `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`

### Candidate bridge

- path: `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json`
- SHA256: `EF7661A673C3BFC89C1D60168163F4651EDA99D5937DD2163F5B666AD8ED51F7`

### Boundaried interpretation of the pair

- the candidate bridge is the fixed baseline bridge plus explicit materialization of `cfg.multi_timeframe.research_defensive_transition_override`
- the paired subject does **not** imply any additional config drift beyond that one research leaf
- no edited copy, alternate candidate, or in-place mutation of the baseline bridge is in scope here

## Exact observational context

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`
- warmup bars: `120`
- data-source policy: `frozen_first`

## Canonical execution notes (reproducibility only)

If a later launch-authorization packet is proposed, the canonical reproducibility notes to re-verify are:

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_FAST_HASH=0`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- explicit CLI flags `--fast-window --precompute-features`

These are reproducibility notes only, not launch authority.

## Descriptive paired command targets only

The command targets below are **descriptive launch-boundary targets only**.
They are not approved for execution in this packet.
They may only be used if a later launch-authorization packet explicitly confirms that the entrypoint, flags, bridge files, and bounded output paths still match current repo state.

### Canonical local interpreter note

If a later launch packet is proposed, the local interpreter surface to re-verify is expected to be:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe`

This is a reproducibility note only, not launch authority.

### Future baseline-run target

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; $env:GENESIS_PRECOMPUTE_CACHE_WRITE='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --warmup 120 --data-source-policy frozen_first --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson --decision-rows-format ndjson --fast-window --precompute-features --no-save`

### Future candidate-run target

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; $env:GENESIS_PRECOMPUTE_CACHE_WRITE='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --warmup 120 --data-source-policy frozen_first --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json --decision-rows-out results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson --decision-rows-format ndjson --fast-window --precompute-features --no-save`

### Why `--compare` and timestamp-driven saves are intentionally excluded here

This boundary packet intentionally does **not** treat any of the following as approved paired outputs:

- `TradeLogger.save_all(...)` JSON/CSV outputs under timestamp-driven filenames
- `--compare` against a saved baseline JSON

Why:

- `--no-save` is the smallest repo-visible way to suppress timestamp-driven result/trade/equity writes from `TradeLogger`
- explicit `--decision-rows-out` paths keep the later paired run surface narrow and reviewable
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0` keeps the canonical paired run shape write-contained on cache miss by suppressing `cache/precomputed/` directory creation and `.npz` writes while preserving existing cache reads and in-memory precompute for the run
- any later metrics/result comparison artifact remains a separate follow-up decision and must not be smuggled into this boundary packet

## Explicit bounded output surface for any later paired run

If a later separate execution step is performed on the exact surface fixed here, the paired no-save run surface should remain bounded to the following explicit outputs only:

1. `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`
2. `results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson`
3. `docs/analysis/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md`

Boundaried meaning:

- the first two paths are explicit machine-readable decision-row captures
- the third path is a later human-written execution summary only if launch is separately authorized and a run is actually performed
- these remain the intended explicit outputs, not proof that the current canonical paired run is already fully bounded
- nothing in this packet approves any additional result JSON, trade CSV, equity CSV, shadow output, promotion/readiness artifact, or `cache/precomputed/` side effect

## Repo-visible evidence observed in this session

| Check                                  | Current status in this session               | Evidence                                                                                                                                                                                                                                                                                                                                                                                                   | Why it matters                                                                                            |
| -------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Paired subject/runtime surfaces stable | Green                                        | current tracked changes are limited to this docs-only refresh plus unrelated `data/DATA_FORMAT.md`; no current diff touches the paired bridge files, `scripts/run/run_backtest.py`, or `src/core/backtest/engine.py`                                                                                                                                                                                       | launch subject identity and containment anchors remain exact                                              |
| Exact baseline bridge identity         | Green                                        | baseline bridge exists at the fixed path and currently hashes to `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`                                                                                                                                                                                                                                                                        | the baseline subject must remain exact and fingerprint-stable                                             |
| Exact candidate bridge identity        | Green                                        | candidate bridge exists at the fixed path and currently hashes to `EF7661A673C3BFC89C1D60168163F4651EDA99D5937DD2163F5B666AD8ED51F7`                                                                                                                                                                                                                                                                       | the candidate subject must remain exact and fingerprint-stable                                            |
| Repo-visible paired CLI support        | Green                                        | `scripts/run/run_backtest.py` currently exposes `--config-file`, `--warmup`, `--data-source-policy`, `--fast-window`, `--precompute-features`, `--decision-rows-out`, `--decision-rows-format`, and `--no-save`                                                                                                                                                                                            | the paired command targets remain expressible without runner edits                                        |
| Full bounded write containment         | Green for the exact suppressed-write surface | `scripts/run/run_backtest.py::_write_decision_rows(...)` writes only to the explicit decision-row output path, `TradeLogger.save_all(...)` remains behind `if not args.no_save`, no `--intelligence-shadow-out` path is used for this pair, and `src/core/backtest/engine.py` now suppresses `cache_dir.mkdir(...)` plus `_np.savez_compressed(...)` on cache miss when `GENESIS_PRECOMPUTE_CACHE_WRITE=0` | the paired run may stay confined to the approved explicit outputs when the exact env surface is preserved |
| Launch authorization                   | Separate companion decision                  | this boundary packet remains non-authorizing even when containment is green for the exact suppressed-write surface                                                                                                                                                                                                                                                                                         | paired command/output definition is not equivalent to permission to execute                               |

## Current state between boundary and launch

The previous blocker is no longer candidate expressibility.
That blocker was already closed by the separate candidate bridge artifact.

The previous containment blocker is now also closed for the exact paired surface that explicitly sets `GENESIS_PRECOMPUTE_CACHE_WRITE=0`.

Interpretation:

- the paired run surface is now nameable, explicit, and boundary-bounded for the exact suppressed-write command shape
- this packet still does **not** authorize execution by itself
- candidate artifact creation and paired command definition still do not authorize launch by themselves
- launch authorization remains a separate companion decision even when the boundary-level containment question is green for this exact surface

## Boundary conditions for any companion authorization or later execution step

Any companion authorization or later execution step that wishes to use this boundary must keep all of the following true:

1. the working tree is clean for tracked files touching the paired bridge subject, runner entrypoint, or governed packet chain
2. the exact baseline and candidate bridge files still exist at the same paths and still match the SHA256 values recorded above
3. `scripts/run/run_backtest.py` still supports the paired no-save command targets without runner edits
4. the paired command targets still keep canonical mode fixed to `1/1` discipline via explicit env vars and `--fast-window --precompute-features`
5. the explicit containment qualifier `GENESIS_PRECOMPUTE_CACHE_WRITE=0` remains present, and the pair continues to avoid `--intelligence-shadow-out`
6. full bounded write containment remains green for that exact suppressed-write surface and is not broadened to env-absent or widened-output variants by implication
7. the paired run remains RI-only, observational-only, and below runtime integration, paper coupling, readiness, cutover, or promotion claims
8. actual execution, if separately performed, remains separate from any post-run comparison or readiness claim

These are retained boundary conditions only.
They are not launch approval in this packet.

## Explicit exclusions / not in scope

The following remain explicitly outside this packet:

- actual baseline execution
- actual candidate execution
- launch authorization
- comparison verdicts
- saved backtest JSON/CSV/trades/equity artifacts
- intelligence-shadow outputs
- readiness, cutover, or promotion framing
- code/config/test/runtime changes
- known unrelated tracked diff `data/DATA_FORMAT.md` outside this packet's governed surface
- any new evidence class beyond the paired boundary definition

## Bottom line

This packet creates only a **paired launch-boundary surface** for the defensive-transition backtest lane.

It locks:

- the exact baseline and candidate bridge identities
- the exact observational context
- the descriptive paired no-save command targets for the exact suppressed-write surface that is repo-visible today
- the explicit bounded decision-row output surface
- green write-containment evidence for the exact surface that explicitly sets `GENESIS_PRECOMPUTE_CACHE_WRITE=0`

It does **not** authorize launch, execution, comparison verdicts, runtime integration, or any broader authority claim.
