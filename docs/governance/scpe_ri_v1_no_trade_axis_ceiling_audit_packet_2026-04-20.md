# SCPE RI V1 no-trade axis ceiling audit packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Required Path: `Full`
Category: `obs`
Constraint: `NO BEHAVIOR CHANGE`
Objective: determine whether the bounded no-trade release axis can satisfy individual replay-quality gate components on its own, or whether a separate bottleneck already makes that impossible even after the first counterfactual revision.
Base SHA: `a54e07dc`
Skills used: `python_engineering`

## Commit contract

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

### Expected changed files

- packet
- report
- one new audit script
- one new commit-safe JSON artifact

### Max files touched

- 4

## Audit question

This slice asks a narrower roadmap question than the first revision report:

- If we stay on the bounded no-trade release axis only — meaning row-local, non-propagating `RI_no_trade_policy -> RI_continuation_policy` counterfactual releases — can that axis ever clear the replay-quality gate by itself?

This audit is observational-only and evaluates whether the frozen no-trade release axis can satisfy individual replay-quality gate components under unchanged baseline and first-revision inputs.

It does not authorize a new revision rule, does not change the current `NEEDS_REVISION` recommendation, and classifies each gate component only as `satisfiable`, `unsatisfiable`, or `unresolved` on this bounded axis alone.

This audit is observational-only and bounded to the frozen baseline and first-revision artifacts. It does not introduce or recommend a new release rule, does not alter baseline or revision recommendation semantics, and only assesses whether the existing replay-quality gate can be satisfied on the no-trade axis alone.

Any follow-up paths are `föreslagen` hypotheses only and are out of scope for this slice.

## Method boundary

This is a summary-only, observational-only, non-authoritative audit. It must:

- read the frozen baseline replay metrics from `results/research/scpe_v1_ri/replay_metrics.json`
- read the frozen first revision artifact from `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`
- decompose the replay-quality gate into its component requirements
- report which requirements remain satisfiable vs impossible on the bounded no-trade axis
- write one commit-safe JSON summary under `results/evaluation/`
- write one deterministic implementation report without volatile fields

This slice must not:

- alter runtime, canonical replay, or prior revision artifacts
- introduce a new revision rule
- claim runtime readiness, promotion evidence, or deployment approval
- reinterpret the replay-quality rule itself

## Planned audit logic

- extract baseline and revised values for:
  - continuation-policy trade count
  - defensive-policy trade count
  - actual policy change rate
- record frozen input references and SHA256 hashes for:
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/evaluation/scpe_ri_v1_no_trade_release_revision_2026-04-20.json`
- evaluate the replay-quality gate as three explicit subconditions:
  - continuation trade floor
  - defensive trade floor
  - change-rate ceiling
- determine whether the bounded no-trade axis can influence each subcondition
- emit an axis-ceiling verdict with explicit reasoning, including any invariant bottleneck detected outside the no-trade continuation-release axis

## Expected evidence

- explicit gate decomposition for baseline and first revision
- explicit statement of which gate(s) remain impossible on the no-trade axis alone
- explicit defensive trade shortfall, if present
- explicit note that this is roadmap-shaping evidence only
- explicit input-hash evidence and `read_only_inputs_confirmed = true`

## Gates required

- `pre-commit run --files docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_packet_2026-04-20.md docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py results/evaluation/scpe_ri_v1_no_trade_axis_ceiling_audit_2026-04-20.json`
- explicit smoke run of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` (unchanged-surface guardrails only; not direct validation of the new audit logic)
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py` with stable output-hash proof for both the JSON artifact and the report
- explicit proof that `results/research/scpe_v1_ri/**` remains unchanged before vs after both runs
- explicit proof that `scripts/analyze/scpe_ri_v1_no_trade_axis_ceiling_audit.py` does not import from `src/core/**`

## Stop conditions

- scope drift beyond the four scoped files
- any write to `results/research/scpe_v1_ri/**`
- any attempt to introduce a new revision rule or modify a previous one
- any wording that turns the ceiling audit into a runtime or promotion claim

## Done criteria

- the ceiling audit is implemented and documented
- all listed gates pass
- Opus post-audit confirms the slice is still observational-only and roadmap-shaping only
