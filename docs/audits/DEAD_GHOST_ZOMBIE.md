# Deep Hygiene Audit — Dead Code / Zombie Flows

Date: 2026-03-02
Scope: Read-only hygiene audit of active code surfaces in `src/`, `scripts/` and `mcp_server/`, with tests/docs used only as evidence.
Constraint: **AUDIT-ONLY** (no code/config/runtime changes performed).

---

## Method and Evidence Rules

- Candidate pool:
  - `src/core/**`
  - `scripts/**` excluding `scripts/archive/**`
  - `mcp_server/**`
- Evidence sources used:
  - `docs/architecture/ARCHITECTURE_VISUAL.md`
  - `tests/test_dead_code_tripwires.py`
  - `tests/test_no_legacy_feature_imports.py`
  - `scripts/docs/README.md`
- Standard checks used:
  - `rg -n "if __name__ == ['\"]__main__['\"]" src scripts mcp_server`
  - `rg -n "<symbol-or-module>" src scripts tests mcp_server docs`
  - `rg -n "_close_position_legacy|GENESIS_HTF_EXITS|_global_index|meta\.skip_champion_merge|DEPRECATED" src tests scripts`
  - local AST/import-graph pass over `src/core/**/*.py`, seeded from non-archive entrypoints plus `core.server` and `src/core/optimizer/runner.py`
- Focused verification run in repo venv:
  - `.venv\Scripts\python.exe -m pytest -q tests/test_dead_code_tripwires.py` -> `4 passed`
  - `.venv\Scripts\python.exe -m pytest -q tests/test_no_legacy_feature_imports.py` -> `2 passed`
  - `.venv\Scripts\python.exe -m pytest -q tests/test_htf_exit_engine_selection.py` -> `2 passed`

False-positive guard applied:
- `src/core/strategy/e2e.py:10-35` was not reported as dead even though broad import-reachability docs previously labeled it `NEVER_IMPORTED`; it is a direct `__main__` entrypoint and therefore reachable by execution.

---

## Del 1: Dead Code

### DGZ-DC-001

- Type: Dead code candidate, module + function
- Location: `src/core/risk/sizing.py:6`
- Classification: `CONFIRMED DEAD`
- Risk: `MEDIUM`
- Evidence:
  - `rg -n "capped_position_size\(" src scripts tests mcp_server docs` returns only the defining line in `src/core/risk/sizing.py:6`.
  - `rg -n "core\.risk\.sizing" src scripts tests mcp_server docs` returns only architecture-doc references, not active imports.
  - `docs/architecture/ARCHITECTURE_VISUAL.md:561-602` already records `core.risk.sizing` as `NEVER_IMPORTED`.
- Why unreachable / why dead:
  - The module is not an entrypoint.
  - No import site or call site was found in active runtime, script, MCP, test, or active doc surfaces.
  - The module contains a single helper, `capped_position_size()`, with no observed registry/plugin path that could load it dynamically.
- Notes:
  - This is a repo-internal reachability conclusion only; no external consumer evidence was inspected.

### DGZ-DC-002

- Type: Dead code candidate, deprecated compatibility module
- Location: `src/core/strategy/features.py:10-40`
- Classification: `LIKELY DEAD`
- Risk: `HIGH`
- Evidence:
  - `src/core/strategy/features.py:18-40` marks the module `DEPRECATED` and returns directly to `_extract_features_asof(...)`.
  - `rg -n "core\.strategy\.features\b" src tests docs .github` shows active code usage only in `tests/test_dead_code_tripwires.py:22` plus guardrail references in `tests/test_no_legacy_feature_imports.py`.
  - `tests/test_no_legacy_feature_imports.py:7-48` explicitly fails if internal code imports `core.strategy.features`.
  - `docs/architecture/ARCHITECTURE_VISUAL.md:596` already lists `core.strategy.features` as `DEPRECATED_PATH`.
- Why unreachable / why dead:
  - No active runtime import path was found.
  - The module is not an entrypoint.
  - Remaining repo-local usage is test/guardrail oriented rather than production reachability.
- Notes:
  - `Risk: HIGH` because the file is in `src/core/strategy/*`; no action is proposed in this audit.
  - Not marked `CONFIRMED DEAD` because it still exists as an explicit compatibility surface and could theoretically be imported out-of-band.

### DGZ-DC-003

- Type: Dead code candidate, legacy method inside active runtime class
- Location: `src/core/backtest/position_tracker.py:464-490`
- Classification: `LIKELY DEAD`
- Risk: `HIGH`
- Evidence:
  - `rg -n "_close_position_legacy|_close_position\(" src tests scripts mcp_server docs` shows `_close_position_legacy` only at its definition and in the tripwire test; active close flow goes through `_close_position()` at `src/core/backtest/position_tracker.py:437-439`.
  - `tests/test_dead_code_tripwires.py:49-78` monkeypatches `_close_position_legacy` to raise and still passes via the public `execute_action()` flow.
  - `src/core/backtest/position_tracker.py:247` and `437-439` route active close behavior to `close_position_with_reason(...)`, not to the legacy method.
- Why unreachable / why dead:
  - No repo-local call site reaches `_close_position_legacy`.
  - The current opposite-signal close path is hardwired to `_close_position()` -> `close_position_with_reason(...)`.
  - The remaining legacy method appears retained only as compatibility residue.
- Notes:
  - `Risk: HIGH` because this sits in `src/core/backtest/*`; no action is proposed in this audit.
  - Not marked `CONFIRMED DEAD` because an out-of-band direct method call remains theoretically possible.

### DGZ-DC-004

- Type: Dead code candidate, test-only legacy validator module
- Location: `src/core/config/validator.py:17-29`
- Classification: `NEEDS_HUMAN_REVIEW`
- Risk: `MEDIUM`
- Evidence:
  - `rg -n "core\.config\.validator|validate_config\(|diff_config\(" src scripts tests mcp_server docs` shows active imports only from `tests/test_config_endpoints.py:3`.
  - `docs/architecture/ARCHITECTURE_VISUAL.md:597` labels `core.config.validator` as `TEST_ONLY`.
  - `docs/architecture/ARCHITECTURE.md:17` still documents `core.config.validator.validate_config` and `diff_config` as legacy JSON Schema v1 helpers.
- Why unreachable / why dead:
  - No active runtime or script import was found.
  - However, the module remains documented and is still exercised by tests, which weakens a `CONFIRMED DEAD` claim.
- Notes:
  - Human review is required because this may be an intentional legacy helper surface rather than removable dead code.

---

## Del 2: Zombie Flows

### DGZ-ZF-001

- Type: Zombie flow, legacy feature-engine path
- Location: `src/core/strategy/features.py:27-40`
- Classification: `CONFIRMED ZOMBIE`
- Risk: `HIGH`
- Evidence:
  - `src/core/strategy/features.py:27-40` emits a deprecation warning and immediately returns `_extract_features_asof(...)`.
  - `tests/test_dead_code_tripwires.py:8-46` monkeypatches `_extract_features_asof` and proves `extract_features()` returns the delegated result unchanged.
  - `tests/test_no_legacy_feature_imports.py:7-48` blocks internal imports of `core.strategy.features`.
- Why unreachable / why zombie:
  - The old feature-engine behavior is no longer selectable inside this module.
  - Every invocation of `core.strategy.features.extract_features()` is dominated by an unconditional delegation to ASOF.
- Notes:
  - `Risk: HIGH` because the shim sits in `src/core/strategy/*`; no action is proposed in this audit.

### DGZ-ZF-002

- Type: Zombie flow, legacy close path in public backtest API
- Location: `src/core/backtest/position_tracker.py:437-439`, `src/core/backtest/position_tracker.py:464-490`
- Classification: `CONFIRMED ZOMBIE`
- Risk: `HIGH`
- Evidence:
  - `src/core/backtest/position_tracker.py:437-439` shows `_close_position()` always forwarding to `close_position_with_reason(...)`.
  - `rg -n "_close_position_legacy|_close_position\(" src tests scripts mcp_server docs` finds no active repo-local caller of `_close_position_legacy`.
  - `tests/test_dead_code_tripwires.py:49-78` installs a tripwire on `_close_position_legacy` and the public `execute_action()` close/open sequence still passes.
- Why unreachable / why zombie:
  - In the active public flow, an opposite signal no longer has any path to `_close_position_legacy`.
  - The legacy close method remains present, but the current control flow bypasses it deterministically.
- Notes:
  - `Risk: HIGH` because this is in `src/core/backtest/*`; no action is proposed in this audit.

### DGZ-ZF-003

- Type: Zombie flow, deprecated wrapper path inside internal feature runtime
- Location: `src/core/strategy/features_asof.py:1036-1084`, `src/core/strategy/evaluate.py:11`, `src/core/strategy/evaluate.py:188-200`
- Classification: `LIKELY`
- Risk: `HIGH`
- Evidence:
  - `src/core/strategy/features_asof.py:1036-1084` marks `extract_features(...)` as deprecated compatibility wrapper.
  - `src/core/strategy/evaluate.py:11` imports `extract_features_backtest` and `extract_features_live`, not the deprecated wrapper.
  - `src/core/strategy/evaluate.py:188-200` explicitly uses the live/backtest split and comments that the deprecated wrapper should be avoided in core runtime code.
  - `tests/test_no_legacy_feature_imports.py:51-98` blocks internal imports of `core.strategy.features_asof.extract_features`, except for the narrow allow-list.
- Why unreachable / why zombie:
  - The intended internal runtime route no longer goes through the deprecated wrapper.
  - Reaching the wrapper from internal active code would require introducing a new import that current guardrails are designed to fail on.
- Notes:
  - Not marked `CONFIRMED ZOMBIE` because tests and compatibility callers still use the wrapper by design.
  - `Risk: HIGH` because the wrapper sits in strategy runtime code; no action is proposed in this audit.

### DGZ-ZF-004

- Type: Zombie flow, former HTF-exit mismatch path
- Location: `src/core/backtest/engine.py:259-287`
- Classification: `LIKELY`
- Risk: `HIGH`
- Evidence:
  - `src/core/backtest/engine.py:260-272` resolves engine selection as:
    - explicit env wins
    - otherwise non-empty `htf_exit_config` selects the new path
  - `tests/test_dead_code_tripwires.py:88-132` passes both:
    - env unset + non-empty config -> `_use_new_exit_engine is True`
    - invalid env value -> warning + legacy fallback
  - `tests/test_htf_exit_engine_selection.py:4-38` passes both:
    - env unset + config -> new engine
    - explicit `GENESIS_HTF_EXITS=0` -> legacy remains authoritative
- Why unreachable / why zombie:
  - The older “manual backtest with config present but env unset silently lands in legacy engine” path is no longer the default branch in current code.
  - The legacy path remains live only when explicitly forced by env or when new-engine availability collapses.
- Notes:
  - Not marked `CONFIRMED ZOMBIE` because explicit `GENESIS_HTF_EXITS=0` and `NewExitEngine is None` still keep a real legacy path alive.
  - `Risk: HIGH` because this sits in backtest engine selection; no action is proposed in this audit.

---

## Excluded From Candidate Scope

- `archive/**`
- `scripts/archive/**`
- Historical docs as standalone findings
- Opportunistic cleanup or inferred remediation

Dead-zone rule used:
- `scripts/docs/README.md:16` classifies `scripts/archive/**` as archive.
- `scripts/docs/README.md:50` states `scripts/archive/**` is ignored in internal reference counting.

Archive material was used only as background context, not as a candidate source of findings in this report.

---

## Confidence / Limits

- This audit is strong on repo-internal reachability and explicit control-flow dominance.
- It is weaker on hypothetical external consumers that are not represented in repo entrypoints, tests, docs or scripts.
- Findings in `src/core/strategy/*` and `src/core/backtest/*` were intentionally classified conservatively because those zones are runtime-sensitive.
- Broad import-reachability documents in `docs/architecture/ARCHITECTURE_VISUAL.md` were treated as supporting evidence, not as sole proof, because they can undercount direct `__main__` entrypoints such as `src/core/strategy/e2e.py:34-35`.
