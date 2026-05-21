# Runtime config `exit.enabled` live-update pre-code packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `precode-defined / docs-only / non-authorizing`

This document opens one bounded pre-code packet for the exact field set `exit.enabled` only. Any later code slice must keep admission fail-closed to the singleton nested patch shape `{"exit": {"enabled": <bool>}}` only; empty dicts, sibling keys, mixed keys, and partial application remain out of bounds. The current slice is docs-only and does not approve implementation, change runtime behavior, widen the live-write whitelist, alter public API behavior, or change truthfulness claims outside this packet.

## Implementation-status note (2026-05-19)

The later bounded runtime slice framed by this packet has now been landed in the current branch.

- `src/core/config/authority.py` now admits only the singleton nested patch shape `{"exit": {"enabled": <bool>}}` for live updates
- non-dict, empty-dict, sibling-only, and mixed-key `exit` payloads remain rejected atomically before merge
- targeted proofs were added in `tests/governance/test_config_ssot.py`, `tests/integration/test_config_endpoints.py`, and `tests/integration/test_config_api_e2e.py`
- verification completed with focused config-authority/API tests plus determinism replay, feature parity / precompute-runtime parity, pipeline invariant, `black --check`, `ruff check`, and `.venv\Scripts\bandit.exe -q -r src/core/config/authority.py`

This status note records the later implementation outcome only. It does not widen the original packet scope.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `MED` — why: this slice remains docs-only, but it frames a later higher-sensitivity runtime/config-authority behavior-change candidate and could be misread as approval if not written tightly
- **Required Path:** `Full` — why: although the current slice touches docs only, the subject is a higher-sensitivity runtime/config-authority candidate and this packet was pre-reviewed for scope discipline
- **Lane:** `Research-evidence` — why: this slice narrows the next admissible reopen to one exact field set only; it does not begin implementation
- **Skill usage:** `none required` — bounded docs-only packet; no repo-local skill matched this slice
- **Objective:** define the smallest honest next bounded candidate for parked item `#7` now that the lower-risk `non_whitelisted_field` API-semantics line is already landed
- **Candidate:** `future exact live-update admission of exit.enabled only`
- **Base SHA:** `b71b1f59d05b0dc547d5a7e297d8f958b03c29ea`
- **Related artifacts:** `docs/decisions/governance/runtime_config_live_update_policy_boundary_packet_2026-05-15.md`, `docs/decisions/governance/runtime_config_live_update_b2_candidate_screening_note_2026-05-19.md`, `docs/decisions/governance/runtime_config_propose_non_whitelisted_error_semantics_packet_2026-05-15.md`, `src/core/config/schema.py`, `src/core/config/authority.py`, `src/core/api/config.py`, `src/core/backtest/engine.py`
- **Pre-code review:** `Opus 4.6 Governance Reviewer -> APPROVED_WITH_NOTES` for one docs-only packet limited to exact field set `exit.enabled`

### Scope

- **Scope IN:** one new docs-only pre-code packet; exact candidate selection for `exit.enabled` only; explicit future scope/gates/stop conditions for a later implementation slice; explicit statement that runtime consumer files are cited as sensitivity evidence only
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; whole-subtree `exit` admission; all sibling `exit.*` leaves; all API error-detail changes; all schema/default changes; all runtime consumer edits; all paper/live/readiness/promotion claims; all claims that implementation is already approved
- **Expected changed files:** `docs/decisions/governance/runtime_config_exit_enabled_live_update_precode_packet_2026-05-19.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this packet
- manual wording audit that the slice remains docs-only and non-authorizing
- manual wording audit that `exit.enabled` stays separated from whole-subtree `exit` admission
- manual consistency review against the current live-update boundary packet, B2 screening note, and landed `non_whitelisted_field` semantics line
- governance pre-code review recorded in this packet

### Stop Conditions

- any wording that treats this packet as implementation approval
- any wording that widens scope from exact `exit.enabled` to `exit.*` or whole-object `exit`
- any wording that silently includes API detail changes, schema changes, or runtime consumer edits
- any wording that claims current runtime behavior already changed because this packet exists
- any wording that treats backtest-engine usage evidence as approval to edit `src/core/backtest/**`

## Purpose

This packet answers one narrow question only:

- if `#7` is reopened honestly after the already-landed `non_whitelisted_field` API-semantics work, what is the next exact bounded candidate?

## What changed in this slice

- one new docs-only pre-code packet narrows the remaining `#7` reopen to exact field set `exit.enabled`
- the packet records why the lower-risk API-semantics line is no longer the open question
- the packet defines future scope, gates, stop conditions, and rollback boundaries for a later implementation-bearing slice without approving it

## What did not change

- no live-write whitelist changed
- no config-authority behavior changed
- no API behavior changed
- no runtime/default/schema behavior changed
- no tests changed
- no runtime consumer files changed

## Governing basis

### Observed

1. `src/core/config/schema.py` currently declares top-level `exit` in `RuntimeConfig`, so this is not a schema-discovery question.
2. `src/core/config/authority.py::ConfigAuthority.propose_update(...)` currently whitelists only `{strategy_family, thresholds, gates, risk, ev, multi_timeframe}` at the top level, so `exit` remains schema-valid but live-blocked.
3. `src/core/api/config.py` currently maps non-whitelisted propose failures to the coarse public detail `non_whitelisted_field`.
4. `docs/decisions/governance/runtime_config_propose_non_whitelisted_error_semantics_packet_2026-05-15.md` now carries an implementation-status note saying that lower-risk API-semantics candidate has already been landed in a separate bounded slice.
5. `docs/decisions/governance/runtime_config_live_update_b2_candidate_screening_note_2026-05-19.md` records that `exit.enabled` is the first grounded behavior-active blocked candidate and that the next admissible move, if reopened, must still be a separate bounded pre-code packet for one exact field set only.
6. Current tracked engine usage evidence shows `configs.get("exit", {})` in `src/core/backtest/engine.py` at the current active seams around lines `1238`, `1463`, and `1599`.

### Inferred

- the remaining honest `#7` reopen is no longer the already-landed API-detail clarification line
- the smallest current reopen is a **higher-sensitivity runtime/config-authority candidate** framed around one exact field only: `exit.enabled`
- any later admission of `exit.enabled` through the guarded propose path would be a **behavior-change candidate**, not a docs clarification
- the current packet must therefore stay narrow enough that runtime consumer evidence is used only to justify sensitivity and candidate selection, not to authorize consumer edits
- public API error semantics are not automatically in scope for this reopen, because the coarse `non_whitelisted_field` line already exists

### Unverified in this packet

- whether exact `exit.enabled` admission can be implemented without whole-object `exit` admission semantics
- whether the later implementation can remain contained to authority admission plus targeted tests only
- whether paper/live surfaces read the same config seam in a way that would require extra gating
- whether an even smaller active blocked field set exists and would be a better first candidate than `exit.enabled`

## Candidate selection

### Current standing conclusion

The next admissible `#7` reopen is:

- a **docs-only pre-code packet for exact field set `exit.enabled` only**

This is a candidate-selection conclusion only. It is **not** approval to implement the change.

### Why exact `exit.enabled`

The current evidence supports this reading:

- `warmup_bars` remains useful as a blocked proof seam, but the current screening note did not prove it as the best first active candidate
- the lower-risk public API error-semantics candidate is already landed
- `exit.enabled` is the first currently grounded blocked field whose behavior is clearly active in backtest flows

That makes `exit.enabled` the smallest honest remaining reopen candidate, but also a higher-sensitivity one.

## Likely future implementation scope

If this candidate is later reopened as an implementation-bearing slice, the smallest honest starting scope is likely:

- `src/core/config/authority.py`
- `tests/governance/test_config_ssot.py`
- `tests/integration/test_config_endpoints.py`
- `tests/integration/test_config_api_e2e.py`

Current runtime consumer files such as `src/core/backtest/engine.py` are cited here as **sensitivity evidence only**, not as approved edit scope.

### Likely future scope OUT

A later implementation slice for this candidate must keep the following out of scope unless separately reopened:

- whole-subtree `exit` admission
- all sibling `exit.*` leaves other than `exit.enabled`
- `src/core/config/schema.py` unless a newly discovered blocker proves change is strictly necessary
- `src/core/api/config.py` unless public contract changes beyond current coarse behavior become strictly necessary
- all edits under `src/core/backtest/**`, `src/core/optimizer/**`, `src/core/strategy/**`, or paper/live execution edges
- default value changes
- public API error-detail redesign
- readiness, promotion, paper/live, or champion claims

## What the future implementation packet must define

A later implementation-bearing packet for this candidate must define at minimum:

- the exact singleton nested patch shape admitted for `exit.enabled`
- the exact pre-merge guard that rejects non-dict, empty-dict, sibling-only, and mixed-key `exit` payloads atomically
- the exact mechanism that keeps sibling `exit.*` leaves rejected with no partial-apply behavior
- whether whole-object `exit` patches stay rejected unless they match the singleton `{"enabled": <bool>}` shape exactly
- whether current merge/propose semantics are sufficient without widening any broader selector path
- the exact targeted tests proving leaf-only containment
- the exact rollback boundary if the change needs to be reverted

## Minimum future verification stack

If this candidate advances to code later, the later packet must require at minimum:

1. `black --check .`
2. `ruff check .`
3. `bandit -r src -c bandit.yaml`
4. focused pytest subset for config authority / API semantics, including accept/reject proofs for singleton, empty, non-dict, sibling-only, and mixed-key `exit` payloads
5. one exact-containment proof that:
   - `exit.enabled` becomes live-writable only for the singleton nested patch shape
   - empty, non-dict, sibling-only, and mixed-key `exit` payloads remain rejected
   - sibling `exit.*` leaves remain rejected
   - rejected proposals do not partially apply and leave persisted config unchanged
   - no implicit widening to whole-object `exit` admission occurs
6. one replay/parity proof for unchanged config states
7. one feature-cache invariance check
8. one pipeline invariant / component-order hash check
9. one focused smoke command for the touched authority flow

This list is for the later implementation slice only. It is **not** claimed as already satisfied by the current docs-only packet.

## Required future stop conditions

A later implementation slice must stop and reopen if any of the following becomes necessary:

- whole-object `exit` admission instead of exact `exit.enabled`
- propose-path selector or merge semantics changes broader than the exact leaf admission
- public API detail changes beyond the current coarse `non_whitelisted_field` contract
- schema/default changes
- edits in runtime consumer files such as `src/core/backtest/**`
- widened paper/live or optimizer integration claims

## Rollback boundary for the later code slice

If this candidate is implemented later and must be reverted, the rollback boundary must remain limited to:

- exact `exit.enabled` authority admission, and
- the targeted tests that prove that exact admission and sibling rejection behavior

No sibling `exit.*` leaf or broader selector semantics may remain enabled after rollback.

## Bottom line

The low-risk `#7` line is no longer the open question because the coarse `non_whitelisted_field` API-semantics candidate is already landed. The next honest reopen is therefore a separate docs-only pre-code packet for **exact field set `exit.enabled` only**. That candidate is admissible to frame now, but any later implementation would be a higher-sensitivity runtime/config-authority behavior-change slice and must be reopened separately with full verification.
