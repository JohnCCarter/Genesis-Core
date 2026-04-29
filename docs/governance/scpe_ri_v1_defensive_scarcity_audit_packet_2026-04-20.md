# SCPE RI V1 defensive scarcity audit packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Risk: `MED`
Required Path: `Full`
Category: `obs`
Constraint: `NO BEHAVIOR CHANGE`
Objective: explain why defensive-policy trade support stays sparse by decomposing the fate of raw defensive candidates across selection, stability-control, and veto outcomes on the frozen baseline replay surface.
Base SHA: `ef44088f`
Skills used: `python_engineering`

## Commit contract

### Scope IN

- `docs/governance/scpe_ri_v1_defensive_scarcity_audit_packet_2026-04-20.md`
- `docs/governance/scpe_ri_v1_defensive_scarcity_audit_report_2026-04-20.md`
- `scripts/analyze/scpe_ri_v1_defensive_scarcity_audit.py`
- `results/evaluation/scpe_ri_v1_defensive_scarcity_audit_2026-04-20.json`

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
- edits to any prior audit/revision script logic
- any new release rule or defensive rule
- any change to baseline or revision recommendation semantics

### Expected changed files

- packet
- report
- one new audit script
- one new commit-safe JSON artifact

### Max files touched

- 4

## Audit question

The bounded question for this slice is:

- Why do `30` raw defensive targets collapse to only `3` selected defensive rows and `2` defensive trades on the frozen baseline replay surface?

This audit is observational-only and bounded to the frozen baseline replay artifacts plus the unchanged replay script as an analysis reference. It does not introduce a new defensive rule, does not change the current `NEEDS_REVISION` recommendation, and only classifies the observed candidate fates.

This audit is observational only. It reconstructs raw defensive-candidate fates from frozen research artifacts using a research-side analytical mirror of the existing replay behavior; it does not modify or supersede canonical replay logic and does not propose a new defensive rule.

The audit script executes helper definitions from `scripts/analyze/scpe_ri_v1_router_replay.py` via `runpy.run_path` only to reconstruct row-local raw target policy from frozen inputs. It does not regenerate canonical replay artifacts, and the run must fail if the frozen `results/research/scpe_v1_ri/**` replay-root surface changes.

Its purpose is limited to describing how raw defensive candidates currently resolve across selection, stability, and veto stages under the frozen replay reference.

Any follow-up paths are `föreslagen` hypotheses only and are out of scope for this slice.

## Planned audit logic

- load frozen baseline routing trace + replay metrics + manifest
- load frozen Phase C entry rows
- reconstruct raw router targets with the unchanged research-only replay logic
- isolate rows where raw target policy = `RI_defensive_transition_policy`
- classify each raw defensive candidate into mutually exclusive observed fate buckets such as:
  - selected defensive
  - retained continuation via `confidence_below_threshold`
  - retained no-trade via `switch_blocked_by_min_dwell`
  - defensive selected but veto-capped
  - defensive selected but veto-forced no-trade
- summarize raw-candidate counts, fate counts, and supporting bucket structure

## Boundaries

This slice must:

- remain summary-only, observational-only, and non-authoritative
- treat `results/research/scpe_v1_ri/**` as frozen input only
- use the unchanged replay script only as an analysis reference for raw-target reconstruction
- emit one deterministic JSON summary under `results/evaluation/`
- emit one deterministic implementation report without volatile fields
- enforce deterministic outputs: sorted JSON keys, stable bucket ordering, no timestamps, no host/user metadata, and no random inputs

This slice must not:

- modify runtime or canonical replay logic
- alter prior revision artifacts
- claim policy approval, release approval, or deployment readiness
- reinterpret the replay-quality rule itself

## Expected evidence

- exact raw defensive target count
- exact selected defensive row count and defensive trade count
- exact fate decomposition for non-selected defensive candidates
- explicit statement of whether scarcity begins upstream (raw target rarity) or downstream (selection/stability/veto suppression)
- explicit statement that the observed scarcity is scarce defensive selection within the defensive candidate population, not rare raw defensive target generation
- explicit statement that the slice describes observed fates only and does not recommend a new defensive rule
- frozen input hashes and `read_only_inputs_confirmed = true`

## Gates required

- `pre-commit run --files docs/governance/scpe_ri_v1_defensive_scarcity_audit_packet_2026-04-20.md docs/governance/scpe_ri_v1_defensive_scarcity_audit_report_2026-04-20.md scripts/analyze/scpe_ri_v1_defensive_scarcity_audit.py results/evaluation/scpe_ri_v1_defensive_scarcity_audit_2026-04-20.json`
- explicit smoke run of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_defensive_scarcity_audit.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` (unchanged-surface guardrails only; not direct validation of the new audit logic)
- second identical rerun of `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/scpe_ri_v1_defensive_scarcity_audit.py` with stable output-hash proof for both the JSON artifact and the report
- explicit proof that `results/research/scpe_v1_ri/**` remains unchanged before vs after both runs
- explicit proof that `scripts/analyze/scpe_ri_v1_defensive_scarcity_audit.py` does not import from `src/core/**`

## Stop conditions

- scope drift beyond the four scoped files
- any write to `results/research/scpe_v1_ri/**`
- any attempt to introduce a new defensive rule or modify existing replay logic
- any wording that turns the audit into runtime advice or promotion evidence

## Done criteria

- the defensive scarcity audit is implemented and documented
- all listed gates pass
- Opus post-audit confirms the slice is still observational-only and governance-safe
