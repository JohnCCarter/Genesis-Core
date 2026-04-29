# Document taxonomy repo-wide migration packet

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Status: `approved scope / docs-only / no behavior change`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `MED` — why: this slice moves a large historical documentation set across taxonomy zones and updates path anchors repo-wide, but touches no runtime/config/test/code semantics.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the task is a documentation-taxonomy refactor on already tracked evidence/decision history, not runtime integration.
- **Objective:** complete the root-level historical migration out of `docs/governance/` so decision records live in `docs/decisions/`, analysis notes live in `docs/analysis/`, and only true governance-core documents remain in `docs/governance/`.
- **Candidate:** `repo-wide document taxonomy migration`
- **Base SHA:** `9595d876808e173afebd954ecd074ef6ca802731`

### Research-evidence lane

- **Baseline / frozen references:** current tracked root-markdown inventory under `docs/governance/`, excluding governance-core files, existing taxonomy READMEs, and `GENESIS_WORKING_CONTRACT.md`
- **Candidate / comparison surface:** manifest-driven relocation of non-core governance-root markdown files into `docs/decisions/` and `docs/analysis/`
- **Vad ska förbättras:** reduce taxonomy drift between governance policy, decision records, and analysis notes
- **Vad får inte brytas / drifta:** no runtime behavior, no source/config/test semantics, no unrelated local edit in `docs/README.md`, no stale path anchors to moved files
- **Reproducerbar evidens som måste finnas:** explicit source→destination manifest counts, repo-wide moved-path consumer sweep, leftover-reference sweep, relative-link audit, and staged diff review

### Scope

- **Scope IN:**
  - move all non-core root markdown files from `docs/governance/` into `docs/decisions/` or `docs/analysis/`
  - apply exact path-anchor updates across tracked text/documentation surfaces
  - update `GENESIS_WORKING_CONTRACT.md` only at path-anchor level
  - update taxonomy/index docs needed to describe the completed migration state
  - record this repo-wide migration packet
- **Scope OUT:**
  - no changes under `src/**`, `scripts/**`, `tests/**`, or `config/**` except exact text-reference updates in documentation-style files if needed
  - no content rewrites beyond minimal taxonomy/path adjustments
  - no changes in `docs/governance/` subdirectories
  - no modification of `docs/README.md` unless an exact moved-path dependency is found (none expected)
- **Expected changed files:** repo-wide docs/text reference surfaces plus moved files
- **Max files touched:** bounded by the migration manifest and exact path-reference consumers only

### Classification rules

- **Keep in `docs/governance/`:** governance-core docs such as `README.md`, `GENESIS_HYBRID_V1_1.md`, and `concept_evidence_runtime_lane_model_2026-04-23.md`
- **Move to `docs/decisions/`:** packets, precode/authorization/boundary/review/handoff/closeout/disposition records, plus manual overrides whose dominant role is governed decision or bounded execution planning
- **Move to `docs/analysis/`:** evidence, diagnosis, comparison, assessment, report, summary, inventory, memo, and chronology/quality notes, plus manual overrides whose dominant role is synthesis or assessment

### Manual override notes

The inventory includes a small set of title-ambiguous files. They must be classified by dominant role after spot-checking title + opening + conclusion. In the current packet, `champion_provenance_admissible_use` and `governed_rerun` remain decision-class, while `cutover_readiness` and the RI policy-router same-window chronology notes remain analysis-class.

### Gates required

- repo-wide exact-consumer sweep for moved governance-root markdown paths outside permitted text/document surfaces
- destination collision check for the move manifest
- `get_errors` on changed documentation files
- repo-wide leftover-reference sweep for moved old paths after migration
- post-move relative-link audit for `governance/` references in tracked markdown
- `pre-commit` on touched markdown/text files if available
- staged diff review showing:
  - no `docs/README.md` changes
  - `GENESIS_WORKING_CONTRACT.md` is path-only
  - moved-file counts match the manifest

### Stop Conditions

- any moved path is consumed by runtime/code/config/test logic in a way that is not documentation-only
- destination collision in the manifest
- `docs/README.md` contains an exact moved-path dependency that would be left stale without a separate isolation plan
- scope drifts into content rewriting or non-taxonomy cleanups
- any leftover exact moved-path references remain after the migration sweep

### Output required

- implementation report with migration counts and affected zones
- diff summary
- validation outcomes for consumer sweep, leftover sweep, relative-link audit, and `pre-commit`
