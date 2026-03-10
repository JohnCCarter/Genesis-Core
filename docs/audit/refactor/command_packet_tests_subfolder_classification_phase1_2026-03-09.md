# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch:feature/tests-subfolder-classification`)
- **Risk:** `MED` — why: upcoming test-file relocation is path-sensitive (CI/docs/scripts refs); this phase is planning-only.
- **Required Path:** `Full`
- **Objective:** Start sensitive test-suite restructuring safely by producing a classification + migration plan before any file moves.
- **Candidate:** Inventory and classify tests into stable/integration/experiments/temporary buckets and propose deterministic move phases.
- **Base SHA:** `d0aee005`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_phase1_2026-03-09.md`
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
- **Scope OUT:**
  - `tests/**` (no moves/renames in phase 1)
  - `.github/workflows/**` (no CI edits in phase 1)
  - runtime/source code paths (`src/**`, `mcp_server/**`, `scripts/**`)
- **Expected changed files:** 2
- **Max files touched:** 2

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q` (informational branch baseline; no code changes expected)
- RESEARCH invariants (explicit):
  - determinism replay selector
  - pipeline invariant/hash guard selector
  - feature cache invariance selector (recommended for this path-sensitive migration)

### Stop Conditions

- Any file move/rename attempted in phase 1
- Scope drift outside planning docs
- Missing evidence for path-sensitive references

### Output required

- **Implementation Report**
- **Phase-2 migration checklist with rollback steps**

### Phase-1 artifacts

- `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
  - inventory, candidate classification, path-sensitive refs, phased migration + rollback.

### Verification evidence (phase 1)

- `python -m pre_commit run --all-files` → **PASS**
- `python -m ruff check .` → **PASS**
- determinism replay selectors → **PASS** (`5 passed`)
- feature cache invariance selectors → **PASS** (`9 passed`)
- pipeline invariant/hash guard selectors → **PASS** (`4 passed`)
- baseline `python -m pytest -q` → **PASS** (`996 passed`)
- transient artifact handling: removed `scripts/build/__pycache__/` after runs.

Validation for Phase 1 includes smoke-equivalent selector coverage (determinism,
feature-cache invariance, pipeline invariant/hash guard) and full baseline
`pytest -q`. No runtime code paths were modified.
