# Feature-cache docs truthfulness narrowing packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `docs-truthfulness-narrowed / docs-only / non-authorizing`

This packet records the bounded docs-only `#12` follow-up after the writer/schema-owner trace. It grants no runtime, backtest, optimizer, training, cache-policy, schema-enforcement, CI, launch, paper/live, or promotion authority. It must not be read as approval to modify `src/**`, `tests/**`, or `scripts/**` runtime behavior.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/*`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice narrows stale command/path claims only; no runtime or schema semantics are changed
- **Required Path:** `Quick`
- **Lane:** `Research-evidence`
- **Objective:** narrow current docs so they no longer present absent standalone feature-artifact producer/helper scripts as live branch commands
- **Candidate line:** `#12 docs-truthfulness narrowing`

### Scope

- **Scope IN:** this packet; `docs/features/FEATURE_COMPUTATION_MODES.md`; `scripts/docs/DATA_FETCH_GUIDE.md`; `data/DATA_FORMAT.md`; one small `handoff.md` live-note refinement
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, and runtime-bearing `scripts/**`; all cache/schema behavior changes; all claims that a current tracked feature-artifact writer/schema-owner now exists

### Gates required

- targeted docs validation for changed markdown files
- manual path audit for every referenced script/test/doc path
- manual wording audit that runtime precompute/cache CLI and read-side feature artifacts remain clearly separated
- self-review for hidden behavior impact

## Governing basis

### Observed

1. `scripts/run/run_backtest.py` exists on the current branch and `--help` exposes both `--fast-window` and `--precompute-features`.
2. Repo-wide file search on the current branch does **not** find:
   - `scripts/precompute_features_v17.py`
   - `scripts/validate_data.py`
   - `scripts/comprehensive_feature_analysis.py`
   - `README.agents.md`
   - top-level `scripts/run_backtest.py`
3. `tests/utils/test_feature_parity.py` and `tests/integration/test_precompute_vs_runtime.py` both exist on the current branch.
4. `docs/features/FEATURE_COMPUTATION_MODES.md`, `scripts/docs/DATA_FETCH_GUIDE.md`, and `data/DATA_FORMAT.md` still contained stale command/path language that treated absent helper scripts as current branch reality.

### Inferred

- The current branch does ground a **runtime precompute/cache CLI path** via `scripts/run/run_backtest.py`.
- The current branch does **not** ground a standalone tracked feature-artifact producer CLI for regenerating the read-side v17/v18 artifacts.
- The most honest docs narrowing is therefore to point users at the current runtime CLI and current test/read-side paths without claiming a live standalone producer.

### Unverified in this packet

- whether any external or untracked local script still regenerates read-side feature artifacts outside the tracked repo surface
- whether any historical archived script should later be restored or formally documented elsewhere

## What changed in this slice

- current docs now point to `scripts/run/run_backtest.py` where they previously pointed to absent top-level runner or standalone precompute helper paths
- stale references to absent `validate_data.py`, `comprehensive_feature_analysis.py`, and `README.agents.md` are removed or narrowed to current tracked surfaces
- `handoff.md` now records that the docs-truthfulness narrowing for `#12` is landed

## What did not change

- no runtime/backtest/training/cache behavior changed
- no feature-artifact writer/schema-owner was introduced
- no schema-version authority was introduced
- no claim is made here that read-side feature artifacts are fully obsolete

## Bottom line

`#12` now has both the writer/schema-owner trace and the current docs-truthfulness narrowing landed on this branch. The docs no longer present absent standalone producer/helper scripts as current commands, and `#12` should stay out of code-bearing implementation unless a new tracked writer/schema-owner is later grounded.
