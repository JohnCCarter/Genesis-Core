# GENESIS_WORKING_CONTRACT.md

> Working anchor for day-start and resumed sessions.
> This file is **not SSOT** and must not override repo governance documents.

## Purpose

This file exists to prevent session drift.
Before starting new work, the agent should re-anchor against the latest validated lane, known blockers, and next admissible step.

## Non-purpose

This file does **not**:
- authorize new implementation work by itself
- override `.github/copilot-instructions.md`, `docs/governance_mode.md`, `AGENTS.md`, or explicit user instructions
- replace packets, reports, or verified evidence artifacts

## Authority order

1. Explicit user request for the current task
2. `.github/copilot-instructions.md`
3. `docs/governance_mode.md`
4. `docs/OPUS_46_GOVERNANCE.md`
5. `AGENTS.md`
6. This file (`GENESIS_WORKING_CONTRACT.md`)

## Current branch and mode anchor

- Branch: `feature/ri-role-map-implementation-2026-03-24`
- Expected mode on this branch: `RESEARCH`
- RESEARCH allows the smallest reproducible, traceable step
- RESEARCH does **not** authorize drift into strict-only surfaces, runtime-default authority, promotion, or champion claims without the required lane/packet

## Core conceptual lock

Genesis must be treated as a **deterministic policy-selection system**.
It is **not** an adaptive system.
It selects among predefined policies based on observable state, and any switching must remain exact, traceable, and reproducible.

## Current validated lane

Active focus right now:
- historical driver/backtest validation on the `3h` lane
- compare real prior evidence vs current bootstrap config behavior
- avoid accidental drift into runtime/paper execution work unless separately opened

## Explicitly not active by default

Unless the user reopens them explicitly with the needed authority, do **not** treat these as active:
- SCPE RI research lane beyond its documented closeout authority
- inherited runtime/integration authority from RI research docs
- runtime-default changes
- paper-shadow follow-up fixes
- promotion/champion claims from isolated research evidence

## Key anchors already verified

- `docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md` closes the bounded research lane and grants no inherited runtime/integration approval
- `docs/governance/scpe_ri_v1_runtime_integration_roadmap_2026-04-20.md` defines fail-closed future ordering
- `docs/governance/scpe_ri_v1_shadow_backtest_packet_boundary_2026-04-20.md` says the next admissible packet, if any, must be a separate RI-only shadow-backtest pre-code slice
- `config/strategy/champions/tBTCUSD_3h.json` is a bootstrap 3h champion, not the strongest known 2024 research config
- better 2024 research results exist under `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/`
- older-year `3h` backtests can appear empty because `src/core/backtest/engine.py` prioritizes `data/raw/*_frozen.parquet` over longer curated history when the frozen file exists

## Last verified facts relevant to today

- canonical bootstrap 3h smoke succeeded for `2024` and `2025`
- the bootstrap 3h config underperforms several earlier `2024` research configs
- older yearly windows like `2017`, `2020`, and `2022` were blocked by data-source priority rather than obvious strategy failure

## Next admissible steps

Choose the smallest valid next step that matches the user request:
1. compare bootstrap 3h results against prior `2024` research configs in one clean table
2. open a bounded packet/fix lane for historical data fallback behavior if older-year testing is required
3. continue read-only historical validation inside already accessible windows

## Hard stops

Stop and re-anchor before proceeding if any of the following happens:
- the next step starts relying on memory instead of cited anchors
- bootstrap 3h results are treated as if they were the best known 2024 evidence
- runtime/paper work starts to creep in without explicit authority
- a task touches strict-only surfaces or champion/promotion semantics
- the lane is no longer obvious from the latest user request

## Required day-start / resume ritual

At the start of a new day or resumed session, do this before reasoning forward:
1. read this file
2. read persistent user memory relevant to workflow
3. read current repo memory items relevant to the active lane
4. identify the latest validated lane and the latest non-active lanes
5. state the next smallest admissible step before making claims

## Update rule

Update this file only when one of these changes:
- active lane
- blocked/not-active lane status
- known verified blocker
- next admissible action

Keep it short. If detail is needed, point to the authoritative doc instead of copying it here.
