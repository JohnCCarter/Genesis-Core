# Year worker execution chain design

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `proposed / non-authoritative / manual-draft`
Scope: `docs-only`
Runtime authority: `none`
Dispatch authority: `none`
Promotion authority: `none`
Skill Usage: no suitable repository skill identified for this docs-only workforce chain-design slice.

This document describes a **proposed** end-to-end year-worker chain for discussion and manual drafting. It does **not** describe a materialized execution path.

This design block is a proposed manual draft for the research-evidence lane only. It is non-authoritative and is **not consumed by runtime, dispatch, validation, promotion, or shared-truth workflows**.

## Command packet

- **Mode:** `RESEARCH` — source: branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW` — why: docs-only chain design that unifies existing workforce draft blocks without touching runtime, config truth, scripts, tests, or results.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the repository already contains separate dependency-closure and runtime-manifest draft blocks, so the next safe step is to connect them into one descriptive lifecycle without implementing automation.
- **Objective:** define one coherent proposed year-worker lifecycle from queue admission to integration and cross-year synthesis.
- **Candidate:** `cloud workforce year-worker end-to-end chain`
- **Base SHA:** `044096e70ea5596181392e77217dab275d603e93`

### Research-evidence lane

- **Baseline / frozen references:** `workforce_roadmap.md`, `docs/governance/worker_governance_envelope.md`, dependency-closure canonical drafts under `docs/contracts/workforce/`, `worker_runtime_execution_manifest_canonical_draft_v1_2026-05-07.yaml`, and `worker_runtime_execution_manifest_example_year_worker_2026-05-07.yaml`
- **Candidate / comparison surface:** current separated workforce draft blocks versus one proposed end-to-end lifecycle description
- **Vad ska förbättras:** make the year-worker chain understandable as one lineage from slice queue to cross-year synthesis
- **Vad får inte brytas / drifta:** no runtime authority, no config mutation, no worker tuning, no inferred missing inputs, no worker global conclusions, no shared-truth writes
- **Reproducerbar evidens som måste finnas:** scoped diagnostics, markdown/YAML validation, scoped `pre-commit`, and post-authoring authority-wording audit

## Scope

- **Scope IN:**
  - `docs/contracts/workforce/year_worker_execution_chain_design_2026-05-07.md`
  - `docs/contracts/workforce/year_worker_slice_queue_canonical_draft_v1_2026-05-07.yaml`
  - `docs/contracts/workforce/year_worker_output_contract_canonical_draft_v1_2026-05-07.yaml`
  - `docs/contracts/workforce/year_worker_integration_queue_canonical_draft_v1_2026-05-07.yaml`
  - `docs/contracts/workforce/fail_closed_runtime_matrix_2026-05-07.md`
- **Scope OUT:**
  - runtime code
  - backtest engine code
  - strategy code
  - optimizer code
  - config truth
  - champion configs
  - scripts
  - tests
  - data
  - `results/backtests/**`
  - `.gitignore`
  - shared truth / promotion docs
  - making any existing draft authoritative
- **Expected changed files:** `5`
- **Max files touched:** `5`

## Relationship to existing workforce drafts

This design intentionally **reuses** rather than replaces the existing draft building blocks:

- dependency closure answers whether the worker has a complete declared input set
- repo snapshot answers which required inputs are satisfiable by a clean clone
- runtime execution manifest answers how one year-worker run would execute once admission is satisfied
- generated year overlay answers what year-local execution metadata may vary without changing strategy truth
- worker output contract answers what the worker may return
- integration queue answers how intake and later cross-year comparison are staged

None of those drafts become authoritative merely because this chain document references them.

## 1. End-to-end lifecycle

The proposed year-worker lifecycle is:

1. **slice candidate discovered**
   - control plane or scheduler identifies one bounded year slice
   - the slice enters the queue as a candidate only
2. **slice admissibility evaluated**
   - control plane checks boundedness, ownership, scope, and whether the slice is worth opening
   - inadmissible slices stop here
3. **worker envelope compiled**
   - governance compiler narrows the worker contract
   - scope, forbidden surfaces, allowed inputs, artifact contract, and validation commands are pinned
4. **dependency manifest compiled**
   - every required repo file, artifact, and operational state dependency is declared
5. **repo snapshot manifest compiled**
   - the clean-clone-satisfiable repo subset is pinned separately from missing or excluded dependencies
6. **runtime execution manifest compiled**
   - baseline config ref, runtime window, command template, provenance, expected artifacts, and drift rules are pinned
7. **generated year overlay compiled**
   - a deterministic, ephemeral, metadata-only overlay is derived from verified declared inputs
8. **dispatch allowed evaluated**
   - dispatch remains blocked unless admissibility, dependency closure, repo snapshot, runtime manifest, overlay, and hash requirements all pass
9. **cloud worker starts in clean clone**
   - worker begins from the pinned branch/base SHA only
10. **worker validates pins, manifests, hashes, and declared inputs**
    - fail-closed startup preflight runs before execution
11. **worker executes only the declared command**
    - no parameter search, no alternate command, no local discovery
12. **worker writes only the declared artifact namespace**
    - any timestamped runtime outputs must be captured or mapped back into the declared namespace
13. **worker runs scoped validation**
    - artifact, provenance, scope-adherence, and schema checks run after execution
14. **worker returns output contract**
    - status, artifacts, observed/inferred/unverified separation, limitations, and scope adherence are returned
15. **integration plane validates and queues the result**
    - intake verifies hashes, namespace, provenance, and authority language before classification
16. **cross-year synthesis compares outputs**
    - only integration plane may compare years and emit recurring or contradictory interpretations

### Lifecycle ownership map

| Lifecycle step       | Owning plane              | Primary artifact                     | Fail-closed rule                             |
| -------------------- | ------------------------- | ------------------------------------ | -------------------------------------------- |
| Slice discovery      | Control plane             | queue item candidate                 | candidate does not imply admissibility       |
| Admissibility        | Control plane             | queue item state                     | boundedness failure blocks progress          |
| Envelope compile     | Governance compiler       | worker envelope                      | envelope may only narrow                     |
| Dependency closure   | Control plane             | dependency manifest + missing report | missing input blocks dispatch                |
| Repo visibility      | Control plane             | repo snapshot manifest               | local-only input is not cloud-visible        |
| Runtime binding      | Control plane             | runtime execution manifest           | runtime contract gaps block dispatch         |
| Overlay generation   | Compiler / packaging step | generated year overlay               | missing or forbidden fields block generation |
| Execution            | Worker plane              | declared command + artifacts         | execute declared command only                |
| Validation           | Worker plane              | validation report                    | any failed check blocks intake               |
| Intake               | Integration plane         | integration queue entry              | mismatched hashes or claims block intake     |
| Cross-year synthesis | Integration plane         | synthesis note / queue decision      | workers may not emit global meaning          |

## 2. Slice queue model

The queue model is defined in `year_worker_slice_queue_canonical_draft_v1_2026-05-07.yaml`.

### Queue semantics

Each queue item represents one **candidate or admitted year slice**, not a live authority surface.

Required fields in the queue item are:

- `slice_id`
- `lane`
- `family`
- `year`
- `symbol`
- `timeframe`
- `question`
- `base_sha`
- `baseline_config_ref`
- `required_artifact_refs`
- `priority`
- `status`
- `blocking_reason`
- `generated_from`
- `admissibility_state`

### Queue rules

- queue presence does **not** imply dispatch readiness
- `baseline_config_ref` becomes immutable within a wave once admissibility is granted
- `required_artifact_refs` must be explicit; workers may not discover missing dependencies ad hoc
- `generated_from` records lineage only; it does not inherit authority from upstream analysis or notes
- queue `status` is bookkeeping, not runtime authority

## 3. Year-worker envelope extension

The existing worker envelope should be extended by reference, not by authority escalation.

### Proposed additional envelope references

| Envelope extension field         | Purpose                                                 | Fail-closed behavior                    |
| -------------------------------- | ------------------------------------------------------- | --------------------------------------- |
| `dependency_manifest_ref`        | points to the declared dependency closure for the slice | missing ref blocks preflight            |
| `repo_snapshot_manifest_ref`     | points to the clean-clone-satisfiable repo subset       | missing ref blocks cloud admission      |
| `runtime_execution_manifest_ref` | points to the exact runtime binding for the year run    | missing ref blocks execution            |
| `generated_overlay_ref`          | points to the verified year-local overlay artifact      | missing or unhashed ref blocks dispatch |
| `output_contract_schema_ref`     | points to the schema the worker must return             | missing ref blocks intake validation    |
| `artifact_namespace`             | pins the worker-owned output root                       | ambiguous root blocks execution         |
| `validation_commands`            | structured list of required validation checks           | absent list blocks admissible execution |

### Envelope extension rule

The envelope remains the **top-level worker-facing contract**. The additional references do not supersede it; they simply make the execution chain explicit enough that the worker does not have to reconstruct the chain from several documents.

## 4. Runtime execution manifest relationship

The runtime execution manifest sits in the middle of the chain and binds together the surrounding workforce objects.

| Related object           | Relationship to runtime execution manifest                                                          |
| ------------------------ | --------------------------------------------------------------------------------------------------- |
| `dependency_manifest`    | proves which required inputs must exist before runtime binding is admissible                        |
| `repo_snapshot_manifest` | proves which declared inputs a clean clone can satisfy directly                                     |
| `generated year overlay` | supplies the year-local, non-strategy execution metadata consumed by the runtime binding            |
| `worker envelope`        | points to the runtime execution manifest and constrains the worker's permitted use of it            |
| `output contract`        | reports what actually happened under the runtime execution manifest                                 |
| `integration queue`      | verifies that the returned output still matches the runtime execution manifest hashes and namespace |

### Important relationship clarification

The current runtime execution manifest draft uses a safe interim `complete_merged_config_carrier` posture. This end-to-end design does **not** make that draft authoritative, but it clarifies the intended decomposition:

- `baseline_config_ref` carries the immutable strategy/config identity
- `generated year overlay` carries metadata-only year execution variance
- an ephemeral derived execution carrier may be materialized from those two layers when the chain is eventually operationalized

That clarification is descriptive only. It does not change the current draft's status or implement a new runtime path.

## 5. Generated year overlay policy

The generated year overlay is an **ephemeral derived artifact** created only from explicitly declared, verified inputs. Missing, mismatched, or undeclared inputs block generation and keep dispatch disallowed.

### Allowed overlay keys

In this end-to-end design, the overlay may carry only metadata needed to bind one year-run without changing strategy identity:

- `overlay_schema_version`
- `slice_id`
- `dispatch_id`
- `run_id`
- `year`
- `runtime_window.start`
- `runtime_window.end`
- `runtime_window.warmup_bars`
- `runtime_window.data_source_policy` **only if explicitly allowed by the runtime execution manifest and envelope**
- `artifact_namespace.namespace_root`
- `artifact_namespace.run_id`
- `artifact_namespace.year`
- `artifact_namespace.lane`
- `artifact_namespace.base_sha_short`
- `artifact_namespace.manifest_hash_short`
- `execution_metadata.validation_profile`
- `execution_metadata.output_contract_schema_version`
- `execution_metadata.resume_mode`
- other explicitly non-strategy execution metadata that does not alter economic logic

### Forbidden overlay keys

The overlay must not contain:

- strategy threshold changes
- optimizer or search-space changes
- feature-family activation changes unless separately authorized
- champion config mutations
- runtime authority changes
- promotion or readiness fields
- `merged_config`
- `cfg`
- `thresholds/**`
- `gates/**`
- `risk/**`
- `exit/**`
- `multi_timeframe/**`
- `features/**`
- `intelligence/**`
- `optimizer/**`
- `search_space/**`
- anything that changes economic logic for the year run

### Overlay rule

If the overlay contains any forbidden key, dispatch remains blocked and the slice is classified as tuning or authority drift rather than admissible year execution.

## 6. Anti-tuning and anti-drift rules

The year-worker chain prevents drift through a layered fence:

1. all workers in the same wave must use the same `baseline_config_ref` and baseline hash
2. overlays must pass a strict field whitelist
3. the merged effective config must be hashed as a design requirement
4. any unexpected config diff must fail closed
5. workers may not edit `config/**`
6. workers may not select parameters based on year result
7. workers may not retry with altered thresholds after seeing outcome
8. workers may only execute the declared command template

### Hash rule caveat

`merged_effective_config_hash` is a required **design target**, but it must not be treated as already standardized until a deterministic canonical serialization rule is explicitly bound. Until then, any workflow that depends on that hash for honest comparability remains blocked or draft-only.

## 7. Artifact namespace contract

Each year-worker run must own one deterministic namespace root.

### Proposed run identifier format

`run_id = {year}__{symbol}__{timeframe}__{lane}__{slice_id}__{base_sha_short}__{manifest_hash_short}`

Where:

- `base_sha_short` = first 12 characters of the pinned `base_sha`
- `manifest_hash_short` = first 12 characters of the `runtime_execution_manifest_hash` until a reviewed bundle-hash scheme exists

### Proposed namespace root

`results/workforce/year_workers/{year}/{symbol}/{timeframe}/{lane}/{slice_id}/{run_id}/`

### Required artifact paths inside the namespace

| Artifact role                       | Proposed path                                 |
| ----------------------------------- | --------------------------------------------- |
| backtest summary                    | `{namespace_root}backtest_summary.json`       |
| trade ledger                        | `{namespace_root}trade_ledger.csv`            |
| decision rows                       | `{namespace_root}decision_rows.ndjson`        |
| intelligence shadow (if applicable) | `{namespace_root}intelligence_shadow.ndjson`  |
| merged_config                       | `{namespace_root}merged_config.json`          |
| config_provenance                   | `{namespace_root}config_provenance.json`      |
| runtime_environment                 | `{namespace_root}runtime_environment.json`    |
| validation_report                   | `{namespace_root}validation_report.json`      |
| worker_output_contract              | `{namespace_root}worker_output_contract.yaml` |

### Timestamped runtime-output caveat

Current runtime behavior may still emit timestamped files under `results/backtests/` and `results/trades/`. In this chain design, those outputs are only admissible if the worker captures or maps them back into the declared namespace and reports the mapping in the worker output contract.

## 8. Worker preflight

Worker startup must fail closed unless all of the following pass:

- clean clone state confirmed
- branch matches the declared worker branch or dispatch branch policy
- `base_sha` matches the pinned value
- `envelope_hash` matches the declared worker envelope
- dependency manifest hash matches
- repo snapshot manifest hash matches
- runtime execution manifest hash matches
- overlay hash matches
- baseline config hash matches
- required artifacts exist where declared
- no undeclared local inputs are required
- output namespace is empty or explicitly resumable
- declared command template is present
- validation commands are present

### Preflight rule

A worker may not partially continue after a failed preflight check. The correct behavior is `blocked` or `fail-closed`, not best-effort execution.

## 9. Execution rules

Worker runtime rules are:

- execute exactly one declared run command unless the envelope explicitly allows more
- no parameter search
- no interactive decisions
- no config mutation
- no ad hoc file discovery
- no fallback to local cache unless declared
- no changing year window
- no changing data source policy
- no undeclared outputs
- fail-closed on unexpected missing data

### Command rule

The worker may only execute the declared command template. A worker may not swap in a similar command, add undeclared flags, remove pinned flags, or reinterpret the runtime execution manifest after seeing preflight results.

## 10. Scoped validation

After execution, the worker must run scoped validation covering:

- artifact existence
- YAML/JSON parse checks for produced structured outputs
- merged-config provenance check
- expected year-window check
- no forbidden path touched
- no unexpected config diff
- deterministic smoke if the slice explicitly requires it
- output contract completeness
- secret scan if generated files are committed

### Validation command policy

`validation_commands` in the worker envelope should be a structured, explicit list of checks such as:

- `verify_artifact_namespace`
- `verify_required_artifacts_present`
- `verify_provenance_fields`
- `verify_runtime_window`
- `verify_no_forbidden_write`
- `verify_output_contract_schema`
- `secret_scan_if_commit_planned`

Those command names are descriptive placeholders only. This document does not implement them.

## 11. Worker output contract

The worker output contract is defined in `year_worker_output_contract_canonical_draft_v1_2026-05-07.yaml`.

### Output contract rules

A year-worker must return at least:

- `status`
- `year`
- `symbol`
- `timeframe`
- `slice_id`
- `base_sha`
- manifest hashes
- artifacts produced
- `observed`
- `inferred`
- `unverified`
- `limitations`
- `missing_dependencies`
- `what_this_year_does_not_prove`
- `recommended_integration_class`
- `scope_adherence_report`

### Inference rule

`inferred` is fail-closed reporting only. It must never backfill a missing required input, missing provenance, or global claim. In an admissible success case it should normally be empty or minimal, with larger interpretation deferred to integration plane.

## 12. Integration queue

The intake and classification surface is defined in `year_worker_integration_queue_canonical_draft_v1_2026-05-07.yaml`.

### Intake verification requirements

Integration must verify:

- `base_sha` match
- manifest hash match
- artifact namespace match
- no forbidden write
- no missing provenance
- no undeclared inputs
- no global claims by the worker
- no promotion or readiness language

### Integration classifications

After intake verification, integration plane alone may classify a returned year-worker output as:

- `ignore`
- `park`
- `blocked`
- `rerun_required`
- `deep_dive_required`
- `integrate_candidate`

That classification is an intake disposition owned by integration plane alone. A worker output may recommend a class, but it may not assign larger meaning, cross-year truth, or runtime action.

## 13. Cross-year synthesis

Only integration plane may compare year-level outputs and emit cross-year interpretation.

### Cross-year synthesis classes

The synthesis layer may classify a year result as:

- `local_only_effect`
- `recurring_effect`
- `regime_dependent_effect`
- `blocked_year`
- `null_year`
- `contradictory_year`
- `insufficient_evidence_year`
- `candidate_recurring_pattern`

### Cross-year admission prerequisites

A year output must not enter cross-year synthesis unless integration plane can verify that at least the following tuple is comparable or explicitly review-waived:

- family
- symbol
- timeframe
- baseline config hash
- runtime execution manifest profile
- lane
- command template identity

This is the key separation line: a worker may return one year; only integration plane may decide what several years mean together.

## 14. Fail-closed matrix

The summary matrix for common failure cases is defined in `fail_closed_runtime_matrix_2026-05-07.md`.

The matrix exists to make one rule operationally obvious:

> when required inputs, hashes, provenance, or scope guarantees break, the system blocks or fails closed before it upgrades meaning.

## 15. MVP rollout plan

### Phase 1 — manual end-to-end design

- deliver the full chain design and supporting draft schemas
- no automation
- no live dispatch implementation

### Phase 2 — one blocked year-worker dry-run manifest

- use existing dependency-closure and runtime-manifest drafts
- keep `dispatch_allowed: false`
- verify the chain can be described coherently without authority drift

### Phase 3 — one clean-clone simulation without executing full backtest

- simulate preflight and intake using pinned docs/manifests only
- no real year runtime yet

### Phase 4 — one actual year-worker runtime dry-run

- execute one declared command with one declared artifact namespace
- require full preflight and scoped validation
- still no automation claims beyond the bounded dry-run

### Phase 5 — two-year parallel comparison

- compare two years with identical baseline/runtime profile
- test cross-year intake and synthesis boundaries

### Phase 6 — small wave of 3–5 years

- run a small bounded batch
- check queue pressure, artifact naming, intake workload, and contradiction handling

### Phase 7 — integration queue and cross-year synthesis draft refinement

- refine classification vocabulary and comparable-tuples using evidence from the bounded wave
- still keep shared-truth promotion separate from worker execution

## 16. Deliverables

This design block consists of:

- `year_worker_execution_chain_design_2026-05-07.md`
  - the complete proposed end-to-end chain
- `year_worker_slice_queue_canonical_draft_v1_2026-05-07.yaml`
  - queue-item draft schema for year slices
- `year_worker_output_contract_canonical_draft_v1_2026-05-07.yaml`
  - worker return-shape draft schema
- `year_worker_integration_queue_canonical_draft_v1_2026-05-07.yaml`
  - integration-plane intake and classification draft schema
- `fail_closed_runtime_matrix_2026-05-07.md`
  - quick-reference failure matrix for blocked/fail-closed handling

## What this design does not prove

This design does **not** prove:

- that the chain exists end to end today
- that current runtime outputs already fit the deterministic namespace contract without a capture step
- that generated overlay materialization is automated
- that merged effective config hashing is already canonically bound
- that any current year-worker should receive a positive dispatch authorization flag
- that workers may produce cross-year truth, promotion language, or shared-truth writes

## Recommended next step

Use this chain design together with the existing dependency-closure and runtime-manifest drafts to author one single blocked year-worker packet bundle that references queue item, envelope, dependency closure, runtime binding, output contract, and integration intake in one traceable lineage.
