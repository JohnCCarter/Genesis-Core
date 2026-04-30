# Legacy policy-router surface-separation pre-code packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `pre-code-defined / docs-only / no implementation or execution authority`

This packet defines the minimum separation contract for any future Legacy policy-router
experiment surface.

It exists to prevent semantic and artifact mixing between:

- the already materialized RI-family `enabled` vs `absent` comparisons, and
- any future true Legacy-family control or enabled/absent comparison.

It does **not** authorize runtime changes, backtest execution, config/schema widening,
family-rule changes, new results, or promotion claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only and freezes naming, namespace, and identity
  guardrails before any future Legacy-surface probe is attempted.
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the current question is
  not whether Legacy policy-router behavior is good or bad, but how to prevent a future Legacy
  probe from being mislabeled as RI-off or mixed into existing RI artifacts.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** define one fail-closed documentation contract that keeps future Legacy
  policy-router evidence, outputs, and notes separate from the existing RI-family policy-router
  line.
- **Base SHA:** `HEAD`

### Constraints

- `docs-only`
- `concept-only / non-authorizing`
- `No runtime / config / schema / family-rule changes`
- `No new execution or result materialization`
- `No reinterpretation of current RI absent baseline as Legacy`

### Skill Usage

- **Applied repo-local skill:** none in this packet
- **Reason:** this slice only documents taxonomy, naming, and identity guardrails for a future
  Legacy experiment surface.
- **Reserved for any later runnable slice:** `decision_gate_debug`, `python_engineering`,
  `backtest_run`, `genesis_backtest_verify`
- **Not claimed:** no skill coverage is claimed as completed by this packet.

## Why this packet exists now

The current annual `enabled` vs `absent` probe does **not** answer a Legacy question.

The repo-visible evidence shows:

1. the carrier config used for the annual RI policy-router line is explicitly
   `strategy_family = "ri"`
2. that carrier also keeps `authority_mode = "regime_module"`
3. the `absent` branch in the annual probe removes only `multi_timeframe.research_policy_router`
4. therefore the current `absent` baseline is **RI without the router leaf**, not a true Legacy
   family surface

Without an explicit separation contract, a later Legacy probe could easily be mislabeled as “the
same thing as absent, just with a different folder name,” which would make future findings and
backtest outputs harder to trust.

## Evidence anchors

- `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- `tmp/policy_router_evidence/verify_router_enabled_vs_absent_all_years_20260428.py`
- `src/core/strategy/family_registry.py`
- `src/core/config/authority.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/ri_policy_router.py`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `GENESIS_WORKING_CONTRACT.md`

## Exact separation contract

### Current RI fact that must stay explicit

The existing annual `enabled` vs `absent` results belong to the RI-family line.

They must continue to be described as:

- `RI enabled`
- `RI absent`
- `RI-family / regime_module carrier`

They must **not** be relabeled as:

- `Legacy absent`
- `Legacy baseline`
- `cross-family control`

unless a future packet actually changes the tested surface.

### Future Legacy identity requirements

Any future Legacy policy-router probe must fail closed unless all of the following are true:

- `strategy_family == "legacy"`
- `authority_mode == "legacy"`
- the source config is recorded explicitly
- the run writes its outputs into Legacy-only namespaces

If any of those identity checks fail, the surface must be treated as non-Legacy and must not be
documented as a Legacy result.

### Namespace contract for future Legacy artifacts

If the user later opens a true Legacy slice, the preferred namespaces are:

- probe/config carriers: `tmp/policy_router_evidence/legacy/`
- backtest outputs: `results/backtests/legacy_policy_router_<subject>/`
- evaluation artifacts: `results/evaluation/legacy_policy_router_<subject>.json`
- analysis notes: `docs/analysis/legacy/policy_router/`
- decision packets / handoffs: `docs/decisions/legacy/policy_router/`

The purpose is not folder inflation.
The purpose is to keep cross-family meaning obvious when reading filenames, notes, and output
roots later.

### Manifest rule for future Legacy runs

Each future Legacy run should emit a small manifest that records at least:

- `experiment_surface: legacy_policy_router`
- `strategy_family: legacy`
- `authority_mode: legacy`
- `comparison_mode: enabled_vs_absent` or other exact pair label
- `source_config`
- `guard_assertions_passed: true`

This manifest rule is preserved here as a future guardrail only.
It is **not** implemented by this packet.

## Exact question preserved by this packet

This packet freezes the following question only:

> If the Legacy line is reopened, how do we guarantee that its configs, outputs, and docs stay
> visibly and semantically separate from the existing RI-family policy-router line?

This packet does **not** assume that a Legacy experiment is already approved or already worth
running.

## Scope

- **Scope IN:**
  - `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - explicit citation to current RI carrier/config evidence only
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `tmp/**`
  - runtime/config/schema changes
  - new Legacy execution or backtest materialization
- **Expected changed files:**
  - `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Mode proof

- **Why this mode applies:** branch mapping from `feature/*` resolves to `RESEARCH` per
  `docs/governance_mode.md`.
- **What RESEARCH allows here:** one small docs-only packet that preserves naming and output
  separation rules before any cross-family probe is attempted.
- **What remains forbidden here:** runtime execution, family-rule changes, schema/config changes,
  or claims that the current RI absent baseline already covers the Legacy question.
- **What would force a heavier path later:** any actual Legacy config creation, new execution
  script, backtest run, or family-sensitive runtime change.

## Gates required for this packet

Choose the minimum docs-only gates appropriate to the current scope:

1. `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
2. basic file diagnostics for both markdown files

No runtime-classified gates are required for this packet itself because it is docs-only and opens
no executable surface by itself.

## Stop Conditions

- the packet starts implying a Legacy run already exists
- the packet starts treating RI `absent` evidence as cross-family proof
- the packet widens into config creation, execution, or runtime-family semantics
- more than the two scoped docs files would need to change

## Output required

- one docs-only pre-code packet preserving Legacy-vs-RI separation rules
- one updated working anchor

## Bottom line

The current `absent` baseline remains an RI-family surface, not a Legacy surface. If the Legacy
question is reopened later, it must use separate namespaces, explicit identity assertions, and
Legacy-labeled notes from the first artifact onward. This packet preserves that boundary only; it
does not authorize any execution or runtime follow-up by itself.
