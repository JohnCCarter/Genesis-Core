# Legacy policy-router 2024 control setup implementation packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `implemented / config-test-docs / no backtest or runtime execution authority`

This packet records the completed setup-proof slice for the first true Legacy-family
policy-router control line.

It materializes one tmp-only Legacy carrier and one focused governance proof that the carrier can
preserve an enabled `research_policy_router` leaf while remaining a true Legacy config.

It does **not** authorize backtest execution, results generation, runtime-default changes,
schema/config-authority rewrites, or cross-family promotion claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is config/test/docs only, stays outside runtime code, and
  proves config admission rather than runtime behavior.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the Legacy
  separation and pre-code setup packets were already frozen, and the next honest move was a
  reproducible config-admission proof rather than a runnable Legacy backtest.
- **Objective:** materialize one true Legacy 2024 setup carrier and prove that current
  schema/config-authority/family validation preserves the enabled router leaf without drifting the
  carrier into RI or hybrid identity.
- **Candidate:** `legacy 2024 policy-router control setup proof`
- **Base SHA:** `HEAD`

### Skill Usage

- **Invoked skills:** `config_authority_lifecycle_check` (primary, because this slice proves
  ConfigAuthority canonicalization on a Legacy carrier) and `python_engineering` (secondary, for
  the focused governance test implementation).
- **Not claimed:** no runtime, backtest, or launch skill coverage is claimed as completed by this
  packet.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
  - `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_precode_packet_2026-04-30.md`
  - `config/runtime.seed.json`
  - `tests/governance/test_config_schema_backcompat.py`
- **Candidate / comparison surface:**
  - `tmp/policy_router_evidence/legacy/tBTCUSD_3h_legacy_policy_router_2024_setup_carrier_20260430.json`
  - `tests/governance/test_legacy_policy_router_setup.py`
- **Vad ska förbättras:**
  - turn the Legacy setup question into one reproducible admission proof
  - lock explicit `authority_mode = legacy` rather than relying only on fallback defaults
  - prove that the enabled router leaf can remain on a true Legacy carrier
- **Vad får inte brytas / drifta:**
  - no `src/**` logic changes
  - no `config/**` edits or additions
  - no `results/**` materialization
  - no runtime or backtest claims
- **Reproducerbar evidens som måste finnas:**
  - the tmp carrier validates through `ConfigAuthority().validate(...)`
  - canonical output preserves the enabled router leaf
  - canonical output keeps `authority_mode = legacy`
  - family identity remains Legacy and does not pick up RI signature markers
  - a derived absent variant omits the router leaf canonically while remaining Legacy

## Why this slice exists now

The repo already contained the critical admission clues, but not yet one carrier-specific proof:

1. the separation packet already froze `RI absent != Legacy`
2. the setup pre-code packet already froze `2024` as the first discriminative Legacy control year
3. `tests/governance/test_config_schema_backcompat.py` already proved that
   `research_policy_router` is legal on `strategy_family = legacy`
4. `config/runtime.seed.json` already provided a stable true-Legacy base

This slice closes the remaining gap by materializing one explicit Legacy carrier and validating it
as Legacy with the router leaf present.

## Implemented files

- `tmp/policy_router_evidence/legacy/tBTCUSD_3h_legacy_policy_router_2024_setup_carrier_20260430.json`
  - tmp-only evidence carrier derived from Legacy seed defaults
  - explicit `strategy_family = legacy`
  - explicit `multi_timeframe.regime_intelligence.authority_mode = legacy`
  - explicit enabled `research_policy_router` leaf
  - explicit `warmup_bars = 120`
- `tests/governance/test_legacy_policy_router_setup.py`
  - validates enabled-leaf canonical retention on the new carrier
  - validates Legacy family identity and absence of RI signature drift
  - validates that a derived absent variant remains Legacy and canonically omits the leaf

## Scope

- **Scope IN:**
  - `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_implementation_packet_2026-04-30.md`
  - `tmp/policy_router_evidence/legacy/tBTCUSD_3h_legacy_policy_router_2024_setup_carrier_20260430.json`
  - `tests/governance/test_legacy_policy_router_setup.py`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - all `config/**` edits/additions
  - `results/**`
  - backtest execution
  - schema/authority/family logic changes
  - existing RI artifacts
- **Expected changed files:**
  - `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_implementation_packet_2026-04-30.md`
  - `tmp/policy_router_evidence/legacy/tBTCUSD_3h_legacy_policy_router_2024_setup_carrier_20260430.json`
  - `tests/governance/test_legacy_policy_router_setup.py`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `4`

## Gates required

The reduced gate path was sufficient for this config/test/docs-only slice:

1. `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_implementation_packet_2026-04-30.md tmp/policy_router_evidence/legacy/tBTCUSD_3h_legacy_policy_router_2024_setup_carrier_20260430.json tests/governance/test_legacy_policy_router_setup.py`
2. `pytest tests/governance/test_legacy_policy_router_setup.py`
3. `pytest tests/governance/test_config_schema_backcompat.py`

The full `test_config_schema_backcompat.py` file is used here deliberately so the cited
legacy-scoped `research_policy_router` proofs are exercised deterministically rather than through
an ambiguous selector.

## Verification outcome

This slice is only complete if the following are all true:

- the new tmp carrier validates canonically through `ConfigAuthority`
- the enabled router leaf is retained in canonical dump
- `validate_strategy_family_identity_config(...)` resolves the canonical carrier as `legacy`
- `has_ri_signature_markers(...)` remains false on the canonical carrier
- the derived absent variant remains Legacy and canonically omits the router leaf

## Stop Conditions

- the carrier drifts into `authority_mode = regime_module`
- the carrier picks up RI signature markers
- the slice widens into `config/**`, `results/**`, or `src/**`
- any step starts claiming runnable Legacy evidence from config admission alone

## Output required

- one tmp-only Legacy carrier artifact
- one focused governance proof file
- one updated working anchor
- this implementation packet

## Bottom line

The repository now has one explicit Legacy-only setup carrier proving that an enabled
`research_policy_router` leaf can survive canonical config validation while the carrier remains a
true Legacy config. That closes the setup-proof gap for the `2024` control line, but it still
does **not** authorize a runnable Legacy backtest by itself.
