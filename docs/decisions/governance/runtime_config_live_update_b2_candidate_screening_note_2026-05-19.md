# Runtime config live-update B2 candidate screening note

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `screening-recorded / docs-only / non-authorizing`

This document is an evidence / screening artifact in `RESEARCH` and grants no implementation, runtime, config-authority, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin code, test, config, whitelist, or API behavior changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice only records the current B2 candidate-screening result for future runtime-config live-update work; the main risk is wording drift that could be mistaken for selecting or approving a whitelist-expansion target
- **Required Path:** `Quick`
- **Objective:** record why no exact B2 field-set packet is opened yet after the current screening pass across blocked schema-valid fields
- **Candidate line:** `future runtime-config live-update B2 field-set work`
- **Base SHA:** `60f5592f`

### Scope

- **Scope IN:** one docs-only screening note; explicit separation between `warmup_bars` as a blocked proof seam and any future live-update candidate selection; explicit record that `exit.enabled` is the first currently grounded behavior-active blocked candidate; explicit statement that no exact field-set packet is opened by this note
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; all whitelist expansion; all schema changes; all API behavior changes; all runtime/default changes; all claims that any specific field is already approved for live update
- **Expected changed files:** `docs/decisions/governance/runtime_config_live_update_b2_candidate_screening_note_2026-05-19.md`
- **Max files touched:** `1`

### Gates required

For this note itself:

- targeted docs validation for this file
- manual wording audit that this note remains screening-only and non-authorizing
- manual wording audit that proof of current blockedness is kept separate from proof of future candidate suitability
- manual consistency review against the current boundary packet and current live-update matrix

### Stop Conditions

- any wording that treats this note as approval to widen the live-write whitelist
- any wording that silently opens a B2 exact-field packet without saying so
- any wording that treats `warmup_bars` blockedness as proof that it is a suitable live-update target
- any wording that treats `exit.enabled` as implementation-approved rather than later-packet-admissible
- any wording that implies current runtime behavior changed because this note exists

## Purpose

This note answers one narrow question only:

- after the current B1 clarification line and blocked-field scan, what is the next honest B2 move?

## Governing basis

This screening note is downstream of the following already visible current-state surfaces:

- `docs/decisions/governance/runtime_config_live_update_policy_boundary_packet_2026-05-15.md`
- `docs/decisions/governance/runtime_config_propose_non_whitelisted_error_semantics_packet_2026-05-15.md`
- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`
- `src/core/config/authority.py`
- `src/core/config/schema.py`
- `src/core/api/config.py`
- `src/core/api/status.py`
- `src/core/optimizer/runner_config.py`
- `src/core/pipeline.py`

### Observed

1. `ConfigAuthority.propose_update(...)` currently allows live writes only for top-level keys `{strategy_family, thresholds, gates, risk, ev, multi_timeframe}`, with narrower nested allowlists under some of those branches.
2. `RuntimeConfig` currently declares additional schema-valid but live-blocked top-level fields including `exit`, `warmup_bars`, `htf_exit_config`, `htf_fib`, `ltf_fib`, and `features`.
3. The current `src/**` authority-consumer scan found `ConfigAuthority` usage in `src/core/api/config.py`, `src/core/api/status.py`, and `src/core/optimizer/runner_config.py`.
4. The current field scan found `warmup_bars` used across pipeline/backtest/optimizer parameter/default paths, but did not establish a clear current consumer seam where authority-loaded runtime-config `warmup_bars` is read as an active live-update control.
5. The current field scan found `exit` behavior to be clearly active in backtest/optimizer flows through merged configs using `configs.get("exit", {})`, including `exit.enabled`.
6. The existing `runtime_config_propose_non_whitelisted_error_semantics_packet_2026-05-15.md` already uses `warmup_bars` as a concrete schema-valid/live-blocked proof seam for guarded propose rejection semantics.

### Inferred

- `warmup_bars` is currently a good proof seam for “schema-valid but live-blocked”, but it is under-grounded as the first whitelist-expansion target because the current scan did not prove a clear authority-loaded runtime-config consumer seam for it.
- `exit.enabled` is the first currently grounded blocked candidate whose behavior is visibly active, but that makes it a higher-risk runtime/config-authority candidate rather than a low-risk first pick.
- The cheapest honest next step is therefore to record the screening result explicitly instead of pretending that a low-risk exact field-set candidate is already proven.
- This note does not foreclose a later docs-only pre-code packet for `exit.enabled`; it only records that such a packet would be a higher-sensitivity candidate-selection move, not a continuation of the `warmup_bars` proof seam.

### Unverified

- whether `RuntimeConfig.warmup_bars` should later gain a clearly traced authority-loaded consumer seam or should remain only a schema-valid/live-blocked field
- whether `exit.enabled` is ultimately the right first B2 implementation candidate versus another smaller active blocked field set
- the exact implementation-time verification stack that would be required if a future packet selects `exit.enabled`

## Screening result

### Current standing conclusion

No exact B2 field-set packet is opened by this note.

More specifically:

- `warmup_bars` remains recorded as a **schema-valid / live-blocked proof seam**, not as a selected whitelist-expansion target
- `exit.enabled` is recorded as the first **grounded behavior-active blocked candidate**, but only as a possible later packet candidate
- no low-risk active field-set has been proven by the current screening pass

### What changed

This note adds one clarification only:

- the repository now has an explicit screening record separating “proof that a field is blocked” from “proof that the same field is a good first expansion target”

### What did not change

This note does **not** change any of the following:

- the current live-write whitelist in `src/core/config/authority.py`
- the declared runtime schema in `src/core/config/schema.py`
- API behavior in `src/core/api/config.py`
- optimizer/backtest/default behavior
- the current B1-style reading documented by the live-update matrix and boundary packet
- the possibility of opening a later separate pre-code packet for one exact high-sensitivity field set

## Reopen rule

If this line is reopened later, the next admissible move must still be a **separate bounded pre-code packet** that chooses one exact field set only.

From the current screening state, the most honest reopen paths are:

- a later docs-only pre-code packet for `exit.enabled` as a high-sensitivity behavior-change candidate, or
- a new evidence slice that proves a smaller active blocked field set exists and is better grounded than `exit.enabled`

This note does not authorize either path by itself.

## Bottom line

The current screening pass did not prove an honest low-risk B2 whitelist-expansion target. `warmup_bars` remains useful as a blocked proof seam, but is under-grounded as a live-update candidate; `exit.enabled` is the first clearly active blocked candidate, but that makes it a later high-sensitivity packet candidate rather than an immediate field-set selection.
