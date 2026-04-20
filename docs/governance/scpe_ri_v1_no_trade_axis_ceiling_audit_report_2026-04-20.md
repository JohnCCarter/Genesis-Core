# SCPE RI V1 no-trade axis ceiling audit report

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Path: `Full`
Constraint: `NO BEHAVIOR CHANGE`
Packet: `docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_packet_2026-04-20.md`
Skills used: `python_engineering`

This audit is observational-only and evaluates whether the frozen no-trade release axis can satisfy individual replay-quality gate components under unchanged baseline and first-revision inputs.

It does not authorize a new revision rule, does not change the current `NEEDS_REVISION` recommendation, and classifies each gate component only as `satisfiable`, `unsatisfiable`, or `unresolved` on this bounded axis alone.

This audit is observational-only and bounded to the frozen baseline and first-revision artifacts. It does not introduce or recommend a new release rule, does not alter baseline or revision recommendation semantics, and only assesses whether the existing replay-quality gate can be satisfied on the no-trade axis alone.

Any follow-up paths are `föreslagen` hypotheses only and are out of scope for this slice.

## Scope summary

### Scope IN

- `docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py`
- `results/evaluation/scpe_ri_v1_no_trade_axis_ceiling_audit_2026-04-20.json`

### Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `artifacts/**`
- `tmp/**`
- `results/research/**`
- `docs/scpe_ri_v1_architecture.md`
- runtime integration
- canonical replay regeneration
- edits to `scripts/analyze/scpe_ri_v1_router_replay.py`
- edits to `scripts/analyze/scpe_ri_v1_no_trade_release_revision.py`
- edits to baseline or revision recommendation semantics
- any new experimental release rule

## File-level change summary

- `docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_packet_2026-04-20.md`
  - Added the bounded contract for an observational-only constraint-mapping audit of the no-trade release axis.
- `scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py`
  - Added a tracked audit script that reads frozen baseline and first-revision artifacts, decomposes the replay-quality gate, records input hashes, and emits a constraint verdict without introducing a new revision rule.
- `results/evaluation/scpe_ri_v1_no_trade_axis_ceiling_audit_2026-04-20.json`
  - Added a commit-safe artifact that records gate-component status, axis satisfiability classification, frozen input hashes, and the ceiling verdict.
- `docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md`
  - Added this implementation report.

## Audit method

- frozen inputs:
  - baseline replay metrics: `results/research/scpe_v1_ri/replay_metrics.json`
  - baseline replay manifest: `results/research/scpe_v1_ri/manifest.json`
  - first revision artifact: `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`
- frozen input hashes:
  - baseline replay metrics sha256 = `f46cc0e1fb0418b6fe8b1759571cb9e967343595c9be85378d09e28492dcfe60`
  - baseline replay manifest sha256 = `273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
  - first revision artifact sha256 = `6423bc2811a0ec7ee137acd5088b2602ea70440c4255cccced4e1024c12c9afe`
- gate decomposition:
  - continuation trade floor: `trade_count >= 10`
  - defensive trade floor: `trade_count >= 10`
  - actual policy change rate ceiling: `actual_policy_change_rate <= 0.25`
- classification surface:
  - `satisfiable`
  - `unsatisfiable`
  - `unresolved`
- read-only inputs confirmed: `true`

## Exact gates run and outcomes

### Commands executed

1. Explicit smoke gate:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py`
   - Result: `PASS`
2. Explicit no-`src/core` import proof on `scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py`
   - Search pattern: `^(from|import)\s+core(\.|$)|src/core`
   - Result: `PASS` (`No matches found`)
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - Result: `PASS` (`2 passed`)
   - Note: these selectors are unchanged-surface guardrails only; they do not validate the new audit logic directly.
4. Determinism + replay-root immutability proof:
  - reran `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py`
  - `json_before = 5b9b78ec85f691afdae89207311b828ee34ccf489ac8d78fd61926d0cd8f8858`
  - `json_after = 5b9b78ec85f691afdae89207311b828ee34ccf489ac8d78fd61926d0cd8f8858`
  - report hash matched before/after rerun
  - `replay_manifest_before = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
  - `replay_manifest_after = 273f16d3247e71327d15aeecac2ecdbed37238b9133fb7aefe45450a5b59b322`
  - Result: `PASS`
5. `pre-commit run --files docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_packet_2026-04-20.md docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py results/evaluation/scpe_ri_v1_no_trade_axis_ceiling_audit_2026-04-20.json`
  - Result: `PASS`

## Boundary proof

- Runtime is unchanged.
- The canonical replay script `scripts/analyze/scpe_ri_v1_router_replay.py` is unchanged.
- The first revision script `scripts/analyze/scpe_ri_v1_no_trade_release_revision.py` is unchanged.
- The canonical replay root `results/research/scpe_v1_ri/` is treated as frozen input only.
- This slice introduces no new release rule and no new recommendation semantics.
- The audit artifact is observational-only, summary-only, and non-authoritative.

## Gate-component mapping

### Continuation trade floor

- threshold: `>= 10`
- baseline value: `89`
- first revision value: `99`
- baseline status: `satisfied`
- first revision status: `satisfied`
- axis classification: `satisfiable`

Interpretation:

- The bounded no-trade release axis directly influences continuation participation, but this component was already green before the first revision.

### Defensive trade floor

- threshold: `>= 10`
- baseline value: `2`
- first revision value: `2`
- baseline status: `unsatisfied`
- first revision status: `unsatisfied`
- shortfall after first revision: `8`
- axis classification: `unsatisfiable`

Interpretation:

- This is the hard ceiling on the current axis.
- The bounded no-trade release axis only releases `RI_no_trade_policy -> RI_continuation_policy` rows, so it cannot raise defensive trade count and therefore cannot satisfy this gate component on its own.

### Actual policy change rate ceiling

- threshold: `<= 0.25`
- baseline value: `0.2`
- first revision value: `0.268966`
- baseline status: `satisfied`
- first revision status: `unsatisfied`
- max allowed actual policy changes at current row count: `36`
- baseline actual policy changes: `29`
- remaining capacity above baseline: `7`
- first revision changed rows: `10`
- required release reduction to re-enter ceiling: `3`
- axis classification: `satisfiable`

Interpretation:

- Churn is binding, but it is not the hard ceiling.
- On this bounded axis, a smaller subset can plausibly re-enter the change-rate ceiling; that alone still would not solve the separate defensive trade bottleneck.

## Ceiling verdict

- full gate satisfiable on no-trade axis alone: `false`
- classification: `blocked_by_external_gate`
- reason: defensive trade scarcity remains unsatisfiable on the bounded no-trade continuation-release axis even before churn is considered

Interpretation:

- The no-trade release axis still matters, but it is no longer the whole roadmap story.
- Even a perfect churn-trimmed continuation-release subset would leave the defensive gate red on this axis.
- The bounded no-trade axis alone cannot satisfy the full replay-quality gate because the defensive-trade floor remains unsatisfied on the frozen first-revision surface, even before churn becomes binding.

## Roadmap implications

This slice does **not** authorize a new revision rule. It sharpens the roadmap in a different way:

1. A tighter second no-trade revision may still be worthwhile for local quality, but it cannot by itself clear the full replay-quality gate.
2. The next missing bottleneck is now explicit: defensive-policy scarcity must be investigated on its own axis.
3. Any next step beyond this audit is only `föreslagen`, not approved by this slice.

## Residual risks

- This remains observational constraint mapping, not execution evidence.
- The ceiling verdict depends on the frozen baseline and first-revision artifacts; a different future revision family could alter the surrounding landscape.
- This audit explains an axis ceiling; it does not yet explain why defensive-policy trade count is so sparse.

## READY_FOR_REVIEW evidence completeness

All gate outcomes listed here are reported evidence from this session's command runs.

- Mode/risk/path: captured above
- Scope IN/OUT: captured above
- Exact commands and outcomes: captured above
- Evidence paths:
  - `docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_packet_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md`
  - `scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py`
  - `results/evaluation/scpe_ri_v1_no_trade_axis_ceiling_audit_2026-04-20.json`
  - `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/manifest.json`

## Bottom line

The bounded no-trade release axis has a real but limited ceiling: continuation participation is already strong, churn can be trimmed back into range, but defensive trade scarcity remains unsatisfied and invariant on this axis. That means the roadmap should stop pretending that a second no-trade release tweak alone can win the whole replay-quality gate; the next meaningful bottleneck is on the defensive-policy side.
