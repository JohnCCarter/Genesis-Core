# Bitfinex nonce-error mapping boundary packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the smallest honest current-branch reading of the Bitfinex nonce-error retry seam. It grants no new retry policy, no IO-runtime behavior change, and no paper/live authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice re-anchors current documentation to already-landed exchange-client behavior and records the narrower residual seam only; it changes no IO code, tests, or runtime behavior
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice clarifies current branch-visible IO behavior and future reopen shape only; it does not reopen Bitfinex runtime work
- **Skill usage:** `none required` — bounded docs-only IO boundary slice; no repo-local skill matched this change
- **Objective:** update `docs/architecture/ARCHITECTURE.md` so it reflects current `ExchangeClient.signed_request(...)` retry behavior, and record the honest residual seam as structured error mapping versus fallback text detection rather than a stale “single 10114 retry” reading
- **Base SHA:** `a1a39d0fea97a7c13852aa6635c6949e0dd6ebb0`
- **Related artifacts:** `src/core/io/bitfinex/exchange_client.py`, `tests/utils/test_exchange_client.py`, `docs/architecture/ARCHITECTURE.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

### Scope

- **Scope IN:** this packet; one bounded wording update in `docs/architecture/ARCHITECTURE.md` under the Bitfinex/NonceManager section so it matches current branch-visible retry behavior and does not understate the already-landed retry surface
- **Scope OUT:** any edit under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; any Bitfinex retry-policy implementation change; any paper/live execution change; any attempt to redefine operational readiness from this docs-only note; the already-dirty local governance docs `docs/decisions/governance/backtest_error_policy_reopen_shape_packet_2026-05-19.md`, `docs/decisions/governance/cache_schema_bump_selector_policy_carrier_decision_packet_2026-05-19.md`, and the unrelated local edit to `docs/decisions/governance/premortem_anchor_role_disambiguation_packet_2026-05-19.md`
- **Expected changed files:** `docs/decisions/governance/bitfinex_nonce_error_mapping_boundary_packet_2026-05-19.md`, `docs/architecture/ARCHITECTURE.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and `docs/architecture/ARCHITECTURE.md`
- manual wording audit that the slice reflects current code/tests without implying a new runtime approval
- manual wording audit that the remaining seam is described as residual mapping brittleness, not as unchanged one-shot retry behavior
- focused proof that `tests/utils/test_exchange_client.py` passes on the current branch

## Purpose

This packet answers one narrow question only:

- what is the smallest honest docs-only fix for `#20` now that current exchange-client code and tests already exceed the older baseline’s “single 10114 retry” reading?

## What changed in this slice

- `docs/architecture/ARCHITECTURE.md` now describes current signed REST retry behavior more accurately
- the packet records that the residual seam is the fallback text-based nonce marker, not the absence of bounded retries or tests

## What did not change

- no Bitfinex retry logic changed
- no test behavior changed
- no paper/live, exchange, or runtime authority changed
- no claim is made that structured Bitfinex error mapping is fully solved

## Governing basis

### Observed

1. `src/core/io/bitfinex/exchange_client.py` now uses `_extract_error_markers(...)` to collect numeric codes and text markers from JSON payloads and raw text.
2. `ExchangeClient._is_nonce_error(...)` now checks for `_NONCE_ERROR_CODE = 10114` in extracted codes and only then falls back to text markers containing `"nonce"`.
3. `ExchangeClient.signed_request(...)` retries up to three attempts for nonce errors, retryable status codes (`429`, `5xx`), and transient request errors with bounded jitter via `exponential_backoff_delay(...)`.
4. `tests/utils/test_exchange_client.py` currently passes (`4 passed`) and includes focused coverage for structured nonce retry and retryable-status retry-through-third-attempt behavior.
5. `docs/architecture/ARCHITECTURE.md` still says only `Engångs-retry vid "nonce too small" (10114) med bump_nonce()`.

### Inferred

- The older architecture wording is now stale and understates current branch-visible behavior.
- The honest residual `#20` seam is no longer “there is only a one-shot string-match retry.”
- The honest residual seam is narrower: the client now has structured marker extraction plus tests, but still keeps a generic text fallback on `"nonce"`, so any later reopen should target structured Bitfinex error mapping rather than retry count.

### Unverified in this packet

- whether Bitfinex will keep current error code/payload conventions stable long-term
- whether a later IO hardening slice should remove the text fallback entirely
- whether additional integration coverage is needed beyond the current focused unit tests

## Boundary decision

### Current standing conclusion

For `feature/risk-hardening-wave2`, the honest current reading is:

- keep the existing exchange-client behavior as-is
- update docs so they do not describe the current client as only a single 10114 retry path
- if a later bounded reopen is needed, target structured Bitfinex error mapping and fallback narrowing, not basic retry count

This packet therefore authorizes only one bounded wording update in `docs/architecture/ARCHITECTURE.md`.

### Non-goals

This slice does **not**:

- approve new retry attempts or backoff changes
- change exchange-client behavior
- claim that Bitfinex error mapping is fully robust against future upstream format changes
- authorize paper/live work

## Hard stop and reopen rule

If a later slice needs any of the following, it must stop and reopen as a separate bounded packet:

- source changes under `src/core/io/bitfinex/**`
- new tests beyond current focused proof
- paper/live behavior or operational-readiness claims
- removal or redesign of the residual text fallback

## Bottom line

The smallest honest `#20` move is a **docs re-anchor**: current Bitfinex signed-request behavior already includes structured marker extraction, bounded multi-attempt retry, and focused tests. The remaining seam is the generic `"nonce"` text fallback, so any future reopen should target structured error mapping rather than pretend the client is still stuck at a single 10114 retry.
