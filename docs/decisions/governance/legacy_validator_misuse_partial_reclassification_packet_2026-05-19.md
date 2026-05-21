# Legacy validator misuse partial reclassification packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This packet records one bounded partial reclassification only for baseline finding `#17`. It does not claim that config-authority risk is solved. It records that the concrete rename/hard-separation action proposed by historical `CONFIG_GOVERNANCE_AUDIT.md` Finding A is already landed on this branch: the legacy helper surface now uses `LEGACY_SCHEMA_PATH`, `validate_legacy_config`, and `diff_legacy_config`, and current tests already enforce those names. The honest current residual for `#17` is therefore stale documentation still repeating superseded helper names, not an unchanged live code seam waiting for the rename itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: docs-only partial reclassification and truthfulness correction; no code/runtime/config behavior change
- **Required Path:** `Quick path / docs-only truthfulness correction`
- **Lane:** `Research-evidence` — why: this slice narrows current branch-visible interpretation of a config-governance finding without changing runtime authority surfaces
- **Skill usage:** `none required` — bounded docs-only truthfulness slice
- **Objective:** record that the exact rename/hard-separation mitigation for `#17` is already landed in code and tests, and update current reference wording that still uses superseded legacy helper names
- **Related artifacts:** `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`, `docs/audit/CONFIG_GOVERNANCE_AUDIT.md`, `src/core/config/validator.py`, `tests/governance/test_dead_code_tripwires.py`, `tests/integration/test_config_endpoints.py`

### Scope

- **Scope IN:** this packet; one later-branch partial-reclassification note for `#17` in `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`; one terminology update in `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`
- **Scope OUT:** any edit under `src/**`; any change to `ConfigAuthority` runtime semantics; any decision on whitelist expansion (`#7`); any historical-audit rewrite beyond adding current-branch truthfulness where needed
- **Expected changed files:** `docs/decisions/governance/legacy_validator_misuse_partial_reclassification_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`

### Gates required

For this docs-only slice:

- `tests/integration/test_config_endpoints.py::test_legacy_config_validation_and_diff_helpers`
- `tests/governance/test_dead_code_tripwires.py::test_legacy_validator_exports_only_legacy_named_helpers`
- manual wording audit that `#17` is narrowed, not closed as a broader config-authority family
- manual wording audit that the runtime live-update matrix still remains a complementary reference note, not new SSOT

## Purpose

This slice answers one narrow question only:

- what is the honest current-branch reading of baseline `#17` now that the legacy validator helper names are already renamed in code and covered by tests?

## What changed in this slice

- one new docs-only packet records the current residual shape for `#17`
- the baseline now carries a dated later-branch note clarifying that the rename itself is already landed on this checkout
- the current runtime live-update reference note now uses the current legacy helper names instead of superseded names

## What did not change

- no runtime, config, or API behavior changed
- no whitelist or schema semantics changed
- no claim is made that all ConfigAuthority / validator confusion is solved
- no historical audit finding is erased; this slice only narrows the current branch-visible reading

## Governing basis

### Observed

1. `src/core/config/validator.py` now defines `LEGACY_SCHEMA_PATH`, `validate_legacy_config`, and `diff_legacy_config`, and its module docstring explicitly marks the surface as legacy/test-only rather than runtime-config authority.
2. `tests/governance/test_dead_code_tripwires.py::test_legacy_validator_exports_only_legacy_named_helpers` passes and explicitly asserts that `SCHEMA_PATH`, `validate_config`, and `diff_config` are not exported aliases.
3. `tests/integration/test_config_endpoints.py::test_legacy_config_validation_and_diff_helpers` passes and exercises the renamed legacy helper surface.
4. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` still states that the rename fix is not landed.
5. `docs/governance/runtime_config_live_update_matrix_2026-05-15.md` still uses superseded helper names in its legacy-helper surface list.

### Inferred

- the exact code-level mitigation proposed by historical Finding A is already landed on this branch
- the honest current residual for `#17` is stale wording in current branch-visible docs, not an unchanged rename gap in executable code
- the broader config-authority / live-write asymmetry questions remain separate and are not resolved by this slice

### Unverified

- whether every historical audit or archive note across the repo has already been reanchored to the new legacy helper names
- whether future agents will always respect the legacy/runtime boundary without stronger repo-wide cleanup or adoption work

## Bottom line

Finding `#17` should be **partially reclassified** on this branch. The rename/hard-separation action proposed in historical audit Finding A is already landed in code and covered by tests; what remained open here was stale branch-visible documentation. This slice corrects that truthfulness gap only and does not change runtime behavior.
