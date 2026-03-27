# Legacy + RI research Phase 0 baseline lock

Date: 2026-03-27
Status: tracked / analysis-only / no implementation authority
Lane: `run_intent: research_experiment`
Phase: `0 - lock current baseline`

## Purpose

This artifact locks the current baseline for the Legacy + RI research lane before any new research hypotheses are opened.

This artifact does not authorize implementation, launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Canonical baseline decisions

### Legacy reference state

- The current Legacy reference state is the incumbent control baseline at `config/strategy/champions/tBTCUSD_3h.json`.
- Legacy remains the control/reference family baseline for this research lane.
- No runtime default, champion, or authority semantics are changed by this artifact.

### RI canonical baseline reference

- The canonical RI baseline reference for this roadmap is the slice-4 anchor from `results/hparam_search/run_20260319_111953`.
- Canonical validation plateau: `0.22516209452403432`.
- Canonical tied-winner anchor: `validation/trial_002.json`.
- Canonical anchor rule: among tied validation winners, select the member with the highest train score.
- This is the RI baseline to carry forward into the next phase.

## Ambiguity resolution

- The earlier `0.22729723723866666` RI result referenced from `results/hparam_search/run_20260318_112046` is retained as historical challenger-family evidence only.
- It is not the canonical RI baseline for this Phase 0 lock.
- Ambiguity is resolved by governance precedence:
  1. later explicitly frozen governed anchor
  2. deterministic tie-break rule
  3. continuity into subsequent governed slices
- On that basis, the slice-4 anchor `0.22516209452403432` is canonical for baseline locking.

## Locked statements

- Legacy and RI remain separate strategy families.
- Mixed family surfaces must not be reintroduced.
- Current RI local research surfaces explored in the governed challenger chain are treated as exhausted for further local tuning.
- Further RI progress now requires new hypotheses rather than more local retuning of the already explored surfaces.

## Out of scope

- no code changes
- no config changes
- no launches
- no runtime default changes
- no champion changes
- no coordination, router, or ensemble implementation
- no comparison, readiness, or promotion opening

## Next admissible step

- The next admissible step after this baseline lock is `Phase 1 - define the experiment map`.
- Phase 1 is a governed mapping/specification step only.
- Phase 1 is not implementation authority.
