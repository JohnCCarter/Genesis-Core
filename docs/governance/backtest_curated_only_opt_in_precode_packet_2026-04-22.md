# Backtest curated-only opt-in pre-code packet

Date: 2026-04-22
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-reviewed / APPROVED_WITH_NOTES / implementation authorized within locked scope only`

Pre-code verdict note (2026-04-22):

- Opus 4.6 verdict: `APPROVED_WITH_NOTES`
- Authorized implementation scope remains locked to explicit backtest data-source policy plumbing, targeted tests, and packet synchronization only.
- This status does **not** imply implemented fix, passed gates, or post-diff approval.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `tooling`
- **Risk:** `MED` — why: this slice changes backtest data-source selection behavior for an explicit opt-in path in `src/core/backtest/*` and the CLI runner, while default behavior must remain unchanged; incorrect implementation could silently change historical coverage, HTF provenance, or comparability.
- **Required Path:** `Full`
- **Objective:** implement the smallest admissible fix that introduces an explicit opt-in `curated_only` backtest data-source policy for both LTF and HTF candle loading, while preserving the current default `frozen_first` behavior exactly.
- **Candidate:** `Historical curated-only backtest data-source policy (slice 1)`
- **Base SHA:** `e626ca2b`
- **Constraints:** explicit **no-default-drift** contract; default data-source selection must remain `frozen_first`; no runtime/API/optimizer/config-default drift; only backtest data-source selection may change when explicit opt-in is provided; no champion/default/config-authority changes; no strategy logic changes; no promotion/runtime claims; no hidden fallback heuristics in this slice.

## Problem statement

Current evidence shows that older-year historical coverage is being masked by a hard-coded source-priority policy rather than missing datasets:

1. `src/core/backtest/engine.py`
   - `load_data()` always prefers `data/raw/*_frozen.parquet` before curated/legacy.
   - HTF loading for `1D` applies the same frozen-first ordering.
2. Verified repo data coverage shows:
   - `data/raw/tBTCUSD_3h_frozen.parquet` and `data/raw/tBTCUSD_1D_frozen.parquet` cover only late-2023 to early-2026.
   - `data/curated/v1/candles/tBTCUSD_3h.parquet` and `.../tBTCUSD_1D.parquet` contain 2016–2026 history.
3. Curated-only read-only probes proved older years are runnable when the engine is pointed at curated data, so `empty dataset` on older years is not the same thing as missing history.

Therefore the smallest safe fix is an explicit opt-in policy, not a silent default reorder.

## Scope

- **Scope IN:**
  - `src/core/backtest/engine.py`
  - `src/core/pipeline.py`
  - `scripts/run/run_backtest.py`
  - `tests/backtest/test_backtest_engine.py`
  - `docs/governance/backtest_curated_only_opt_in_precode_packet_2026-04-22.md`
- **Scope OUT:**
  - all strategy logic surfaces under `src/core/strategy/**`
  - champion/config-authority/runtime-default files under `config/**`
  - optimizer/preflight surfaces such as `scripts/preflight/**`
  - `data/**` contents and dataset mutation
  - any auto-fallback policy such as `curated_fallback_on_empty`
  - all `results/**`, `artifacts/**`, `logs/**`, `cache/**`
  - unrelated existing untracked docs: `GENESIS_WORKING_CONTRACT.md`, `docs/analysis/ri_bucket_sample_expansion_b1_findings_2026-04-21.md`, `docs/bugs/RI_BUCKET_SAMPLE_EXPANSION_B1_20260421.md`
- **Expected changed files:** `4-5`
- **Max files touched:** `5`

## Intended implementation shape

This slice should remain the smallest opt-in, provenance-safe change:

1. Introduce a backtest data-source policy surface with exactly two options in this slice:
   - `frozen_first` (default, current behavior)
   - `curated_only` (explicit opt-in)
2. Apply the policy consistently to both:
   - primary candle loading for the requested timeframe
   - HTF candle loading for `1D`
3. Thread the policy through the pipeline and CLI runner.
4. Emit the selected policy and actual chosen LTF/HTF files in backtest metadata so artifact provenance is explicit.
5. Add targeted regression tests proving:
   - default still chooses frozen when frozen exists
   - `curated_only` chooses curated even when frozen exists
   - the same policy applies to HTF loading

- invalid policy values are rejected explicitly
- `curated_only` does not fall back to frozen implicitly
- default behavior remains unchanged for the existing frozen-first path

6. Minimal backtest-local cache isolation is allowed inside `src/core/backtest/engine.py` if required to prevent frozen/curated cross-contamination.

- This is a bounded cache-namespace exception only; it prevents frozen/curated aliasing without changing default `frozen_first` ordering or backtest result semantics.
- Any such cache isolation must remain scoped to the selected candle source/policy for this engine path only.
- No broader cache contract redesign is authorized in this slice.

7. Provenance additions must remain strictly additive inside transient backtest metadata / CLI surface only.

- If provenance requires changes to persistent artifact formats, logs, cache keys, or broader result contracts, stop and re-scope.

## Gates required

- `python -m ruff check src tests scripts/run/run_backtest.py`
- `python -m bandit -r src -c bandit.yaml`
- focused selectors:
  - `python -m pytest -q tests/backtest/test_backtest_engine.py`
  - `python -m pytest -q tests/backtest/test_backtest_engine.py -k "data_source or curated or frozen"`
- required invariants:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`
- touched-flow smoke requirements:
  - default frozen-first smoke remains runnable for `2024` using `run_backtest.py --no-save`
  - opt-in curated-only smoke becomes runnable for an older year such as `2017` using `run_backtest.py --no-save`

## Stop Conditions

- any evidence that default frozen-first behavior drifts
- any evidence that policy plumbing through `GenesisPipeline` affects non-backtest callers or requires changed env/config interpretation
- any need to modify strategy logic, champion configs, or runtime authority paths
- any need to introduce automatic curated fallback heuristics in the same slice
- any inconsistency where LTF and HTF data-source policies diverge unintentionally
- any need to mutate persistent artifact formats, logs, or cache keys to satisfy provenance requirements
- any determinism/cache/pipeline guard regression
- any attempt to widen scope into research artifact cleanup or promotion semantics

## Output required

- minimal implementation diff for explicit data-source policy only
- targeted regression tests for default parity + curated-only opt-in
- implementation report with exact gates and outcomes
- Opus post-diff audit before any commit claim

## Evidence anchor

- `src/core/backtest/engine.py` frozen-first source ordering
- verified curated coverage probes and curated-only yearly execution probes from 2026-04-22 terminal runs
- repo memory anchor: `/memories/repo/backtest_curated_shadowing_verified_2026-04-22.json`

## Skill usage

- Repo-local skills loaded/applied:
  - `.github/skills/python_engineering.json`
  - `.github/skills/backtest_run.json`
  - `.github/skills/genesis_backtest_verify.json`
- Skill usage is part of the implementation contract for this slice and must remain explicit in implementation/audit reporting.
- Governance authority for this slice remains the packet + Opus review, not the skills themselves.
