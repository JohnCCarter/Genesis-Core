# Intelligence Pipeline Branch Handoff

Status: DESCRIPTIVE HANDOFF NOTE
Authority: Subordinate to the canonical intelligence preparation documents

## Purpose

This note summarizes what is complete in `feature/intelligence-pipeline-v1`, what remains valid in this branch, and what must move to the next implementation branch.

This note is descriptive only and does not override:

- `docs/intelligence/GOVERNANCE_INTELLIGENCE_RULES.md`
- `docs/intelligence/INTELLIGENCE_ARCHITECTURE.md`
- `docs/intelligence/INTELLIGENCE_PIPELINE_SPEC.md`
- `docs/intelligence/INTELLIGENCE_PARALLEL_DEVELOPMENT_RULES.md`

Any follow-on branch name mentioned here is a working label only and does not change governance or merge order.

## Complete in this branch

The preparation/contracts branch now owns and preserves:

- canonical intelligence documentation under `docs/intelligence/`
- frozen canonical event schema under `src/core/intelligence/events/`
- package structure for `collection/`, `normalization/`, `features/`, and `evaluation/`
- public package export surfaces for those prep modules
- contract-only tests covering schema validation, package import surfaces, stage compatibility, and deterministic ordering assumptions

## Still valid in this branch

The following work remains valid in `feature/intelligence-pipeline-v1`:

- interface refinements
- package/export cleanup
- stage compatibility tests
- deterministic / shallow frozen-contract tests
- contract clarifications consistent with the existing intelligence docs

## Must move to the next implementation branch

The following work must move to the next processing branch, proposed working label:

- `feature/intelligence-pipeline-processing-v1`

That branch should own actual pipeline processing work such as:

- collection processing logic
- normalization processing logic
- feature derivation logic
- evaluation logic
- any downstream pipeline assembly beyond contract-only compatibility

## Controlling scope wording that must remain in force

The following wording remains controlling for this branch:

> The preparation phase may define contracts, interfaces, package layout, and tests only.

> The preparation phase must not add runtime intelligence processing logic.

> The preparation phase must not add database complexity, orchestration logic, or intelligence analysis logic.

> This preparation slice does not implement:
>
> - event collection logic
> - normalization algorithms
> - feature extraction logic
> - evaluation logic

## Branch handoff summary

`feature/intelligence-pipeline-v1` should be treated as the canonical preparation/contracts branch.

The next implementation branch should consume the existing docs and canonical event contracts without redefining them.
