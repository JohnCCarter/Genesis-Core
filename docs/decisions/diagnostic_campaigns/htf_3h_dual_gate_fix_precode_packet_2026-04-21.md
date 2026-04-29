# HTF 3h dual-gate fix pre-code packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-reviewed / APPROVED_WITH_NOTES / implementation authorized within locked scope only`

Pre-code verdict note (2026-04-22):

- Opus 4.6 verdict: `APPROVED_WITH_NOTES`
- Authorized implementation scope remains locked to the two source seams, two targeted tests, and status synchronization in this packet/bug doc only.
- This status does **not** imply implemented fix, passed gates, or post-diff approval.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice changes live strategy/backtest behavior on the 3h lane by enabling HTF context where it is currently silently disabled; the seam touches both `src/core/strategy/*` and `src/core/indicators/*` and flows into `compute_htf_regime`, HTF gate behavior, and HTF-aware sizing.
- **Required Path:** `Full`
- **Objective:** implement the smallest admissible fix that enables HTF context on `3h` by correcting both blocking seams while preserving non-`3h` semantics exactly and keeping LTF context semantics unchanged in this slice.
- **Candidate:** `HTF 3h dual-gate fix (slice 1)`
- **Base SHA:** `deb4cd68`
- **Constraints:** explicit **behavior-change exception** limited to `timeframe="3h"` on the HTF path only; no other timeframe eligibility changes, no LTF-context broadening, no selector-policy changes, no config/champion/default mutations.

## Problem statement

Current evidence shows that `3h` is blocked in two separate seams:

1. `src/core/strategy/features_asof_parts/context_bundle_utils.py`
   - `_ELIGIBLE_TIMEFRAMES = {"1h", "30m", "6h", "15m"}`
   - this prevents the feature pipeline from building HTF context on `3h`
2. `src/core/indicators/htf_fibonacci_context.py`
   - runtime allowlist also excludes `"3h"`
   - direct calls therefore return `HTF_NOT_APPLICABLE`

A one-file fix is therefore insufficient.

## Scope

- **Scope IN:**
  - `src/core/strategy/features_asof_parts/context_bundle_utils.py`
  - `src/core/indicators/htf_fibonacci_context.py`
  - `tests/utils/test_features_asof_context_bundle.py`
  - `tests/utils/test_htf_fibonacci_context_edge_cases_table.py`
  - `docs/bugs/HTF_ALLOWLIST_MISSING_3H_20260421.md`
  - `docs/decisions/diagnostic_campaigns/htf_3h_dual_gate_fix_precode_packet_2026-04-21.md`
- **Scope OUT:**
  - `src/core/strategy/htf_selector.py` (already supports `3h` via `TIMEFRAME_TO_MINUTES["3h"] = 180`; no selector-policy edits)
  - `src/core/strategy/evaluate.py`
  - `src/core/intelligence/regime/htf.py`
  - `src/core/strategy/decision.py`
  - all `config/**` and `config/strategy/champions/**`
  - all `results/**`, `artifacts/**`, `logs/**`, `cache/**`
  - any runtime observability/logging enhancement
  - any LTF-context broadening for `3h`
  - any expansion to `4h`, `12h`, or other non-requested timeframes
  - any champion re-evaluation, backtest campaign, promotion, or runtime-default authority work
- **Expected changed files:** `5-6`
- **Max files touched:** `6`

## Intended implementation shape

This slice should remain the smallest behavior-changing fix that solves the verified defect:

1. Split `context_bundle_utils.py` eligibility so HTF and LTF are no longer hard-coupled behind the same set.
   - HTF eligibility becomes `{15m, 30m, 1h, 3h, 6h}`
   - LTF eligibility remains unchanged from current semantics in this slice
2. Extend the HTF runtime allowlist in `htf_fibonacci_context.py` to include `3h`
3. Add targeted tests proving:
   - `3h` now builds HTF context via the bundle path
   - `3h` still does **not** force a new LTF-context behavior change in the bundle path
   - runtime HTF context accepts `3h` with valid cached HTF data
   - `4h` and other non-eligible timeframes remain `HTF_NOT_APPLICABLE`

## Gates required

- `pre-commit run --all-files`
- `python -m pytest -q`
- focused selectors:
  - `python -m pytest -q tests/utils/test_features_asof_context_bundle.py`
  - `python -m pytest -q tests/utils/test_htf_fibonacci_context_edge_cases_table.py`
  - `python -m pytest -q tests/utils/test_htf_fibonacci_context_requires_reference_ts.py`
  - `python -m pytest -q tests/utils/test_htf_fibonacci_context_levels_completeness.py`
  - `python -m pytest -q tests/utils/test_htf_fibonacci_context_invalid_swing_bounds.py`
  - `python -m pytest -q tests/utils/test_features_asof_context_bundle.py::test_build_fibonacci_context_bundle_enables_htf_only_for_3h`
  - `python -m pytest -q tests/utils/test_htf_fibonacci_context_edge_cases_table.py::test_get_htf_fibonacci_context_accepts_3h_when_cached_levels_are_valid`
  - `python -m pytest -q tests/utils/test_htf_fibonacci_context_edge_cases_table.py::test_get_htf_fibonacci_context_edge_cases_table[timeframe not applicable]`
- touched-flow regression / smoke requirement:
  - prove that the `3h` feature-bundle path now invokes HTF-context construction without invoking a new LTF-context path in the same slice
  - prove that direct runtime HTF-context calls on `3h` no longer return `HTF_NOT_APPLICABLE`
  - prove that `4h` continues to return `HTF_NOT_APPLICABLE`
- required invariants:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- security/lint baseline for the final implementation cycle:
  - `python -m ruff check src tests`
  - `python -m black --check src tests`
  - `bandit -r src -c bandit.yaml`

## Stop Conditions

- any evidence that a source surface beyond the two identified blockers must also change
- any need to broaden LTF-context semantics for `3h` to make the HTF fix work
- any evidence that `3h` begins building LTF-context as part of this slice
- any need to touch `evaluate.py`, `decision.py`, selector policy, config defaults, champion files, or runtime authority paths
- any behavior drift for non-`3h` timeframes
- any behavior drift in bundle semantics for `4h` or other currently ineligible timeframes
- any determinism, cache-key, or pipeline-hash regression
- any attempt to expand scope to 4h/12h/other timeframe enablement in the same slice

## Output required

- minimal implementation diff for the two blocking seams only
- targeted regression tests for `3h` enablement + non-`3h` preservation
- implementation report with exact gates and outcomes
- Opus post-diff audit before any commit claim

## Evidence anchor

- bug doc: `docs/bugs/HTF_ALLOWLIST_MISSING_3H_20260421.md`
- extended evidence: `docs/analysis/recommendations/ri_bucket_sample_expansion_b1_findings_2026-04-21.md`
- verified symptom: `htf_regime = "unknown"` in all 715 extended rows on `2018–2025`

## Skill usage

- Repo-local skills loaded/applied:
  - `.github/skills/python_engineering.json` — implementation discipline, typed Python, lint/security/test baseline
  - `.github/skills/feature_parity_check.json` — parity guard for feature-surface changes touching `features_asof` orchestration
- Pre-code review anchor:
  - `feature_parity_check` is the explicit parity/governance SPEC for preserving non-`3h` feature behavior while opening the `3h` HTF path only
- Post-diff audit anchor:
  - `feature_parity_check` must be cited again during post-diff audit together with determinism/cache/pipeline invariants
- Optional fallback diagnostic only if the implementation unexpectedly changes trade flow:
  - `.github/skills/decision_gate_debug.json`
- Governance authority for this slice remains the packet + Opus review, not the skills themselves.
