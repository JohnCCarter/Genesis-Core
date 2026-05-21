# Backtest error-policy reopen shape packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `reopen-shape-proposed / docs-only / non-authorizing`

This document is a planning / decision artifact in `RESEARCH` and grants no implementation, runtime, test, API/result-contract, env/config, paper/live, launch, or promotion authority. It must not be used as approval to change `BacktestEngine` behavior.

> Later-branch truthfulness note (2026-05-21, `feature/risk-hardening-wave3`): the proposed first reopen shape below is no longer purely future-tense for the current checkout. Current `src/core/backtest/engine.py` already exposes `BacktestEngine.run(..., error_policy=...)`, preserves `continue_collect_raise_after_loop` as the default, supports `fail_fast`, and rejects invalid policy strings before replay; focused tests in `tests/backtest/test_backtest_engine.py` now lock the default late-raise path, `fail_fast`, and invalid-policy reject behavior. This note preserves the packet as a historical pre-implementation selection artifact only. It does **not** widen current truth to constructor-level defaults, env/config semantics, `best_effort`, or returned-`errors` payload forms.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only, but wording drift could be mistaken for approving a new runtime policy on a high-sensitivity backtest surface
- **Required Path:** `Quick`
- **Lane:** `Concept` — why: this slice chooses one exact future reopen shape only; it does not implement or approve a runtime change
- **Objective:** choose one exact first reopen shape for `#18` on the current backtest error-policy seam without entering `src/core/backtest/engine.py` runtime behavior
- **Candidate line:** `#18 backtest error-policy explicitness`
- **Proposed first reopen shape:** `future run-level BacktestEngine.run(..., error_policy=...) surface with default current behavior preserved`
- **Base SHA:** `6f842a9c`
- **Skill Usage:** `ingen matchande skill identifierad`

### Scope

- **Scope IN:** one docs-only packet; explicit observed/inferred/unverified framing; exact current code/test anchors for the existing continue+raise policy; explicit first reopen-shape selection pinned to a future `BacktestEngine.run(..., error_policy=...)` surface only; explicit statement that the first future implementation should keep the current default behavior unchanged; explicit statement that constructor-level, env/config, and result-payload widening are out of the first reopen shape
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `.github/**`, `scripts/**`, `results/**`, and `artifacts/**`; all runtime behavior changes; all new tests; all API/result-contract changes; all env/config semantics; all paper/live or optimizer changes; all claims that `error_policy` already exists or is approved for implementation
- **Expected changed files:** `docs/decisions/governance/backtest_error_policy_reopen_shape_packet_2026-05-19.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual path/anchor audit for every named file path, symbol, and test anchor
- manual wording audit that the chosen reopen shape remains future-tense / `föreslagen` rather than implemented
- manual wording audit that the current default behavior remains explicitly unchanged unless a later implementation slice says otherwise
- manual wording audit that constructor/env/config and result-payload / `best_effort` widening remain out of the first reopen shape
- manual wording audit that no runtime, contract, or approval authority is implied

### Stop Conditions

- any wording that treats `BacktestEngine.run(..., error_policy=...)` as already present in the repo
- any wording that implies a runtime change is already approved rather than needing a separate future slice
- any wording that widens the first reopen shape into constructor defaults, env flags, or persisted config semantics
- any wording that includes `best_effort` / returned `errors` payload in the first reopen shape
- any wording that turns this packet into a claim about paper/live, optimizer, or API result-contract policy

## Purpose

This packet answers one narrow question only:

- after the current code/tests made the continue+raise behavior explicit, what is the smallest honest first reopen shape for `#18` if an alternative backtest error policy is later needed?

## What changed in this slice

- the repo now has one docs-only record for the smallest first reopen shape on `#18`
- the repo now records which nearby surfaces stay out of that first reopen shape

## What did not change

- no runtime behavior
- no `src/core/backtest/engine.py` implementation
- no tests or test outcomes
- no API/result payload
- no env/config semantics
- no approval for a runtime slice

## Governing basis

### Observed

1. `src/core/backtest/engine.py` currently defines `_PER_BAR_ERROR_POLICY = "continue_collect_raise_after_loop"`.
2. `src/core/backtest/engine.py::_raise_if_per_bar_errors(...)` logs the active policy label and raises `RuntimeError(...)` after replay if any per-bar evaluation errors were collected.
3. `src/core/backtest/engine.py::BacktestEngine.run(...)` already documents the current behavior explicitly: the loop continues, then raises after completion when per-bar errors were seen.
4. `tests/backtest/test_backtest_engine.py::test_engine_raises_on_pipeline_errors` proves repeated per-bar pipeline failures still lead to one late `RuntimeError(...)` after replay.
5. `tests/backtest/test_backtest_engine.py::test_engine_error_policy_continues_loop_before_raising` proves a first processed-bar failure still lets the replay finish before the late raise.
6. `docs/audit/BACKTEST_ENGINE_AUDIT.md` Fynd D frames the remaining issue as caller surprise and recommends making the policy explicit via parameter/config, with examples like `fail_fast`, `fail_on_any_error`, and `best_effort`.
7. The current repo scan for this slice did not locate an existing `error_policy` parameter on `BacktestEngine.__init__(...)`, `BacktestEngine.run(...)`, env flags, or persisted runtime config.

### Inferred

- The current behavior is no longer a hidden seam: code, docstring, and tests already make the existing continue+raise path explicit.
- Because the current behavior is already explicit, the smallest honest reopen is not a broader documentation pass or a direct runtime rewrite, but a single future policy surface that a caller can opt into deliberately.
- A run-level `BacktestEngine.run(..., error_policy=...)` surface is smaller than a constructor-level surface because it keeps policy choice call-scoped and does not introduce new engine-instance defaults.
- A run-level `BacktestEngine.run(..., error_policy=...)` surface is smaller than env/config control because it avoids global defaults, persisted semantics, config-authority questions, and runner/manual divergence.
- A first reopen shape that keeps non-raising `best_effort` out is smaller than one that adds returned `errors` payloads, because result-payload expansion would widen into caller-contract changes.

### Unverified in this packet

- the exact future function signature beyond the presence of a run-level `error_policy` surface
- the exact internal implementation mechanics if a later runtime slice adds `error_policy`
- whether a first implementation should support only one non-default mode immediately or defer that to a later packet
- any later observability/result-reporting shape beyond the current raised-error contract

## First reopen-shape selection

### Current standing conclusion

If `#18` is reopened after this packet, the smallest honest first future implementation shape should be limited to:

- a run-level `BacktestEngine.run(..., error_policy=...)` surface only
- default behavior that preserves the current `continue_collect_raise_after_loop` path unchanged
- no constructor-level default, env flag, or persisted config policy in that first slice
- no `best_effort` mode and no returned `errors` payload in that first slice

More specifically, this packet proposes that the first reopen shape stay bounded to a run-level policy choice between:

- the current default continue+raise behavior already anchored in code/tests
- at most one alternate raising-mode surface later, if a separate runtime slice chooses to introduce it

This packet does **not** approve the runtime slice itself. It records the first reopen shape only.

### Why the other shapes are not chosen first here

- **Constructor-level policy:** not chosen first because it would widen policy choice into engine-instance defaults and cross-call behavior, which is larger than a single call-scoped surface.
- **Env/config policy:** not chosen first because it would widen into default semantics, persisted behavior, and runner/manual parity questions.
- **`best_effort` / returned `errors` payload:** not chosen first because it widens into result-contract changes and caller expectations beyond the current raised-error contract.
- **Broader backtest reporting changes:** not chosen first because observability/result-shape expansion is downstream of settling the smallest callable policy surface.

These alternatives remain possible later bounded follow-ups. They are not rejected globally by this packet.

## Reopen rule

If this line is reopened later, the next admissible move under this packet must still be a separate bounded follow-up that stays within the chosen first shape.

That later follow-up must not silently widen into:

- constructor-level engine defaults
- env/config semantics
- `best_effort` / returned `errors` result-contract changes
- optimizer, runner, paper/live, or API result-shape policy
- a claim that the packet itself already approves runtime change

If a later implementation slice discovers it cannot remain inside that boundary, it must stop and reopen as a new packet.

## Bottom line

The current repo already makes the existing backtest continue+raise policy explicit in code, docstring, and tests. The smallest honest first `#18` reopen shape is therefore a **future run-level `BacktestEngine.run(..., error_policy=...)` surface with the current default behavior preserved**, while constructor/env/config and `best_effort` / returned-`errors` widening stay out of the first slice.
