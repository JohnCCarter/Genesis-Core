# RI policy router insufficient-evidence discriminator-bundle displacement crosscheck packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / read-only recurrence-falsifier crosscheck / no behavior change`

Relevant skills: `decision_gate_debug`, `python_engineering`

Active repository skill for this slice: `python_engineering.json`, covering the read-only
analysis script, any focused pure-helper test, and the associated evidence-note updates.

Skill coverage for this slice is explicit and bounded:

- `decision_gate_debug` governs the gate-oriented reading and mechanism separation between the already-fixed `insufficient_evidence` target rows and the already-fixed nearby `stable_continuation_state` displacement rows.
- `python_engineering` governs the typed helper structure, focused unit test coverage for any new pure logic, and the minimal-diff validation path.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads only already-fixed action-diff rows plus curated candles, emits one bounded JSON artifact plus one analysis note, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the fixed 2021-vs-2025 target contrast is complete, so the next honest question is whether the candidate discriminator bundle survives a falsifier against the already-fixed nearby displacement rows rather than a fresh annual scan or runtime speculation.
- **Objective:** test whether the candidate discriminator bundle from the fixed March 2021 vs March 2025 target contrast also separates the already-fixed target rows from their nearby displacement rows inside the same windows, or whether it collapses into a generic target-vs-displacement distinction.
- **Candidate:** `fixed March 2021/2025 target-vs-displacement discriminator crosscheck`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`

## Exact proposed subject

### Fixed March 2021 rows

Target rows:

- `2021-03-26T12:00:00+00:00`
- `2021-03-27T06:00:00+00:00`
- `2021-03-27T15:00:00+00:00`
- `2021-03-28T00:00:00+00:00`

Fixed row count: `4`

Nearby displacement comparison rows:

- `2021-03-26T15:00:00+00:00`
- `2021-03-29T00:00:00+00:00`

Fixed row count: `2`

### Fixed March 2025 rows

Target rows:

- `2025-03-14T15:00:00+00:00`
- `2025-03-15T00:00:00+00:00`
- `2025-03-15T09:00:00+00:00`
- `2025-03-15T18:00:00+00:00`
- `2025-03-16T03:00:00+00:00`

Fixed row count: `5`

Nearby displacement comparison rows:

- `2025-03-13T15:00:00+00:00`
- `2025-03-14T00:00:00+00:00`

Fixed row count: `2`

### Allowed comparison surface

This slice is a fixed-surface observational crosscheck. It is fail-closed to four pre-fixed cohorts
only: the exact March 2021 target timestamps (`4` rows), the exact March 2021 nearby displacement
timestamps (`2` rows), the exact March 2025 target timestamps (`5` rows), and the exact March 2025
nearby displacement timestamps (`2` rows) already identified in the completed local-window notes.
No representative-row reselection, nearest-neighbor expansion, threshold sweep, year-wide mining,
extra local-window discovery, or runtime-semantics inference is in scope.

The helper may read only the existing action-diff rows and their existing router-debug payloads from:

- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2021_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

Allowed comparison fields are limited to the shared blocked-shape descriptors already surfaced in
the completed 2026-04-30 target contrast plus the candidate separator bundle and the same fixed
observational candle proxies already used in the 2026-04-29 anchor notes.

Exact allowlist for this slice:

- top-level action-diff fields: `timestamp`, `absent_action`, `enabled_action`
- router-debug blocked-shape descriptors: `switch_reason`, `zone`, `selected_policy`, `raw_target_policy`, `regime`, `confidence_level`, `mandate_level`, `switch_proposed`, `switch_blocked`
- candidate separator fields: `bars_since_regime_change`, `dwell_duration`, `action_edge`, `confidence_gate`, `clarity_raw`, `clarity_score`
- candle observational proxies: `fwd_4_close_return_pct`, `fwd_8_close_return_pct`, `fwd_16_close_return_pct`, `mfe_16_pct`, `mae_16_pct`

No other router-debug fields, separators, years, or neighbor-discovery rules are in scope.
The source-row allowlist applies only to extracted cohort records. Derived output is limited to
provenance, row-lock counts, cohort summaries, within-year target-minus-displacement gaps, and
cross-year recurrence classification computed from that allowlisted row surface.

The helper may derive simple descriptive contrasts such as:

- target mean minus nearby-displacement mean within 2021
- target mean minus nearby-displacement mean within 2025
- 2021 gap minus 2025 gap on the same metric
- shared-signature or diverging-signature summaries across the four fixed cohorts

### Exact output paths to materialize

- JSON artifact: `results/evaluation/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.json`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.md`

The JSON artifact must include fixed-surface provenance with:

- exact source JSON paths
- the fixed field allowlist and fixed proxy allowlist
- exact cohort membership for all four cohorts
- fixed row counts for all four cohorts
- stable deterministic ordering of cohorts, timestamps, and emitted summaries

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_packet_2026-04-30.md`
  - `scripts/analyze/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_20260430.py`
  - `tests/backtest/test_ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck.py`
  - `results/evaluation/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.json`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.md`
- **Scope OUT:**
  - no runtime/config/schema/authority/default changes
  - no new backtest reruns
  - no widening to additional years or additional local windows
  - no representative-row mining, stronger-row benchmarking, or alternate cohort discovery beyond the fixed rows above
  - `GENESIS_WORKING_CONTRACT.md` remains OUT of scope by default and may be reopened only after the artifact exists and only if the crosscheck materially narrows the next admissible step
  - no edits to the completed local-window helper, positive-year control wrapper, or target-contrast helper unless strictly required to resolve import/runtime issues in the new crosscheck helper; if that becomes necessary, stop and re-review rather than widening silently
  - no promotion/readiness/champion claims
- **Expected changed files:** 5-6
- **Max files touched:** 6

## Evidence anchors

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2021_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2025_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`

## Planned method

1. load the exact already-fixed 2021 target rows, 2021 nearby displacement rows, 2025 target rows, and 2025 nearby displacement rows only
2. normalize one bounded descriptive signature per row from existing `enabled.router_debug` fields plus the same candle-side observational proxies already used in the earlier notes
3. summarize target-vs-displacement contrasts inside each year and compare whether the candidate discriminator bundle stays specific to the harmful 2021 target cluster or appears as the same separation in both years
4. keep all conclusions descriptive and non-authoritative, explicitly allowing the crosscheck to weaken the current candidate bundle if the falsifier says so

Results in this slice are descriptive/observational only. They do not authorize a runtime
threshold, router-policy change, family/champion/promotion claim, or readiness conclusion. If
`GENESIS_WORKING_CONTRACT.md` is ever reopened after the artifact exists, any wording change must
remain explicitly `föreslagen`, not `införd`.

## Validation requirements

- `get_errors` on the new packet/script/test/note and any touched contract file
- repo-standard lint/format on touched code (`ruff check` and `pre-commit run --files`)
- one deterministic smoke execution of the new script against the frozen source JSONs
- deterministic repeat-run proof with stable identical JSON output
- artifact schema plus fixed-row-count verification proving the emitted cohort membership, exact timestamps, row counts, and fixed field/proxy allowlists match this packet exactly
- focused unit tests only if new pure helper logic is extracted; otherwise the deterministic smoke execution plus schema/count verification is the minimum sufficient test surface
- explicit ignored/staging check on the new `results/evaluation` artifact
- manual diff review confirming no runtime/config/default/authority drift
- any broader runtime/pipeline gates must either be executed or explicitly marked `N/A` with untouched-surface rationale; they may not be silently omitted

Done criteria for this slice:

- the script produces one deterministic JSON artifact from the fixed inputs only
- a repeat run confirms stable output ordering/content
- missing or duplicate selected rows, missing required fields, unstable artifact output, or widened selector logic are FAIL
- runtime/config/default/authority surfaces remain untouched

## Stop conditions

- the helper starts depending on runtime imports from `src/**`
- the crosscheck requires widening into fresh annual sweeps or additional local windows to say anything honest
- the row payloads do not expose enough stable fields to compare the fixed cohorts honestly
- the note starts implying runtime tuning or promotion authority
- scope drifts into editing the already-completed 2026-04-29 or 2026-04-30 slice files instead of adding one bounded falsifier layer

## Output required

- one deterministic JSON summary artifact for the fixed four-cohort crosscheck
- one human-readable analysis note stating what the crosscheck does and does not justify for the robust-policy question
- exact command run and validation outcomes
