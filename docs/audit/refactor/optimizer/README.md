# Optimizer refactor audit index

This README is a navigation aid for the files currently present in this folder.
It does not replace or reinterpret the underlying audit or evidence documents.
For authoritative details, open the referenced command packet and context map files directly.

> Later-status note (2026-05-19): On `feature/risk-hardening-wave2`, treat this folder as
> **historical optimizer refactor traceability only**. It is not a branch-current approval,
> completion signal, or active refactor queue by itself.
>
> Current observed branch-state context at HEAD `481269a7`:
>
> - `src/core/optimizer/runner.py` = 1625 lines
> - `src/core/optimizer/runner_optuna_orchestration.py` = 1113 lines
> - `src/core/optimizer/runner_config.py` = 830 lines
>
> If a later bounded reopen is needed, the first admissible subtopic is the
> **orchestration / validation / promotion boundary** across current `runner.py` and
> `runner_optuna_orchestration.py`, rather than blanket continuation of all March split artifacts.

> Later-branch truthfulness note (2026-05-21, `feature/risk-hardening-wave3`): the first
> code-bearing follow-up on that broader boundary is now already landed in current tracked code via
> `src/core/optimizer/runner.py`, `src/core/optimizer/runner_validation.py`, and
> `src/core/optimizer/runner_trial_results.py`. This README should therefore no longer be read as
> if the default next reopen still automatically starts with broad `runner.py` +
> `runner_optuna_orchestration.py` work. The folder remains historical traceability only; if a later
> bounded reopen is needed from current wave3 truth, the next fresh `#16` surface is the
> validation result-payload carrier in `runner_validation.py::run_validation_stage_impl(...)`, as
> recorded in
> `docs/decisions/governance/optimizer_validation_payload_carrier_surface_selection_packet_2026-05-21.md`.

## What lives here

This folder currently holds optimizer refactor planning/evidence artifacts for the `runner.py` split work.
The file pattern in this folder is primarily:

- `command_packet_*` — scope, constraints, and gate expectations for a slice
- `context_map_*` — local context and file/symbol map for that slice

## Suggested reading order

1. Open the newest `command_packet_*` file first.
2. Open the matching `context_map_*` file next.
3. Read older packet/map pairs only when you need the history of a previous slice.

## Current observed subtopics

- split-2: Optuna orchestration / validation / promotion support
- split-3: config / metadata / parameter-space extraction

## Interpretation note

Treat these files as refactor traceability records for this folder.
Do not infer broader completion or approval status beyond what each individual packet or signoff document explicitly states.
