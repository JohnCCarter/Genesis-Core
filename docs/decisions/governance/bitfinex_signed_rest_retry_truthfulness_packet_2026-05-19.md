# Bitfinex signed REST retry truthfulness packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `implemented / docs-only / truthfulness-correction`

This packet records one bounded docs-only truthfulness correction for the stale `#21` branch reading in the 2026-05-18 project baseline. It does not change exchange-client behavior, approve a new retry budget, or claim that Bitfinex burst-rate-limit handling is fully solved.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice corrects wording only and does not touch runtime, test, or config surfaces
- **Required Path:** `Quick` — why: two docs files only, no runtime behavior change, no dependency/schema/env/default changes
- **Lane:** `Research-evidence` — why: this slice narrows a stale baseline claim to current tracked evidence
- **Skill usage:** `none required` — bounded docs-only truthfulness correction
- **Objective:** record that the current branch no longer matches the older `#21` “single-retry” reading and add a dated later-branch truthfulness note to the baseline without rewriting its historical 2026-05-18 framing
- **Related artifacts:** `src/core/io/bitfinex/exchange_client.py`, `tests/utils/test_exchange_client.py`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `docs/decisions/governance/bitfinex_nonce_error_mapping_boundary_packet_2026-05-19.md`

### Scope

- **Scope IN:** this packet; one later-branch truthfulness note in `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` limited to the `#21` reading under the IO / Bitfinex section
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `artifacts/**`, and `results/**`; any retry-policy or backoff implementation change; any operational-readiness, paper/live, or “fully solved” claim; any broad color-table rewrite beyond the dated `#21` note
- **Expected changed files:** `docs/decisions/governance/bitfinex_signed_rest_retry_truthfulness_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the baseline remains historical and the new note is explicitly dated as later-branch truthfulness
- manual wording audit that no new retry-policy approval is implied
- focused proof that `tests/utils/test_exchange_client.py` passes on the current branch

## Purpose

This packet answers one narrow question only:

- what is the smallest honest current-branch correction for the stale `#21` “single-retry on signed REST” reading in the 2026-05-18 baseline?

## What changed in this slice

- one new docs-only truthfulness packet records the evidence boundary for `#21`
- the 2026-05-18 baseline now carries a dated later-branch note clarifying that current branch code no longer matches the older single-retry reading
- the historical baseline wording remains preserved as a 2026-05-18 assessment rather than being silently rewritten away

## What did not change

- no exchange-client code changed
- no retry budget or backoff parameters changed
- no tests changed
- no paper/live or operational-readiness claim was added
- no claim is made that Bitfinex burst-rate-limit resilience is fully solved

## Governing basis

### Observed

1. `src/core/io/bitfinex/exchange_client.py` currently defines `_MAX_SIGNED_REQUEST_ATTEMPTS = 3`.
2. `ExchangeClient.signed_request(...)` retries nonce errors, retryable status codes (`429`, `5xx`), and transient request errors while attempts remain.
3. `ExchangeClient._sleep_jitter(...)` currently delegates to `exponential_backoff_delay(...)` with `base_delay=0.05`, `max_backoff=0.4`, and jitter `100-300ms`.
4. `tests/utils/test_exchange_client.py` includes focused proof for structured nonce retry and retryable-status retry-through-third-attempt behavior.
5. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` still records `#21` as a “Single-retry på signed REST” seam and still cites `_sleep_jitter` as `base_delay=0.0, max_backoff=0.3`.
6. `docs/decisions/governance/bitfinex_nonce_error_mapping_boundary_packet_2026-05-19.md` already narrowed the adjacent `#20` seam to structured error mapping versus fallback text detection, not to an absence of bounded retries.

### Inferred

- the older `#21` baseline wording is now stale for the current branch
- the smallest honest correction is a dated later-branch truthfulness note, not a new runtime change
- the current residual `#21` question, if reopened later, is no longer “single-retry versus retry,” but whether the existing bounded retry budget and backoff remain sufficient under real burst-rate-limit conditions

### Unverified

- whether the current three-attempt budget is operationally sufficient under sustained Bitfinex burst-rate-limit scenarios
- whether later IO hardening should adjust retry budget, backoff envelope, or metrics
- whether broader integration or paper/live evidence is needed beyond the current focused unit tests

## Applied correction

The baseline now carries a dated note stating that on `feature/risk-hardening-wave2`:

- `#21` should be read as a historical 2026-05-18 assessment only
- current `ExchangeClient.signed_request(...)` behavior includes bounded multi-attempt retry
- `_sleep_jitter(...)` now uses `exponential_backoff_delay(...)` rather than the older parameters cited in the baseline
- any future reopen should target retry-budget sufficiency or operational evidence rather than restating the stale one-shot claim

## Bottom line

For the current branch, the `#21` premortem wording is stronger than the code and focused tests support today. The smallest honest move is therefore a docs-only truthfulness reconcile: preserve the historical baseline, add a dated later-branch note, and leave any future runtime retry-budget work as a separately reopened slice.
