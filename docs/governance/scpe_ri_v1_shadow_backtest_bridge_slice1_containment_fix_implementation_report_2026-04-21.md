# SCPE RI V1 shadow-backtest bridge slice1 containment-fix implementation report

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_packet_2026-04-21.md`
Skills used: `python_engineering`, `repo_clean_refactor`

This slice removes the out-of-bound filesystem-touch side effect from `scripts/run/run_backtest.py` while preserving config-package resolution, canonical CLI behavior, bounded decision-row outputs, `--no-save` suppression semantics, and intelligence-shadow summary / ledger-root behavior.

## Scope summary

### Scope IN

- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_packet_2026-04-21.md`
- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_report_2026-04-21.md`
- `scripts/run/run_backtest.py`

### Scope OUT

- `src/**`
- `tests/**` edits
- `config/**` edits
- writable-surface expansion
- CLI semantics changes
- intelligence-shadow derivation changes
- launch re-authorization
- runtime integration / paper / readiness / cutover / promotion widening
- unrelated tracked or untracked working-tree changes

## File-level change summary

- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_packet_2026-04-21.md`
  - Added the bounded one-file implementation contract and exact gate set for the containment fix.
- `scripts/run/run_backtest.py`
  - Removed the unconditional bootstrap side-effect block:
    - `CONFIG_DIR = ROOT_DIR / "config"`
    - `CONFIG_DIR.mkdir(exist_ok=True)`
    - `(CONFIG_DIR / "__init__.py").touch(exist_ok=True)`
  - Preserved `ROOT_DIR` / `SRC_DIR` bootstrap and `sys.path` insertion unchanged.
- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_report_2026-04-21.md`
  - Added this implementation report.

## Exact gates run and outcomes

### Commands executed

1. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --help`
   - Result: `PASS`
2. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -c "import sys; from pathlib import Path; root=Path(r'C:/Users/fa06662/Projects/Genesis-Core'); sys.path.insert(0,str(root)); sys.path.insert(0,str(root/'src')); import config; print(config.__all__)"`
   - Result: `PASS`
   - Output: `['timeframe_configs']`
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/run/run_backtest.py`
   - Result: `PASS`
4. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_run_backtest_decision_rows.py tests/backtest/test_run_backtest_intelligence_shadow.py tests/backtest/test_run_backtest_mode_flags.py`
   - Result: `PASS` (`10 passed`)
5. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
   - Result: `PASS` (`3 passed`)
6. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_features_asof_cache_isolation.py::test_feature_cache_key_separates_precompute_and_runtime_modes`
   - Result: `PASS` (`1 passed`)
7. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
   - Result: `PASS` (`1 passed`)

### Editor diagnostics

- `scripts/run/run_backtest.py`
  - Result: `PASS` (`No errors found`)

## Governance review outcomes

### Opus pre-code review

Verdict:

- `APPROVED`

Recorded conditions:

- keep the diff strictly inside `scripts/run/run_backtest.py`
- run the full approved gate set without reduction
- stop on config-package proof failure, canonical `--help` smoke failure, or any need for scope widening

### Opus post-diff audit

Verdict:

- `APPROVED`

Recorded conclusion:

- the diff stays confined to removing the unconditional mkdir/touch side effect
- the supplied evidence is sufficient for a no-behavior-change assessment on the intended surfaces
- no code remediation was required after audit

## Boundary proof

- `config` package resolution remains valid from tracked repo state without recreating or touching `config/__init__.py` at runtime.
- Canonical CLI help output remains available.
- Targeted `run_backtest` behavior surfaces remained green after the diff.
- Determinism replay, feature-cache invariance, and pipeline component-order hash guard all remained green.
- No writable-surface expansion was introduced.
- This slice does **not** re-authorize a shadow/control execution and does **not** reopen runtime, paper, readiness, cutover, or promotion scope.

## Residual risks

- This fix assumes the tracked repo package initializer `config/__init__.py` continues to exist; if that file is later removed, that is a separate packaging regression rather than grounds to restore filesystem-touch behavior in the script.
- The earlier launch-authorization packet remains a historical `NOT AUTHORIZED NOW` decision under the then-current evidence state; any future execution decision still requires its own separate re-authorization step.
- Unrelated local working-tree changes remain out of scope for this slice and were intentionally not absorbed.

## READY_FOR_REVIEW evidence completeness

- Mode / risk / path: captured above
- Scope IN / OUT: captured above
- Exact gates and outcomes: captured above
- Evidence paths:
  - `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_packet_2026-04-21.md`
  - `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_report_2026-04-21.md`
  - `scripts/run/run_backtest.py`

## Lane-status conclusion

For the **containment-fix implementation lane itself**, no additional slices or docs are required before implementation:

- the pre-code packet exists
- the implementation packet exists
- the code diff is landed
- the approved gate set passed
- the post-diff audit is green
- this implementation report now closes the lane's documentation loop

Any further document would belong to a **different** question, such as later execution re-authorization for the RI-only shadow run, not to this implementation slice.

## Bottom line

The containment blocker identified in the write-boundary audit is now removed from `scripts/run/run_backtest.py` with no observed behavior drift on the approved guard surfaces.

This implementation lane is documentation-complete and implementation-ready status is satisfied for the fix that was scoped here.
