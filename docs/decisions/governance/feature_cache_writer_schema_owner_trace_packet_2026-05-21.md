# Feature-cache writer/schema-owner trace packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `writer-trace-recorded / docs-only / non-authorizing`

This packet records the next bounded `#12` follow-up requested after the Wave 3 `#2 + #12` reframe. It grants no runtime, backtest, optimizer, training, cache-policy, schema-enforcement, CI, launch, paper/live, or promotion authority. It must not be read as approval to start `src/**`, `tests/**`, `scripts/**`, or workflow changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/*`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only, but it sits adjacent to determinism/cache language where a missing writer/schema-owner could easily be over-retold as a ready code fix
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice traces the current writer/schema-owner surface for `#12`; it does not implement or authorize enforcement
- **Skill usage:** `none required` — bounded writer/schema-owner trace slice; no repo-local skill matched this work
- **Objective:** determine whether the current tracked repo still contains a live writer/schema-owner for the `#12` read-side feature-artifact seam, and record the smallest honest next move if it does not
- **Candidate line:** `#12 writer/schema-owner trace`
- **Base SHA:** `c7971624`

### Scope

- **Scope IN:** this packet; one small live-note refinement in `handoff.md`; explicit observed/inferred/unverified framing; exact current tracked reader/writer/schema-owner findings for `data/**/features`
- **Scope OUT:** all edits under `src/**`, `tests/**`, `scripts/**`, `config/**`, `results/**`, and `artifacts/**`; all runtime/cache/schema changes; all CI/workflow activation; all direct docs corrections in `docs/features/**`, `scripts/docs/**`, or `data/**` beyond naming them as future truthfulness candidates; all claims that `#12` now has an implementation-ready carrier
- **Expected changed files:** `docs/decisions/governance/feature_cache_writer_schema_owner_trace_packet_2026-05-21.md`, `handoff.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual path audit for every referenced reader/writer/doc path
- manual wording audit that `observed`, `inferred`, and `unverified` remain distinct
- manual wording audit that this slice does not silently upgrade `#12` into a runtime/cache implementation lane
- self-review for hidden behavior impact

### Stop Conditions

- any wording that claims a live current tracked writer/schema-owner was found when the repo search only found docs/tests references
- any wording that treats `scripts/precompute_features_v17.py` as present on this branch
- any wording that reintroduces `schema_version=1` as a grounded current contract without a tracked owner
- any wording that bundles `#12` back into implementation work with `#2`

## Purpose

This packet answers one narrow question only:

- does the current tracked branch still ground a writer/schema-owner for the `#12` feature-artifact seam?

## What changed in this slice

- one new packet records the current tracked writer/schema-owner trace for `#12`
- `handoff.md` gets a small live-note refinement so the next agent does not reopen `#12` as a hypothetical code fix before the docs-truthfulness question is settled

## What did not change

- no runtime/backtest/training/cache behavior changed
- no feature-artifact writer was introduced
- no schema-version authority was introduced
- no existing feature-artifact docs outside this packet and `handoff.md` were corrected in this slice

## Governing basis

### Observed

1. `src/core/utils/data_loader.py::load_features(...)` is still the current tracked read-side loader for feature artifacts under:
   - `data/curated/v1/features`
   - `data/archive/features`
   - `data/features`
     and it currently tries versioned suffixes `v18`, `v17`, `v16`, then unsuffixed files.
2. `scripts/train/train_model.py::load_features_and_prices(...)` is still the current tracked training-side consumer that calls `load_features(...)`.
3. `tests/utils/test_train_model.py` writes synthetic feature `.parquet` files only inside test setup; those writes are test fixtures, not a current repo production writer/schema-owner for `data/**/features`.
4. `tests/utils/test_feature_parity.py` reads `tests/data/tBTCUSD_1h_features_v17.parquet`, which is a repo fixture snapshot used for parity proof, not a current writer path.
5. Repo-wide file search on the current branch did **not** locate a current tracked `scripts/precompute_features_v17.py` or `scripts/precompute_features_v18.py` file.
6. `docs/features/FEATURE_COMPUTATION_MODES.md` and `scripts/docs/DATA_FETCH_GUIDE.md` still reference `scripts/precompute_features_v17.py` as if it were a current callable producer.
7. Repo-wide search for feature-artifact writes (`to_feather(...)`, feature-targeted `to_parquet(...)`, `curated/v1/features`, `data/features`) did **not** locate a current non-test writer under present `src/**` or `scripts/**` that writes the read-side feature artifacts named by `#12`.
8. Repo-wide search for `schema_version=1` or equivalent current owner text found the claim only in governance/baseline documentation; it did **not** locate a current tracked code/config/data contract owner for a live read-side feature-artifact `schema_version=1`.
9. `data/DATA_FORMAT.md` still describes:
   - curated feature directories under `data/curated/v1/features`
   - historical features under `data/archive/features`
   - `.json` metadata next to feature files
     but this trace did not locate a current tracked writer/schema-owner that produces or governs those outputs.

### Inferred

- The current tracked repo still grounds a **training/read-side feature-artifact reader**, but it does **not** currently ground a live writer/schema-owner for that carrier.
- The current tracked branch state therefore does **not** support reopening `#12` as an implementation-bearing schema-enforcement slice.
- The repeated docs references to `scripts/precompute_features_v17.py` are now more plausibly **historical/stale producer language** than evidence of a current writer surface on this branch.
- The stronger `schema_version=1` framing now appears to live only in baseline/governance memory of the seam, not in a current tracked owner contract.

### Unverified in this packet

- whether an external/private/non-tracked producer still exists outside the current tracked repo surface
- whether the missing feature-writer script exists only in history, another branch, or a local untracked environment
- whether the `.json` feature metadata described in `data/DATA_FORMAT.md` is still produced by any current non-tracked workflow

## Boundary decision

### Current standing conclusion

For `feature/risk-hardening-wave3`, the smallest honest current `#12` reading is now:

- a current tracked **read-side training artifact seam** still exists
- a current tracked **writer/schema-owner/schema_version=1 authority** does **not** currently exist on the branch surface inspected here
- `#12` should therefore stay out of runtime/cache implementation and move next, if at all, into **docs-truthfulness narrowing**

### Operational consequence for Wave 3

Wave 3 should **not** open a `#12` code/enforcement slice from this evidence.

If work continues now, the next admissible `#12` move should be a **separate docs-truthfulness packet** that evaluates and, if warranted, corrects the still-live producer wording in:

- `docs/features/FEATURE_COMPUTATION_MODES.md`
- `scripts/docs/DATA_FETCH_GUIDE.md`
- and any other doc surface that still presents `scripts/precompute_features_v17.py` or a live writer/schema-owner as current branch reality

### What this decision does not mean

This decision does **not** mean:

- that the read-side feature artifacts are irrelevant or fully stale
- that an external/non-tracked producer cannot exist
- that `#12` is deleted outright
- that `data/DATA_FORMAT.md` has already been proven wrong in every detail

## Bottom line

The current tracked Wave 3 branch still shows a training/read-side consumer for feature artifacts, but the writer/schema-owner trace came back empty on present `src/**` and `scripts/**` surfaces. That means `#12` no longer points honestly to a bounded code fix here; it points first to a docs-truthfulness narrowing of stale producer/schema language unless a new tracked producer is later grounded.
