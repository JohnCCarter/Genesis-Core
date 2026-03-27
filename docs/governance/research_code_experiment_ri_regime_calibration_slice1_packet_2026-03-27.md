# Research code experiment RI regime calibration slice 1 packet

Date: 2026-03-27
Status: tracked / packet-open / bounded code-level research
Lane: `run_intent: research_code_experiment`
Phase: `2 - RI internal research track`
Slice: `ri regime calibration slice 1`

## Exact hypothesis

- The current RI path falls back to default calibration when the authoritative regime is `balanced`.
- This slice tests one narrow alternate mapping: allow `balanced` to use an explicit RI research-only calibration entry instead of the current default-calibration fallback.

## Exact bounded code surface

- `src/core/strategy/evaluate.py`
- `src/core/strategy/prob_model.py`

## Isolated research-only metadata path

- `config/research/model_meta/ri_regime_calibration_slice1/tBTCUSD_3h.json`

## Allowed work

- one opt-in pass-through seam from runtime config metadata into `predict_proba_for(...)`
- one research-only metadata loader for isolated model metadata outside active production paths
- one research-only metadata file for the exact RI slice hypothesis
- only the minimum tests needed to prove:
  - default behavior is unchanged
  - the opt-in research path is isolated
  - active production model paths are rejected for research override use

## Forbidden work

- `family_registry` or family-admission semantics
- champions
- runtime defaults
- active `config/models/**` writeback
- threshold, exit, override, fib, sizing, `risk_state`, or `clarity` reopening
- Legacy or coordination surfaces

## Minimum evidence package

- targeted integration proof that default evaluation path remains unchanged when no research override is present
- targeted proof that `run_intent: research_code_experiment` can pass an isolated metadata path into the probability layer
- targeted proof that active `config/models/**` paths are rejected
- replay and pipeline-hash drift guard remain green

## Stop conditions

- stop if the seam needs to touch family rules, champions, runtime defaults, or active production model metadata paths
- stop if the change requires broader decision-surface reopening beyond calibration
- stop if the research override path cannot remain explicit and opt-in
- fail closed on ambiguity
