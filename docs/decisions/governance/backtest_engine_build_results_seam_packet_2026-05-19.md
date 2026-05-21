# Backtest engine `_build_results()` seam pre-code packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `proposed candidate-selection packet only / docs-only / non-authorizing`

Later-branch truthfulness note (2026-05-21): this exact candidate has now been implemented on
`feature/risk-hardening-wave3` as a no-behavior-change internal extraction into
`src/core/backtest/engine_results.py`. `BacktestEngine._build_results()` remains the only engine
entry point and now delegates to the internal helper; result payload schema, top-level key
set/order, nested `backtest_info` consumer surface, and git-hash provenance logic remained
unchanged in the landed slice. Observed gate stack for that later branch implementation:
`black --check` and `ruff check` on the touched runtime/proof files; `pytest`
`tests/backtest/test_backtest_engine.py`; `pytest`
`tests/backtest/test_extract_backtest_provenance.py`; `pytest`
`tests/backtest/test_backtest_determinism_smoke.py`; `pytest`
`tests/utils/test_features_asof_cache.py`; `pytest`
`tests/utils/test_features_asof_cache_key_deterministic.py`; `pytest`
`tests/governance/test_pipeline_fast_hash_guard.py`; and `pytest`
`tests/governance/test_import_smoke_backtest_optuna.py`. This packet remains a historical pre-code
selection artifact only; the note above is for later-branch truthfulness, not new authority.

Later-branch next-surface note (2026-05-21): with this exact `_build_results()` seam now landed,
the next fresh current-branch `#15` surface should not be read back through this packet as if the
same candidate were still open. The later wave3 surface-selection note is now
`docs/decisions/governance/backtest_engine_run_setup_surface_selection_packet_2026-05-21.md`,
which narrows any future `#15` reopen to the pre-loop run-setup/config-preparation block inside
`BacktestEngine.run(...)`, not to `_build_results()` again and not to the old worktree-split
story.

This document records one bounded candidate-selection packet only. It does not authorize implementation, module extraction, schema changes, or broader `src/core/backtest/engine.py` modularization. Any later runtime work would require a fresh strict pre-code packet and post-change audit against then-current `HEAD`.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `MED` — why: the slice is docs-only, but it frames a later high-sensitivity `src/core/backtest/*` candidate and must not read as approval
- **Required Path:** `Full` — why: this packet constrains a later high-sensitivity backtest seam and therefore needs explicit scope discipline even though the current edit is docs-only
- **Lane:** `Research-evidence` — why: this slice selects one exact next candidate from current `engine.py` reality without beginning runtime work
- **Skill usage:** `none required` — bounded docs-only packet; no repo-local skill was a closer fit than direct evidence review
- **Objective:** replace the stale worktree-split follow-up story for `#15` with one current-branch seam candidate grounded directly in `src/core/backtest/engine.py`
- **Candidate:** a later no-behavior-change extraction of the current `_build_results()` implementation into `src/core/backtest/engine_results.py`
- **Related artifacts:** `docs/decisions/governance/backtest_engine_split_track_reconcile_packet_2026-05-19.md`, `docs/audit/BACKTEST_ENGINE_AUDIT.md`, `src/core/backtest/engine.py`, `tests/backtest/test_backtest_engine.py`, `tests/backtest/test_extract_backtest_provenance.py`
- **Scoping review:** `Slice Scout -> recommended _build_results() as the smallest current honest seam`
- **Governance review:** `Opus 4.6 Governance Reviewer -> APPROVED_WITH_NOTES` for a docs-only, conditional, non-authorizing packet with explicit schema-drift and scope boundaries

### Scope

- **Scope IN:** this packet only; exact candidate selection for the current `_build_results()` seam; explicit future maximum contemplated scope, frozen future scope OUT, later gates, and rescope triggers
- **Scope OUT:** all runtime/test code edits in the current slice; broader `engine.py` modularization; `load_data()`; `run()`; `_check_htf_exit_conditions()`; `_check_traditional_exit_conditions()`; `_initialize_position_exit_context()`; all `htf_exit*` helper modules; `position_tracker`; `scripts/extract/extract_backtest_provenance.py`; any result-schema drift; any public API or re-export claim for `engine_results.py`
- **Expected changed files:** `docs/decisions/governance/backtest_engine_build_results_seam_packet_2026-05-19.md`
- **Max files touched:** `1`

### Future maximum contemplated scope

The files listed here represent the **maximum contemplated scope** for a later candidate slice; presence on this list does not itself authorize modification.

- `docs/decisions/governance/backtest_engine_build_results_seam_packet_2026-05-19.md`
- `src/core/backtest/engine.py`
- `src/core/backtest/engine_results.py` _(new, internal helper candidate only)_
- `tests/backtest/test_backtest_engine.py`
- `tests/backtest/test_extract_backtest_provenance.py`

Any need to touch a listed Scope OUT file would invalidate this candidate and require re-scoping rather than packet expansion.

### Gates required

For this docs-only packet now:

- targeted docs validation for this packet
- manual wording audit that the packet stays conditional, documentary, and non-authorizing
- manual wording audit that no broader modularization or schema drift is implied
- self-review for hidden behavior impact

For any later runtime slice on this candidate:

- canonical lint/format gates for the touched runtime/test files
- targeted backtest/provenance tests from the existing repo gate surfaces
- focused smoke coverage for the touched engine flow
- determinism replay / parity gate from the canonical existing surfaces
- feature-cache invariance gate from the canonical existing surfaces
- pipeline invariant / component-order hash gate from the canonical existing surfaces

## Purpose

This packet answers one narrow question only:

- what is the smallest current-branch strict pre-code candidate for `#15`, now that the old worktree split claim has been reconciled away as branch-current evidence?

## What changed in this slice

- one new docs-only candidate-selection packet records the current `engine.py` seam choice
- the packet narrows `#15` to one exact future candidate: `_build_results()` only
- the packet freezes future Scope OUT and schema-drift prohibitions up front so the next reopen cannot quietly widen itself

## What did not change

- no runtime code changed
- no backtest behavior changed
- no result payload changed
- no extractor or downstream consumer changed
- no new module was introduced
- no implementation was approved by this packet

## Governing basis

### Observed

1. `docs/decisions/governance/backtest_engine_split_track_reconcile_packet_2026-05-19.md` already concluded that the old worktree split claim lacks a current tracked carrier and that `#15` remains open as a hot-file risk around `src/core/backtest/engine.py`.
2. Current seam anchors in `src/core/backtest/engine.py` include `load_data()` (~491), `run()` (~816), `_check_htf_exit_conditions()` (~1215), `_check_traditional_exit_conditions()` (~1589), `_build_results()` (~1638), and `_initialize_position_exit_context()` (~1729).
3. `_build_results()` currently assembles the final backtest payload from position tracker summaries, execution metadata, git-hash lookup, trade serialization, and `equity_curve`.
4. `tests/backtest/test_extract_backtest_provenance.py` currently consumes the downstream `backtest_info` payload shape extracted from result payloads.
5. `src/core/backtest/engine_results.py` does not currently exist in this branch review.

Line anchors above are observational aids only. If file offsets drift before any later implementation slice, scope does not widen automatically.

### Inferred

- `_build_results()` is a smaller current seam than `load_data()` or `run()` because it sits at the tail end of the replay flow and does not itself decide entry/exit behavior
- `_build_results()` is a safer first candidate than the exit/orchestration seams because those touch direct trade-behavior surfaces already known to be higher sensitivity
- a later `engine_results.py` helper would need to remain internal-only to avoid turning a local extraction into a broader module/public-boundary change
- downstream provenance extraction makes result payload stability a real contract, not a cosmetic preference

### Unverified

- whether a later extraction could be completed without touching any currently frozen Scope OUT surface
- whether a later extraction would need additional targeted consumer proofs beyond the currently identified tests
- whether a later extraction could preserve full contract equivalence without any helper signature drift outside the contemplated scope

## Candidate definition

The only candidate considered here is relocation of the current implementation behind `BacktestEngine._build_results()` into `src/core/backtest/engine_results.py`, while preserving the same private call contract from `src/core/backtest/engine.py`.

If safe extraction would require edits outside the frozen future maximum contemplated scope, this candidate would be invalid and would need a new scoped packet rather than expansion of this one.

## Result-contract boundary

No result-schema drift is authorized by this packet.

Any later runtime slice would have to preserve returned payload shape and semantics — including `backtest_info`, provenance content, execution metadata, git-hash reporting, `trades`, and `equity_curve` — as contract-equivalent for existing consumers.

Inclusion of `tests/backtest/test_extract_backtest_provenance.py` is for consumer-invariant proof only. It does not authorize edits to `scripts/extract/extract_backtest_provenance.py`, and any need to change the extractor or downstream contract would be a re-scope trigger.

## Bottom line

The old `#15` worktree-split story is no longer the honest branch-current follow-up. The smallest current candidate is therefore a later, separately reopened, no-behavior-change extraction of `_build_results()` only — kept conditional, internal, schema-stable, and invalidated immediately if it collides with any frozen Scope OUT surface.
