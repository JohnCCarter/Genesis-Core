# RI advisory environment-fit — Phase 3 strategy-family bridge admissibility

This memo is docs-only and fail-closed.
It resolves the blocker exposed by the failed Phase C carrier-materialization slice:
`phaseC_oos_trial.json` cannot be copied unchanged into a runtime-valid carrier because its donor `merged_config` lacks `strategy_family`.

Governance packet: `docs/governance/ri_advisory_environment_fit_phase3_strategy_family_bridge_admissibility_packet_2026-04-17.md`

## Source surface used

- `docs/governance/ri_advisory_environment_fit_phase3_phaseC_carrier_materialization_packet_2026-04-16.md`
- `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
- `src/core/config/authority.py`
- `src/core/config/schema.py`
- `src/core/strategy/family_registry.py`
- `tests/governance/test_config_ssot.py`

## Decision question

May the roadmap open a future bounded slice that adds `strategy_family` to donor `cfg` solely to satisfy runtime validation and create a runtime-valid RI carrier?

## Short answer

**No — not under the current `NO BEHAVIOR CHANGE` contract.**

In this repository, `strategy_family` is runtime identity, not decorative metadata.
Adding it to the donor `cfg` would be semantic authoring, not neutral carrier materialization.

## Why the failed slice matters

The blocked Phase C packet already proved the key fact:

- exact donor copy passed the inertness idea,
- exact donor copy failed runtime validation,
- the first failing reason was `strategy_family` missing.

That narrows the question from "can we copy the donor?" to the more precise governance question:

> does adding `strategy_family` merely preserve already-implied identity, or does it author new executable semantics?

## Repository evidence: `strategy_family` is executable identity

### 1. Runtime schema makes `strategy_family` mandatory

`src/core/config/schema.py` declares `strategy_family: Literal["legacy", "ri"]` on `RuntimeConfig`.
That means runtime validation does not treat the field as optional provenance.
It is part of the executable config contract.

### 2. Config authority only backfills missing family for legacy backcompat

`src/core/config/authority.py` normalizes missing `strategy_family` only through a narrow backcompat path for legacy-shaped configs.
For non-legacy signatures, the path fails closed with `missing_strategy_family_backcompat_requires_legacy_signature`.

That is the opposite of a general-purpose “safe inference” rule.
It is a tightly bounded exception.

### 3. Family registry treats it as semantic identity

`src/core/strategy/family_registry.py` makes `strategy_family` mandatory for both supported families.
For RI, validation is coupled to canonical RI semantics:

- `authority_mode = regime_module`
- `atr_period = 14`
- canonical hysteresis/cooldown gates
- canonical RI threshold cluster

So adding `strategy_family: ri` does more than label provenance.
It activates a specific identity/validation contract.

### 4. The repository exposes explicit authoring helpers

The same file exposes `inject_strategy_family(config)`.
That helper exists precisely because adding the field is an authoring action.
If the field were inert metadata, a dedicated injection helper would not be needed.

## Consequence for the Phase C donor

`phaseC_oos_trial.json` may well *look* RI-shaped.
But once the lane needs runtime-valid standalone `cfg`, the repository requires explicit family identity.

Under the current slice constraints, the following two requirements cannot both hold:

1. `cfg` stays exactly equal to donor `merged_config`
2. `cfg` becomes runtime-valid through `ConfigAuthority`

The only known way to reconcile them is to author `strategy_family` into `cfg`.
That is not neutral copying.
That is semantic bridge authoring.

## Admissibility verdict

A future slice that injects `strategy_family` into donor `cfg` is **not admissible as materialization-only work** under the current `NO BEHAVIOR CHANGE` framing.
That is a statement about the present contract, not a claim that such bridge authoring is permanently forbidden in every future governance context.

If such a slice is ever proposed, it must be described honestly as one of the following:

- a semantic bridge-authoring slice with explicit governance exception, or
- a rejected idea if the lane insists on pure materialization semantics.

## What is still admissible now

The next admissible step is **not** runtime-valid bridge implementation.
The next admissible step is one of these:

1. **docs-only non-runtime namespace decision**
   - decide whether the donor should be preserved as a fixed research reference in a clearly non-runtime artifact surface
   - this path may use research-ledger / evidence semantics, but must not pretend to create a runtime-valid carrier
2. **lane close**
   - if the roadmap truly requires a runtime-valid fixed carrier and no non-authoring bridge exists, the honest outcome is to stop

## What should not happen next

- no silent use of `inject_strategy_family(...)` under a “materialization” label
- no claim that `strategy_family` is merely descriptive for runtime config
- no reopening of capture v2 on a bridge-authored artifact as if the blocker were already neutralized
- no baseline opening

## Bottom line

The failed Phase C slice did useful work: it proved that the remaining gap is not inert packaging but **config identity authoring**.

That means the roadmap should now branch explicitly:

- either open a docs-only decision on a **non-runtime evidence namespace**, or
- close the lane rather than smuggling semantic authoring into a supposedly neutral carrier step.

Under the current contract, runtime-valid `strategy_family` bridge authoring is **not** the next admissible move.
