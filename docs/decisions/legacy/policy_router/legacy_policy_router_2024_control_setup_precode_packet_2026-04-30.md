# Legacy policy-router 2024 control setup pre-code packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `pre-code-defined / docs-only / setup-only / no implementation or execution authority`

This packet defines the first bounded setup question for a true Legacy-family policy-router
control line.

It does **not** authorize runtime changes, config creation, backtest execution, working-tree
materialization, new result files, or cross-family promotion claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only and freezes the first truthful Legacy-2024
  setup question before any config, run, or output surface is created.
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the repository already has
  a Legacy-vs-RI separation packet, but the next honest move is still to define whether a true
  Legacy config can carry the router leaf without becoming RI or hybrid before any runnable slice
  is proposed.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** preserve the first exact Legacy setup/control question on the strongest annual
  contrast year (`2024`) while keeping runtime, config, and result surfaces unchanged.
- **Candidate:** `legacy 2024 policy-router control setup`
- **Base SHA:** `HEAD`

### Constraints

- `docs-only`
- `setup-only / non-authorizing`
- `No runtime / config / schema / family-rule changes`
- `No new execution or result materialization`
- `No claim that a Legacy router run is already admissible`

### Skill Usage

- **Applied repo-local skill:** none in this packet
- **Reason:** this slice only freezes the next bounded setup question and does not execute a
  debugging, implementation, or backtest workflow.
- **Reserved for any later runnable slice:** `decision_gate_debug`, `python_engineering`,
  `backtest_run`, `genesis_backtest_verify`, `config_authority_lifecycle_check`
- **Not claimed:** no skill coverage is claimed as completed by this packet.

## Why this packet exists now

The current repo-visible evidence already locks three truths:

1. the annual `enabled` vs `absent` probe is an **RI-family** line, not a Legacy line
2. `2024` is the clearest first control year because the RI annual note records it as a negative
   enabled year while the same annual summary shows the `absent` branch as the strongest full-year
   raw return on that surface (`633.901347%`)
3. before any future Legacy run can be honest, the repository must prove that the candidate config
   remains a true Legacy config instead of drifting into `regime_module` or RI-signature territory

This packet therefore preserves the correct next question:
not “run Legacy now,” but “define the exact setup proof for the first true Legacy 2024 control.”

## Evidence anchors

- `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/enabled_vs_absent_all_years_summary.json`
- `src/core/strategy/family_registry.py`
- `src/core/config/schema.py`
- `src/core/config/authority.py`
- `GENESIS_WORKING_CONTRACT.md`

## Exact setup question preserved by this packet

This packet freezes the following question only:

> Can the repository construct one true Legacy-family 2024 control carrier that keeps
> `strategy_family = legacy`, keeps `authority_mode = legacy`, avoids RI signature markers, and
> still carries `multi_timeframe.research_policy_router` as a bounded test leaf for a later
> paired Legacy `enabled` vs `absent` run?

This packet does **not** assume the answer is yes.
It only preserves that this is now the smallest honest Legacy follow-up.

## Exact setup boundary

### Current RI fact that must stay explicit

The existing annual `enabled` vs `absent` evidence remains:

- `strategy_family = ri`
- `authority_mode = regime_module`
- `absent = same RI carrier with research_policy_router removed`

That line must **not** be relabeled as Legacy by implication, shorthand, or filename drift.

### Legacy config-admission facts already visible in the repo

Current repo-visible schema and validation surfaces show:

- `RuntimeConfig` includes `multi_timeframe.research_policy_router` as a legal optional leaf
- `RuntimeConfig.model_dump_canonical()` preserves that leaf only when it is enabled
- config-authority whitelist handling explicitly permits the router leaf and its current bounded
  fields
- `family_registry.py` requires a true Legacy config to keep `authority_mode != regime_module`
  and to avoid RI signature markers

Therefore the next truthful Legacy step is a **setup proof**, not a backtest claim.

### Why `2024` is the first Legacy control year

`2024` is the sharpest first discriminative surface because:

- the curated RI annual note already marks `2024` as a negative full year for the enabled router
  leaf
- the same annual summary records the RI `absent` branch as the strongest full-year raw return on
  that annual surface (`633.901347%` final PnL-equivalent delta over initial capital; raw return
  `633.901347%`)

That makes `2024` the right first place to ask whether the observed regression is:

- router-general, or
- RI-carrier-specific

### Future runnable subject if setup proof succeeds later

If a later slice proves a true Legacy carrier is admissible, the first preferred paired subject
should stay tightly aligned with the existing annual surface:

- symbol: `tBTCUSD`
- timeframe: `3h`
- window: `2024-01-01 .. 2024-12-31`
- data-source policy: `curated_only`
- warmup: `120`
- comparison: Legacy `enabled` vs Legacy `absent`

This future runnable subject is preserved here as a planning target only.
It is **not** authorized by this packet.

## What this packet explicitly forbids

This packet must not be read as authority for any of the following:

- creating a Legacy config that silently uses `authority_mode = regime_module`
- creating a “Legacy” carrier that inherits RI threshold/gate signature markers
- treating the current RI `absent` annual result as if it were already the Legacy control answer
- opening a dedicated Legacy working tree before a true runnable slice exists
- materializing `tmp/`, `results/`, or `config/` artifacts for Legacy execution from this packet
  alone

## Preferred next bounded follow-up if this line is reopened

If the user explicitly wants to continue this line after this packet, the cleanest next step is:

- one setup-only slice that materializes a candidate Legacy carrier config and proves, via current
  schema/config-authority/family validation, that it remains Legacy-typed while carrying the
  router leaf

What is **not** admissible from this packet alone:

- a paired backtest run
- new results/evaluation outputs
- a runtime packet
- a working-tree launch for execution

## Scope

- **Scope IN:**
  - `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_precode_packet_2026-04-30.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - explicit citation to current RI annual evidence plus repo-visible Legacy config-admission seams
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `tmp/**`
  - runtime/config/schema changes
  - Legacy carrier creation
  - Legacy backtest execution
- **Expected changed files:**
  - `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_precode_packet_2026-04-30.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Mode proof

- **Why this mode applies:** branch mapping from `feature/*` resolves to `RESEARCH` per
  `docs/governance_mode.md`.
- **What RESEARCH allows here:** one small docs-only setup packet that preserves the next Legacy
  control question without opening runtime/default/config authority.
- **What remains forbidden here:** config creation, backtest execution, family-rule changes,
  output materialization, or relabeling RI evidence as Legacy proof.
- **What would force a heavier path later:** any actual Legacy config materialization, validation
  harness, backtest run, or execution-only working tree.

## Gates required for this packet

Choose the minimum docs-only gates appropriate to the current scope:

1. `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_precode_packet_2026-04-30.md`
2. basic file diagnostics for both markdown files

No runtime-classified gates are required for this packet itself because it is docs-only and opens
no executable surface by itself.

## Stop Conditions

- the packet starts implying a runnable Legacy 2024 subject already exists
- the packet starts assuming the router leaf is automatically admissible on Legacy without a
  setup proof
- the packet widens into config creation, execution, or output paths
- more than the two scoped docs files would need to change

## Output required

- one setup-only pre-code packet for the first Legacy 2024 control question
- one updated working anchor

## Bottom line

`2024` is the correct first year for a true Legacy control question, but the repository still
needs an explicit setup proof before any Legacy-enabled vs Legacy-absent run is honest. This
packet preserves that setup boundary only; it does not authorize config creation, execution, or
working-tree materialization by itself.
