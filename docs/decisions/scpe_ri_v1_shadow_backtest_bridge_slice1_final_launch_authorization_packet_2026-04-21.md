# SCPE RI V1 shadow-backtest bridge slice1 final launch authorization packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `AUTHORIZED NOW / state-bound / self-revoking`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet grants a tightly bounded launch authorization for one exact RI-only observational backtest shadow slice, but must remain fail-closed, state-bound, and non-authoritative outside the explicitly reviewed surface.
- **Required Path:** `Quick`
- **Objective:** authorize exactly one bounded control/shadow execution for the already-reviewed SCPE RI V1 shadow-backtest bridge slice1 subject now that the previously remaining cleanliness blocker has been cleared and the reviewed containment evidence remains green.
- **Candidate:** `shadow-backtest bridge slice1 final launch authorization`
- **Base SHA:** `b8fd38cb`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `RI-only observational-only bounded execution`
- `No runtime/paper/readiness/cutover/promotion reopening`
- `Authorization applies only to the exact anchor path + SHA256 below`
- `Authorization self-revokes on launch-surface drift`

### Skill Usage

- **Applied repo-local skill:** `backtest_run`
  - **Reason:** command discipline for `scripts/run/run_backtest.py`, canonical seed handling, and explicit fast-window/precompute execution flags.
- **Applied repo-local skill:** `genesis_backtest_verify`
  - **Reason:** deterministic verification coverage for the bounded backtest lane.
  - **Observed execution:** `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run_skill.py --skill genesis_backtest_verify --manifest stable --dry-run` → `PASS`
- **Applied repo-local skill:** `shadow_error_rate_check`
  - **Reason:** dedicated shadow parity / containment contract coverage.
  - **Observed execution:** `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run_skill.py --skill shadow_error_rate_check --manifest dev --dry-run` → `PASS`

### Scope

- **Scope IN:**
  - one final docs-only launch authorization packet for the exact RI-only shadow bridge slice1 subject
  - explicit `AUTHORIZED NOW` decision for one bounded control run and one bounded shadow run only
  - explicit self-revocation predicates and preflight requirements
  - exact writable-surface discipline for the later execution summary step
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, or `scripts/**` edits
  - no widening to alternate configs, alternate dates, alternate symbols, or alternate timeframes
  - no paper/runtime coupling
  - no promotion/readiness claim
  - no reinterpretation of this packet as runtime approval or production evidence
- **Expected changed files:** `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_final_launch_authorization_packet_2026-04-21.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For the authorized launch surface:

- clean working tree immediately before launch
- exact anchor path unchanged
- exact anchor SHA256 unchanged
- `scripts/run/run_backtest.py --help` still exposes the required bounded CLI surface
- bounded containment evidence from the closed implementation lane remains applicable
- skill coverage above remains green

### Stop Conditions

- working tree not clean immediately before launch
- exact anchor path changes or digest changes
- required CLI flags/options disappear or rename
- bounded writable surfaces widen beyond the paths listed below
- any sentence in later reporting upgrades this run into runtime, paper, readiness, cutover, or promotion evidence

### Output required

- one final launch authorization packet
- exact allowed launch subject and allowed writable surfaces
- explicit self-revocation rule set
- explicit research-only execution boundary

## Purpose

This packet is the **separate final launch authority artifact** for the exact RI-only SCPE shadow-backtest bridge slice1 subject.

It does **not** replace or rewrite the earlier historical packets.
It does **not** turn the setup-only packet into execution proof.
It authorizes exactly one bounded control/shadow execution only while the reviewed launch surface stays green.

## Upstream governed basis

This packet depends on the already-tracked upstream chain:

- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_setup_only_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_launch_authorization_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_write_boundary_audit_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_precode_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_packet_2026-04-21.md`
- `docs/analysis/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_report_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_launch_reauthorization_packet_2026-04-21.md`

Carried-forward meaning that remains in force:

1. the slice remains RI-only, observational-only, and non-authoritative
2. setup-only framing never by itself authorizes launch
3. the earlier `NOT AUTHORIZED NOW` decision was correct for its then-current dirty-tree state
4. the containment-fix implementation lane is closed and green
5. launch authority remains exact-state and fail-closed

## Exact launch subject

The only authorized bridge anchor is:

- path: `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- SHA256: `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`

Bounded execution context remains fixed:

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`
- save behavior: `--no-save`
- execution flags: `--fast-window --precompute-features`
- environment baseline:
  - `GENESIS_RANDOM_SEED=42`
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_FAST_HASH=0`

No alternate config, edited copy, renamed clone, widened date range, or additional output path is authorized by implication.

## Authorization verdict

### Decision

- **AUTHORIZED NOW**

### Why this is now the correct decision

The earlier historical blocker set was:

1. clean working tree
2. bounded write containment
3. ledger-root derivation re-verification

At the current reviewed surface, all three predicates are green:

- working tree was clean when this authorization decision was prepared
- the out-of-bound `config/__init__.py` touch side effect has already been removed and validated in the closed containment-fix lane
- shadow-summary / derived-ledger-root behavior already has targeted test coverage and current-session green evidence

Therefore one exact bounded control/shadow execution is authorized now, subject to the self-revocation rules below.

## Current evidence supporting authorization

### 1. Working tree status

Observed state while preparing this packet:

- green / clean

Observed evidence:

- `git status --short` returned no file lines at the reviewed pre-packet launch surface

Interpretation:

- the historical cleanliness blocker has been cleared
- because this packet itself is a repo file, launch must occur only from a clean commit that includes this packet or the authorization self-revokes immediately

### 2. Exact anchor identity

Observed state:

- green

Observed evidence:

- anchor path remained `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- SHA256 remained `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`

Interpretation:

- the exact launch subject is stable
- authorization is limited to this exact path + digest pair

### 3. Repo-visible CLI support

Observed state:

- green

Observed evidence:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --help` passed on the current reviewed surface
- the CLI still exposes:
  - `--config-file`
  - `--decision-rows-out`
  - `--decision-rows-format`
  - `--intelligence-shadow-out`
  - `--no-save`
  - `--fast-window`
  - `--precompute-features`

Interpretation:

- the exact bounded control/shadow commands remain expressible now
- this is launch-surface support evidence, not execution proof by itself

### 4. Containment and ledger-root evidence

Observed state:

- green

Observed evidence carried forward from the already-closed implementation lane and current-session reads:

- `scripts/run/run_backtest.py` no longer performs the unconditional `config/__init__.py` touch
- `tests/backtest/test_run_backtest_intelligence_shadow.py::test_run_backtest_main_writes_shadow_summary_without_changing_dummy_results` passed in the containment-fix lane
- `src/core/backtest/intelligence_shadow.py` persists bounded summary fields including `summary_path`, `ledger_root`, counts, and `ledger_entity_ids`

Interpretation:

- the previously identified containment blocker is closed
- the shadow summary / ledger-root surface remains reviewable and bounded

### 5. Deterministic verification / parity contract coverage

Observed state:

- green

Observed evidence:

- `...python.exe scripts/run_skill.py --skill genesis_backtest_verify --manifest stable --dry-run` → `PASS`
- `...python.exe scripts/run_skill.py --skill shadow_error_rate_check --manifest dev --dry-run` → `PASS`

Interpretation:

- deterministic verification coverage and dedicated shadow parity contract coverage are both present on the reviewed launch surface

## Exact authorized writable surfaces

Only the following later execution outputs are authorized:

- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`
- `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`
- `docs/analysis/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`

No other writable surface is authorized by this packet.

## Exact authorized commands

### Control

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson --decision-rows-format ndjson --fast-window --precompute-features --no-save`

### Shadow

`$env:GENESIS_RANDOM_SEED='42'; $env:GENESIS_FAST_WINDOW='1'; $env:GENESIS_PRECOMPUTE_FEATURES='1'; $env:GENESIS_FAST_HASH='0'; C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson --decision-rows-format ndjson --intelligence-shadow-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json --fast-window --precompute-features --no-save`

## Self-revocation rules

This authorization becomes invalid immediately if any of the following becomes true before launch:

1. the working tree is not clean
2. the anchor path above changes
3. the anchor SHA256 above changes
4. the required CLI surface in `scripts/run/run_backtest.py --help` changes
5. any extra writable output path is added
6. the run is reframed as runtime, paper, readiness, cutover, or promotion evidence

## Launch boundary

This packet authorizes a bounded research execution only.

It does **not** authorize:

- runtime integration
- paper/live coupling
- read-path or write-surface widening
- promotion or cutover claims
- decision-drift tolerance beyond explicit post-run observation

## Final statement

At the reviewed current surface, this exact RI-only shadow-backtest bridge slice1 subject is **AUTHORIZED NOW** for one bounded control run plus one bounded shadow run only.

That authorization is exact-anchor-bound, clean-tree-bound, CLI-surface-bound, and self-revoking.
