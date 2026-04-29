# RI router replay defensive-transition backtest setup-only packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `setup-only / planning-only / no launch authorization`

This packet defines the setup-only surface for the already-selected defensive-transition backtest question.

It does **not** authorize execution, code changes, config changes, runtime integration, default changes, family authority, readiness claims, or promotion claims.

Any runnable backtest step still requires a separate follow-up packet with fresh scope approval and explicit launch-time verification.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is docs-only and specializes one future backtest comparison surface without opening execution or authority.
- **Required Path:** `Quick`
- **Objective:** define one bounded setup-only surface for a possible later baseline-vs-candidate backtest comparison on the fixed RI bridge subject, including exact anchor identity, the baseline command shape that is repo-visible today, bounded output discipline, and the remaining candidate-carrier blocker.
- **Candidate:** `defensive-transition mandate-2 backtest setup only`
- **Base SHA:** `2dc6df79`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup-only / non-authorizing`
- `No runtime/paper/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill Usage

- **Applied repo-local skill:** none
- **Reason:** this packet is docs-only setup framing and does not itself execute a run-domain workflow.
- **Deferred:** `backtest_run` and `genesis_backtest_verify` belong to a later launch/verification step only if such a step is separately opened.

### Scope

- **Scope IN:**
  - create one docs-only setup-only packet for the already-defined defensive-transition baseline-vs-candidate backtest question
  - lock the exact bridge anchor, observational context, canonical execution notes, descriptive baseline command target, and current repo-visible output discipline
  - explicitly record the candidate-carrier gap that still blocks a runnable comparison on current repo-visible surfaces
  - re-anchor `GENESIS_WORKING_CONTRACT.md` to this setup-only state and blocker
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**` changes
  - no launch authorization
  - no actual baseline run
  - no actual candidate run
  - no code/config/test/runtime carrier for the candidate
  - no runtime instrumentation approval
  - no paper-shadow coupling
  - no new env/config/default authority
- **Expected changed files:**
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may authorize or imply execution
- no sentence may treat the descriptive baseline command target as already approved to run
- no sentence may imply the candidate run is already expressible on current repo-visible surfaces if it is not
- no sentence may reopen runtime, paper, readiness, cutover, or promotion
- no sentence may silently convert the candidate-carrier gap into implicit approval for a code or config slice

### Stop Conditions

- any wording that sounds like launch authorization instead of setup-only framing
- any wording that treats the candidate as already runnable through current CLI/config surfaces without separate authority
- any wording that expands writable surfaces beyond the bounded surfaces described here
- any wording that changes env/config semantics instead of citing current repo-visible surfaces
- any need to modify files outside the two scoped docs files

### Output required

- reviewable setup-only packet
- explicit exact anchor identity
- explicit descriptive baseline command target
- explicit writable-surface discipline notes
- explicit candidate-carrier blocker statement
- explicit launch-time re-verification items

## Purpose

This document is a **setup-only packet** for the already-defined defensive-transition backtest question.

It defines the bounded setup surface for a possible later baseline-vs-candidate backtest on the fixed RI bridge subject.
It does **not** authorize execution, artifact generation, readiness, promotion, runtime integration, or any broader runtime/integration step.

Fail-closed interpretation:

> This packet defines only the proposed future setup surface for a later, separately reviewed launch or carrier packet. It does not authorize execution, does not prove seam sufficiency, and does not assume that the candidate run is already expressible on current repo-visible surfaces.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/decisions/ri_router_replay_counterfactual_closeout_report_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`

This sequencing choice is also consistent with prior governance patterns that separated pre-code boundary selection from setup-only framing and later launch decisions.

Carried-forward meaning from the upstream chain:

1. the bounded replay lane is closed and grants no inherited runtime/integration approval
2. the first backtest subject is fixed to one exact RI bridge anchor
3. the current question remains local to the `defensive_transition_state` mandate semantics only
4. any runnable comparison still requires later separate launch or carrier authorization and launch-time re-verification

## Setup subject and exact anchor

The only active setup subject in this packet is the defensive-transition backtest comparison anchored to:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

### Exact anchor identity

- SHA256: `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`

Any later launch or carrier packet must recompute the anchor fingerprint and confirm it still matches this exact identity before treating the setup surface as unchanged.

### Exact observational context

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`
- warmup bars: `120`
- data-source policy: `frozen_first`

### Canonical execution notes (reproducibility only)

If a later launch packet is proposed, the canonical reproducibility notes to re-verify are:

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_FAST_HASH=0`
- explicit CLI flags `--fast-window --precompute-features`

These are reproducibility notes only, not launch authority.

## Admissible input surface

Only the following inputs are admissible inside this setup-only packet.

### 1. Governance anchors

- `docs/decisions/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_counterfactual_closeout_report_2026-04-23.md`

Allowed use:

- preserve the already-defined baseline-vs-candidate question
- preserve the fixed bridge subject
- preserve the prove-or-stop framing

### 2. Exact RI bridge anchor

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

Allowed use:

- preserve the exact RI bridge surface for a later baseline run
- preserve RI-only family identity and backtest-only framing
- preserve that the subject remains non-champion and not promotion evidence

### 3. Existing repo-visible backtest entry and output surfaces

- `scripts/run/run_backtest.py`
- `src/core/backtest/trade_logger.py`
- `docs/features/FEATURE_COMPUTATION_MODES.md`

Allowed use:

- cite the current CLI and canonical execution surfaces that a later launch packet would need to re-verify
- define descriptive baseline command and output-shape notes only
- record the current timestamp-driven save behavior that a later launch packet must handle explicitly

### 4. Candidate-carrier boundary evidence

- current repo-visible fixed bridge config
- current repo-visible `run_backtest.py` CLI surface
- current repo-visible strategy state surface in `src/core/strategy/decision_sizing.py`

Allowed use:

- record whether a bounded candidate run is directly expressible today without widening scope

## Descriptive future command targets only

The command targets below are **descriptive setup targets only**.
They are not approved for execution in this packet.
They may only be used if a later launch or carrier packet re-verifies that the entrypoint, flags, anchor file, and bounded output paths still match current repo state.

### Canonical local interpreter note

If a later launch packet is proposed, the local interpreter surface to re-verify is expected to be:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe`

This is a reproducibility note only, not launch authority.

### Future baseline-run target (expressible on current repo-visible surface)

A later launch packet may consider the following descriptive baseline-run target:

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --warmup 120 --data-source-policy frozen_first --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson --decision-rows-format ndjson --fast-window --precompute-features`

### Future candidate-run target (not yet expressible on current repo-visible surface)

This packet does **not** fix an executable descriptive candidate-run target yet.

Why:

- `scripts/run/run_backtest.py` exposes `--config-file`, `--decision-rows-out`, `--decision-rows-format`, `--compare`, `--warmup`, `--data-source-policy`, `--fast-window`, and `--precompute-features`, but it does **not** expose a mandate-semantics override for `defensive_transition_state`
- the fixed bridge config already exposes gate values such as `hysteresis_steps` and `cooldown_bars`, but it does **not** expose a repo-visible field for `defensive_transition_state mandate/confidence`
- `src/core/strategy/decision_sizing.py` tracks regime transition state, but the current repo-visible backtest surface does **not** expose a config-only carrier for lifting `defensive_transition_state` from mandate/confidence `1` to `2`

Interpretation:

- the baseline run is expressible today on current repo-visible surfaces
- the candidate run is **not yet** directly expressible as a bounded config/CLI-only backtest command
- any later candidate run therefore requires a separate carrier decision rather than silent assumption

## Writable-surface discipline

The current repo-visible baseline run shape implies the following bounded write surfaces would need to be re-verified later:

1. `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`
2. `results/backtests/tBTCUSD_3h_<timestamp>.json`
3. `results/backtests/tBTCUSD_3h_equity_<timestamp>.csv`
4. `results/trades/tBTCUSD_3h_trades_<timestamp>.csv`
5. `docs/analysis/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md`

### Timestamp-driven save behavior

Under current implementation, `TradeLogger.save_all(...)` writes result artifacts using runtime timestamps under:

- `results/backtests/`
- `results/trades/`

This means the exact materialized JSON/CSV filenames are **not** fixed by CLI input alone on the current repo-visible surface.

Therefore:

- this setup-only packet records the output shape only
- a later launch packet must re-verify how the exact materialized filenames will be captured, mapped, and compared without ambiguity
- if bounded filename discipline cannot be kept reviewable, the lane must stop rather than widen implicitly

## Current blocker between setup and launch

The current blocker is no longer the baseline subject definition.
That is already fixed.

The current blocker is:

- **candidate-carrier gap** — there is no current repo-visible config/CLI surface that directly expresses `defensive_transition_state mandate/confidence 2` as a bounded candidate backtest run

This packet therefore narrows the next question further:

- what is the smallest separately governed carrier surface, if any, that could express the candidate without widening into generic gate-stack rewrites or runtime-default drift?

## Preconditions for any later launch or carrier packet

Any later launch or carrier packet that wishes to use this setup surface remains blocked unless all of the following are true:

1. the working tree is clean for tracked files touching the anchor, backtest entrypoint, output-shape surface, or candidate-carrier decision
2. the exact bridge anchor still exists at the same path and still matches SHA256 `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`
3. `scripts/run/run_backtest.py` still supports the required baseline flags:
   - `--config-file`
   - `--decision-rows-out`
   - `--decision-rows-format`
   - `--compare`
   - `--warmup`
   - `--data-source-policy`
   - `--fast-window`
   - `--precompute-features`
4. the baseline command target can still be expressed without Python, config, test, runtime, or paper-path changes
5. a bounded candidate carrier exists under separate governance if a candidate run is to be authorized
6. the later slice can keep canonical mode and metadata discipline intact
7. the later slice can keep timestamped result files reviewable without ambiguous artifact attribution
8. the later slice remains RI-only, observational-only, and below runtime integration

These are preconditions for a later separate launch or carrier packet only.
They are not launch approval in this packet.

## Reproducibility notes (non-authority)

Any environment variables, interpreter paths, CLI flags, output locations, or timestamp patterns mentioned here are recorded only as **reproducibility notes** and **descriptive setup targets**.

They do **not**:

- authorize execution
- create new env/config/default authority
- prove candidate-carrier sufficiency
- prove bounded filename discipline
- prove launch readiness

If a later launch or carrier packet is ever proposed, only the then-current, actually verified values should be treated as run evidence.

## Explicit exclusions / not in scope

The following remain explicitly outside this packet:

- actual baseline execution
- actual candidate execution
- launch authorization
- carrier implementation authorization
- comparison verdicts
- readiness, cutover, or promotion framing
- code/config/test/runtime changes
- runtime instrumentation approval
- paper coupling
- any new evidence class

## Disallowed claims

This packet must not be read as permitting any of the following claims:

- `launch is approved`
- `the baseline command may now be run`
- `the candidate command already exists`
- `the current repo-visible surface already expresses the mandate-2 candidate`
- `timestamped result filenames are already proven to be bounded enough`
- `this packet changes env/config/default semantics`
- `this packet creates readiness, cutover, or promotion evidence`

## Bottom line

This packet creates only a **setup-only surface** for the defensive-transition backtest lane.

It locks:

- the exact RI bridge anchor and fingerprint
- the exact observational context
- the descriptive baseline command target that is repo-visible today
- the current output-shape discipline and its timestamp-driven constraint
- the real remaining blocker: the candidate-carrier gap

It does **not** authorize launch, execution, carrier implementation, runtime integration, or any broader authority claim.
