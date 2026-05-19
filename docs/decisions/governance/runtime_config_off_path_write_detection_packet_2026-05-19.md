# Runtime config off-path write detection packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `pre-code contract / runtime-touching / non-authorizing until implemented`

This packet records one bounded config-authority hardening slice for best-effort divergence detection between the current `config/runtime.json` state and the latest audit entry when that entry is directly comparable. It authorizes a warning-only detection path; it does not authorize blocking, file watching, audit-schema changes, whitelist expansion, API changes, or any replacement source of truth.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `obs`
- **Risk:** `HIGH` — why: this slice touches the high-sensitivity runtime/config-authority surface in `src/core/config/authority.py`, even though the approved behavior change is limited to one warning-only path
- **Required Path:** `Full` — why: runtime/config-authority surface with an explicit narrow behavior-change exception requires pre-code contract, focused tests, and post-change verification
- **Lane:** `Runtime-integration` — why: the slice changes runtime-side authority observability behavior, not just documentation
- **Skill usage:** `none required` — no repository skill matched this exact config-authority drift-detection slice
- **Objective:** add one best-effort warning when the current `config/runtime.json` canonical version/hash diverges from the latest `logs/config_audit.jsonl` entry that is directly comparable during `ConfigAuthority` startup
- **Related artifacts:** `src/core/config/authority.py`, `tests/governance/test_config_ssot.py`, `config/README.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Governance review:** `Opus 4.6 Governance Reviewer -> APPROVED_WITH_NOTES`

### Scope

- **Scope IN:** this packet; one narrow startup-time divergence-detection helper in `src/core/config/authority.py`; focused tests in `tests/governance/test_config_ssot.py`
- **Scope OUT:** `config/runtime.json` contents; `logs/config_audit.jsonl` schema; `src/core/api/**`; whitelist semantics; optimistic-locking semantics; blocking prevention/file locks/watchers; rewrite-on-drift behavior; any new SSOT or authority path; any API or error-response change
- **Expected changed files:** `docs/decisions/governance/runtime_config_off_path_write_detection_packet_2026-05-19.md`, `src/core/config/authority.py`, `tests/governance/test_config_ssot.py`
- **Max files touched:** `3`

### Approved behavior-change exception

The only approved behavior change in this slice is:

- emit one warning when `ConfigAuthority` can safely compare the current canonical runtime version/hash against the latest comparable audit snapshot and those values diverge

This warning means only:

- current runtime state diverges from the latest comparable audit snapshot
- operator review is recommended

It does **not** mean:

- tampering is proven
- the load path should block
- `runtime.json` should be rewritten
- audit history should be repaired automatically

### Gates required

- `black --check .`
- `ruff check .`
- `pytest tests/governance/test_config_ssot.py`
- `pytest tests/integration/test_config_endpoints.py`
- `pytest tests/integration/test_config_api_e2e.py`
- `pytest tests/backtest/test_backtest_determinism_smoke.py`
- `pytest tests/utils/test_feature_parity.py`
- `pytest tests/integration/test_precompute_vs_runtime.py`
- `pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- manual diff audit that the slice adds warning-only detection and no API/schema/write-block drift

## Purpose

This packet answers one narrow question only:

- what is the smallest honest runtime-side mitigation for baseline finding `#22` if the repository should detect, but not block, off-path `config/runtime.json` drift?

## Governing basis

### Observed

1. `src/core/config/authority.py` currently writes audited atomic updates with `hash_before`, `hash_after`, `expected_version`, and `new_version`, but does not currently expose a comparable startup-time drift warning hook.
2. `config/README.md` already documents that direct/off-path edits to `config/runtime.json` bypass the `ConfigAuthority` propose path and its audit attribution.
3. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` records `#22` as structural and names detection rather than prevention as the honest mitigation shape.
4. Current repo state check before implementation showed the live `config/runtime.json` version/hash matched the latest directly comparable `logs/config_audit.jsonl` entry, so the proposed warning does not immediately trip on the current checkout.

### Inferred

- the smallest honest mitigation is best-effort divergence detection, not prevention
- the comparison must reuse the existing canonical config hash contract rather than inventing a second hash definition
- fail-open behavior is required when no safe comparable audit state exists

### Unverified before implementation

- whether a later slice should add stronger mismatch reporting or operator tooling
- whether malformed audit tails should later earn a separate warning path
- whether any future prevention mechanism would be worth the operational complexity

## Test contract

Focused tests must prove at least:

1. matching runtime state and latest directly comparable audit entry => no warning
2. externally modified runtime state after an audited write => warning on init/startup path
3. missing comparable audit state => fail open (no exception, no warning by default)
4. drift warning path causes no side effects beyond logging: no rewrite, no audit append, no load block

## Bottom line

This slice is a narrow observability hardening change on a high-sensitivity config-authority surface. It may add one warning when current runtime state diverges from the latest audit entry that is directly comparable, and nothing more.
