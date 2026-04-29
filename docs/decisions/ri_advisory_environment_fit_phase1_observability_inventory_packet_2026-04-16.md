# RI advisory environment-fit Phase 1 observability inventory packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / observability inventory / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only inventory of already tracked RI observability surfaces; no execution, no artifact regeneration, no runtime/config/test changes.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** inventory the already existing `ri` observability surfaces relevant to the advisory environment-fit roadmap and state plainly which advisory dimensions are already observable, partially observable, or still missing.
- **Candidate:** `RI advisory environment-fit Phase 1 observability inventory`
- **Base SHA:** `45fecbeb`

### Scope

- **Scope IN:**
  - `docs/decisions/ri_advisory_environment_fit_phase1_observability_inventory_packet_2026-04-16.md`
  - `docs/analysis/ri_advisory_environment_fit_phase1_observability_inventory_2026-04-16.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - `artifacts/**`
  - any runtime/default/config-authority change
  - any new advisory scoring formula
  - any ML/model work
  - any execution or replay run
- **Expected changed files:**
  - `docs/decisions/ri_advisory_environment_fit_phase1_observability_inventory_packet_2026-04-16.md`
  - `docs/analysis/ri_advisory_environment_fit_phase1_observability_inventory_2026-04-16.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/ri_advisory_environment_fit_phase1_observability_inventory_packet_2026-04-16.md docs/analysis/ri_advisory_environment_fit_phase1_observability_inventory_2026-04-16.md`

### Stop Conditions

- any drift into runtime implementation, config changes, or advisory formula authoring
- any wording that upgrades this slice into a launch, shadow-runtime, or promotion packet
- any silent cross-family extension beyond `ri`
- any attempt to treat post-entry research labels as already available scoring-time observability
- any attempt to open the ML comparator lane from this packet alone

### Output required

- one docs-only packet
- one compact inventory memo
- one explicit mapping of current RI observability fields to candidate advisory roles
- one explicit missing-dimensions section

## Purpose

This slice exists to answer one narrow question only:

> What RI-specific observability surfaces already exist in tracked code today that can support a later advisory environment-fit lane without changing default behavior?

This slice does **not** decide:

- what the final advisory score formula should be
- whether any advisory score should enter runtime
- whether ML is justified
- whether any implementation slice should open immediately after this memo

## Allowed evidence inputs

This slice may cite only already tracked source and docs surfaces needed for the inventory:

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `src/core/intelligence/regime/clarity.py`
- `src/core/intelligence/regime/risk_state.py`
- `src/core/intelligence/regime/contracts.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`

No replay artifact or regenerated output is required for this inventory slice.

## Interpretation rules

The memo produced by this packet must keep the following distinctions explicit:

1. **already observable today**
2. **partially observable via proxies or decomposed fields**
3. **missing and not yet implemented**

The memo must also separate:

- observability fields that exist only in state/meta payloads
- fields that already affect RI sizing
- family/governance guardrails that constrain the lane but are not themselves advisory signals

## Required questions

The inventory memo must answer at minimum:

1. What current RI observability already describes confidence / clarity?
2. What current RI observability already describes transition risk?
3. What current RI observability already describes authoritative-vs-shadow regime disagreement?
4. What candidate advisory outputs are already partially decomposed but not unified?
5. What still does **not** exist yet for:
   - `transition_risk_score`
   - `decision_reliability_score`
   - `market_fit_score`

## Non-authorizations

This packet does **not** authorize:

- code changes
- config changes
- label definition
- deterministic advisory baseline implementation
- ML comparator work
- shadow runtime integration

Those belong to later bounded slices, if the inventory result supports continuing.

## Exact next admissible step

If the inventory memo shows that enough RI observability exists to define labels cleanly, the next admissible step is:

- a separate bounded Phase 2 label-definition / failure-taxonomy slice

If the inventory memo shows the lane is still too underspecified even at the observability level, the next admissible step is:

- stop or reopen the roadmap with a narrower framing note only

## Bottom line

This packet authorizes one docs-only Phase 1 inventory memo and nothing more.
Its job is to convert the already observed RI surfaces into a clear ledger of:

- usable inputs
- partial proxies
- missing dimensions

without changing code, defaults, or runtime authority.
