# Regime Intelligence challenger family slice 2 — execution runbook

Date: 2026-03-18
Slice: `feature/ri-optuna-train-validate-blind-v1`
Status: `docs-only / prep-approved / execution not implied by this runbook alone`

## Purpose

This document defines the operational runbook for executing the RI challenger-family slice-2 campaign safely and reproducibly.

It is intentionally concrete, but it still does **not**:

- approve champion promotion
- approve default/cutover changes
- reinterpret the incumbent champion as deprecated

This runbook exists so the next actual campaign start can be done without storage reuse mistakes, scope drift, or command-surface improvisation.

## Reviewed execution provenance

The runbook is pinned to the currently reviewed slice state:

- branch: `feature/ri-optuna-train-validate-blind-v1`
- short SHA: `a801edc4`
- working tree requirement: clean
- canonical execution mode:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_FAST_HASH=0`
  - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
  - `GENESIS_RANDOM_SEED=42`
  - `PYTHONPATH=src`

If execution is later proposed from a successor SHA, the operator should first confirm that the runbook still matches the current optimizer YAML and governance packet.

## Canonical committed config for the real slice-2 run

Primary execution config:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml`

Governance references:

- `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice2_2026-03-18.md`
- `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice2_2026-03-18.md`

## Preconditions before the real run

All of the following must be true before starting the real slice-2 campaign:

1. working tree is clean
2. no committed `results/**` edits are pending
3. the canonical slice-2 storage path does **not** already exist when `resume=false`
4. the committed slice-2 YAML still points at:
   - study: `ri_challenger_family_slice2_3h_2024_v1`
   - storage: `results/hparam_search/storage/ri_challenger_family_slice2_3h_2024_v1.db`
5. canonical execution flags are set exactly as above
6. validator, preflight, and the focused governance anchors remain green

## Expected storage and result surfaces

The real slice-2 run should write to the committed canonical study path:

- storage DB:
  - `results/hparam_search/storage/ri_challenger_family_slice2_3h_2024_v1.db`

The optimizer should then create a new run directory under:

- `results/hparam_search/`

Expected result families to inspect after completion:

- `run_meta.json`
- `best_trial.json`
- validation trial JSONs under `validation/`
- logs for individual trials

## Required command order

### 1. Activate the project environment

```powershell
. .\.venv\Scripts\Activate.ps1
```

### 2. Set canonical execution flags

```powershell
$env:GENESIS_FAST_WINDOW='1'
$env:GENESIS_PRECOMPUTE_FEATURES='1'
$env:GENESIS_FAST_HASH='0'
$env:GENESIS_PREFLIGHT_FAST_HASH_STRICT='1'
$env:GENESIS_RANDOM_SEED='42'
$env:PYTHONPATH='src'
```

### 3. Run validator on the committed slice-2 YAML

```powershell
C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml
```

### 4. Run preflight on the committed slice-2 YAML

```powershell
C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml
```

### 5. If and only if preflight is green, start the real run

```powershell
C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m core.optimizer.runner config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml
```

## Temporary smoke path

If the operator wants to re-check bootability without touching committed `results/**`, use a temporary smoke config under `tmp/` and a unique temporary DB under `tmp/`.

Current reviewed smoke example:

- `tmp/tBTCUSD_3h_ri_challenger_family_slice2_smoke_20260318.yaml`

Rules for any future smoke rerun:

- smoke YAML must stay under `tmp/`
- smoke DB must stay under `tmp/`
- smoke study name must be unique
- smoke artifacts must not be committed as part of the slice

## Focused governance anchors to rerun before confidence claims

The following focused anchors are the minimum reviewed evidence bundle for this slice:

```powershell
python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py
python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py
python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable
python -m pytest -q tests/governance/test_authority_mode_resolver.py
```

These do **not** by themselves approve a champion promotion.
They only preserve the execution-confidence floor for this optimizer slice.

## What to record after the real run

Once the real slice-2 run completes, capture at least:

- exact run directory path under `results/hparam_search/`
- `run_meta.json` path
- `best_trial.json` path
- validation winner cluster summary
- whether the incumbent champion still leads or the challenger family improved
- whether any new blind-2025 follow-up is justified

## Stop conditions

Stop immediately and do **not** continue the real run if any of the following happens:

- preflight reports storage reuse with `resume=false`
- working tree is dirty in a way that affects scope or evidence clarity
- the committed slice-2 YAML has drifted from the reviewed packet/context map intent
- execution requires editing `src/**`, `tests/**`, `config/runtime.json`, or champion files
- someone tries to interpret slice-2 execution as automatic promotion authority
- a replacement storage path or study name is improvised without updating the evidence record

## Decision boundaries

This runbook supports only the following action:

- execute the RI challenger-family slice-2 campaign in canonical mode

It does **not** support these actions by itself:

- promote a new champion
- retire the incumbent champion
- change runtime defaults
- run blind-2025 candidate evaluation in the same step
- re-open the direct incumbent-overlay migration path

## Bottom line

If we choose to execute slice 2, the correct move is:

1. use the committed slice-2 YAML
2. run validator
3. run preflight
4. start the optimizer only if preflight is green
5. treat the output as challenger evidence, not automatic promotion evidence
