# HTF exit-engine selection partial reclassification packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `implemented / docs-only / partial-reclassification`

This packet records one bounded docs-only partial reclassification for baseline finding `#8`. It does not change backtest runtime behavior, authorize an explicit `htf_exit_config["enabled"]` contract, or claim that the broader HTF engine-selection seam is fully closed.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `MED` — why: this slice is docs-only, but it narrows a high-sensitivity backtest finding and therefore must avoid over-claiming closure
- **Required Path:** `Quick` — why: two docs files only, no runtime behavior change, no dependency/schema/env/default changes
- **Lane:** `Research-evidence` — why: this slice reclassifies current branch truthfulness for one backtest finding without reopening runtime work
- **Skill usage:** `none required` — bounded docs-only reclassification slice
- **Objective:** record that one older `#8` subclaim is stale on the current branch while preserving the still-open residual risk around implicit HTF engine-selection semantics
- **Related artifacts:** `docs/audit/BACKTEST_ENGINE_AUDIT.md`, `docs/audits/DEAD_GHOST_ZOMBIE.md`, `src/core/backtest/engine.py`, `tests/backtest/test_htf_exit_engine_selection.py`, `tests/governance/test_dead_code_tripwires.py`, `src/core/optimizer/runner.py`, `src/core/optimizer/runner_trial_backtest.py`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

### Scope

- **Scope IN:** this packet; one later-branch truthfulness note in `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` limited to finding `#8` under the BacktestEngine section
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `artifacts/**`, and `results/**`; any implementation of explicit `htf_exit_config["enabled"]`; any logging change; any edit that broadens into `#9` or other BacktestEngine findings; any wording that says `#8` is closed, fixed, eliminated, or fully mitigated
- **Expected changed files:** `docs/decisions/governance/htf_exit_engine_selection_partial_reclassification_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the slice says `narrowed` / `partially mitigated`, not `closed`
- contradiction self-review against `docs/audit/BACKTEST_ENGINE_AUDIT.md` and `docs/audits/DEAD_GHOST_ZOMBIE.md`
- focused proof that `tests/backtest/test_htf_exit_engine_selection.py` and `tests/governance/test_dead_code_tripwires.py` pass on the current branch

## Purpose

This packet answers one narrow question only:

- what is the smallest honest current-branch reclassification for baseline finding `#8` now that one older runner/manual mismatch subpath has narrowed, but the broader implicit engine-selection contract has not been replaced?

## What changed in this slice

- one new docs-only packet records the evidence boundary for `#8`
- the 2026-05-18 baseline now carries a dated later-branch note clarifying that the older “config present + env unset silently lands in legacy” subclaim should not be repeated unchanged for this checkout
- the same baseline note keeps the residual `bool(htf_exit_config)` versus explicit-enable seam visible as still open

## What did not change

- no backtest-engine code changed
- no optimizer code changed
- no tests changed
- no explicit `htf_exit_config["enabled"]` contract was introduced
- no claim is made that runner/manual drift is impossible or that finding `#8` is fully solved

## Governing basis

### Observed

1. `docs/audit/BACKTEST_ENGINE_AUDIT.md` Finding A originally flagged implicit HTF exit-engine selection and warned that runner/manual flows could diverge depending on env presence and config truthiness.
2. `src/core/backtest/engine.py` currently resolves HTF engine selection by explicit `GENESIS_HTF_EXITS` override first and otherwise by `bool(htf_exit_config)`.
3. `tests/backtest/test_htf_exit_engine_selection.py` currently proves four selector states: env unset + non-empty config => `NEW`, env `0` => legacy, env `1` + empty config => `NEW`, env unset + empty config => legacy.
4. `tests/governance/test_dead_code_tripwires.py` currently includes a tripwire that env unset + config present selects the `NEW` engine, plus a warning check for invalid `GENESIS_HTF_EXITS` values.
5. `docs/audits/DEAD_GHOST_ZOMBIE.md` already classifies the older “config present + env unset silently lands in legacy engine” path as a likely zombie, not as a still-dominant current branch flow.
6. `src/core/optimizer/runner.py` and `src/core/optimizer/runner_trial_backtest.py` reduce one runner/manual drift path further by setting `GENESIS_HTF_EXITS=1` when trial config requests HTF exits.

### Inferred

- the older broad carry-forward reading for `#8` is too strong for the current branch if repeated unchanged
- `#8` is more honestly described as partially mitigated than as fully open or fully closed
- the residual risk remains real because selection still depends on implicit env-override else `bool(htf_exit_config)` semantics, so `{}` versus non-empty config still changes engine choice without an explicit enable/disable contract

### Unverified

- whether the current implicit selector is acceptable as a long-term runtime contract
- whether a future backtest slice should introduce explicit `htf_exit_config["enabled"]` semantics or equivalent
- whether additional non-optimizer callers still experience meaningful ambiguity beyond the narrowed stale subclaim recorded here

## Applied correction

The baseline now carries a dated note stating that on `feature/risk-hardening-wave2`:

- the older `#8` subclaim about config-present/env-unset defaulting to legacy should not be repeated unchanged
- current branch tests support env-unset + non-empty config selecting the `NEW` engine
- optimizer-side explicit env forcing reduces one historical runner/manual drift path
- the broader finding remains open until engine selection stops depending on implicit truthiness and gains an explicit enable/disable contract

## Bottom line

For the current branch, `#8` is neither honestly “unchanged open” nor honestly “closed.” The smallest truthful move is therefore a docs-only partial reclassification: preserve the historical audit, narrow the stale subclaim, and leave the residual implicit-selection seam explicitly open.
