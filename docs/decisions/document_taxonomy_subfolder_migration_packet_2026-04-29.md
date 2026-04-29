# Document taxonomy subfolder migration packet

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Status: `approved scope proposed / doc-taxonomy-plus-anchor-updates / no behavior change`

Relevant skill: `repo_clean_refactor`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `MED` — why: this slice introduces durable subfolder taxonomy under `docs/decisions/` and `docs/analysis/`, relocates a large number of tracked docs, and updates exact consumer path anchors in related tracked text/documentation surfaces without touching runtime/config/test semantics.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the work is a documentation-structure refactor on already tracked decision and analysis history, plus exact consumer anchor repairs, not a runtime integration change.
- **Objective:** create durable, domain-driven subfolders under `docs/decisions/` and `docs/analysis/`, move the current root-heavy series into those folders, and preserve navigation with exact consumer path-anchor updates.
- **Candidate:** `docs decisions+analysis subfolder taxonomy migration`
- **Base SHA:** `0914b01588a632880c79196e05ef24684d6ca85c`
- **Operational reclassification rule:** if the consumer sweep finds any operational dependency outside tracked text/documentation references, stop and reclassify before editing.

### Research-evidence lane

- **Baseline / frozen references:** current root-heavy inventories under `docs/decisions/` and `docs/analysis/`, plus the existing zone README files.
- **Candidate / comparison surface:** family-driven relocation into durable subfolders such as `regime_intelligence/**`, `feature_attribution/**`, `scpe_ri_v1/**`, `diagnostics/**`, and `recommendations/**`.
- **Vad ska förbättras:** reduce root clutter, increase navigability by series/domain, and align both folders with the repository layout policy's preference for coarse, understandable taxonomy.
- **Vad får inte brytas / drifta:** no runtime behavior, no source/config/test semantics, no unrelated local edit in `docs/README.md`, no stale path anchors to moved files, and no loss of chronology inside document families.
- **Reproducerbar evidens som måste finnas:** explicit move-manifest rules, destination-collision check, exact-path consumer sweep, leftover-reference audit, relative-link audit, `get_errors`, and pre-commit success.

This slice is limited to one-to-one docs moves, README taxonomy updates, and exact repo-path anchor replacements in related tracked text/documentation consumers. If the consumer sweep finds any operational dependency outside tracked text/documentation references, stop and reclassify before editing.

### Scope

- **Scope IN:**
  - create agreed subfolders under `docs/decisions/` and `docs/analysis/`
  - move tracked files from the two roots into those subfolders according to durable family rules
  - apply exact path-anchor updates across tracked text/documentation surfaces
  - update `GENESIS_WORKING_CONTRACT.md` only at path-anchor level if affected
  - update `docs/decisions/README.md` and `docs/analysis/README.md` to describe the new subfolder taxonomy
  - record this migration packet
- **Scope OUT:**
  - no runtime, source, config, or test logic changes
  - no content rewrites beyond minimal taxonomy/path adjustments
  - no modification of `docs/README.md` unless an exact moved-path dependency is detected
  - no movement of files out of `docs/decisions/` or `docs/analysis/` into other top-level zones
  - no opportunistic cleanup of unrelated documentation
- **Expected changed files:** move-set files plus exact path-reference consumers and the affected README files
- **Max files touched:** bounded by the explicit family-based move manifest and exact path-reference consumers only

### Planned durable subfolders

#### Under `docs/decisions/`

- `regime_intelligence/optuna/challenger_family/`
- `regime_intelligence/optuna/decision/`
- `regime_intelligence/optuna/signal/`
- `regime_intelligence/advisory_environment_fit/`
- `regime_intelligence/policy_router/`
- `regime_intelligence/router_replay/`
- `regime_intelligence/p1_off_parity/`
- `regime_intelligence/experiment_map/`
- `regime_intelligence/upstream_candidate_authority/`
- `regime_intelligence/core/`
- `feature_attribution/v1/`
- `feature_attribution/post_phase14/`
- `scpe_ri_v1/`
- `volatility_policy/`
- `diagnostic_campaigns/`
- `research_findings/`

Root exceptions expected to stay in `docs/decisions/`:

- `README.md`
- `document_taxonomy_*.md`

#### Under `docs/analysis/`

- `regime_intelligence/advisory_environment_fit/`
- `regime_intelligence/policy_router/`
- `regime_intelligence/core/`
- `regime_intelligence/optuna/challenger_family/`
- `regime_intelligence/role_map/`
- `regime_intelligence/router_replay/`
- `regime_intelligence/upstream_candidate_authority/`
- `scpe_ri_v1/`
- `diagnostics/`
- `recommendations/`

Root exceptions expected to stay in `docs/analysis/`:

- `README.md`

### Classification rules

- Use domain/family first, not document subtype.
- Keep entire chronology-linked families together even when filenames mix `packet`, `summary`, `assessment`, `report`, or `diagnosis` semantics.
- Prefer coarse stable buckets over micro-folders.
- `core/` is reserved for corpus-level material that does not belong to a narrower stream such as `policy_router`, `router_replay`, or `optuna`; it is not a general overflow bucket.
- `research_findings/` stores decision-level synthesized findings only; raw evidence and generated outputs belong elsewhere.
- Leave root only for README and a very small number of explicit taxonomy/meta records.

### Gates required

- exact moved-path consumer sweep under `src/`, `scripts/`, `tests/`, and `config/`
- destination collision check for the move manifest
- exact moved-path dependency check for `docs/README.md`
- repo-wide leftover-reference sweep for moved old paths after migration
- relative-link audit after migration
- `git diff --check`
- `get_errors` on manually edited packet/README/working-contract files
- `pre-commit` on the changed existing files (excluding `docs/README.md` if still out of scope)
- staged diff review showing moved-file counts and a clean commit boundary

### Stop Conditions

- any moved path is consumed by runtime/code/config/test logic in a non-documentation role
- destination collisions in the manifest
- `docs/README.md` contains moved exact-path dependencies that would remain stale without separate isolation
- scope drifts into content rewriting or unrelated docs cleanup
- any leftover exact moved-path references remain after the migration sweep

`docs/README.md` remains out of scope unless an exact moved-path dependency is detected. If such a dependency exists, only the exact affected path anchors may be updated; unrelated local edits must remain excluded from the commit.

### Output required

- implementation report with subfolder counts and family mapping
- diff summary
- validation outcomes for consumer sweep, leftover sweep, relative-link audit, `get_errors`, and pre-commit
