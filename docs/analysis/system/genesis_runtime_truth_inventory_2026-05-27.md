# Genesis-Core — runtime truth inventory

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base SHA anchor: `83d0771b`
Status: `completed / docs+artifact inventory / observational only`

## Purpose

This bounded slice freezes one branch-current runtime truth inventory for Genesis-Core.

The goal is not to prove new market edge.
The goal is to answer a simpler and more urgent question:

> what is actually active in the current runtime spine, what is runtime-support, and what appears to be compatibility or legacy surface rather than branch-current authority?

This slice is intended to reduce confusion before any larger cleanup, archive split, V2 extraction, or new optimizer work.

## Scope

### Scope IN

- current runtime SSOT and effective runtime snapshot
- active backtest/runtime execution spine
- active model and champion resolution paths
- active indicator families in current runtime-near paths
- schema-declared but currently null / disabled runtime surfaces
- explicit compatibility / legacy surfaces already marked as such in code
- one machine-readable inventory artifact

### Scope OUT

- runtime behavior changes
- removal or relocation of files
- V2 repository creation
- full dead-code deletion audit
- new backtests, Optuna runs, or feature generation
- authority changes in Phase 5 / Phase 6 Edge Topology docs

## Evidence inputs

- `config/runtime.json`
- `src/core/config/authority.py`
- `src/core/config/schema.py`
- `src/core/config/authority_mode_resolver.py`
- `src/core/strategy/family_registry.py`
- `scripts/run/run_backtest.py`
- `src/core/pipeline.py`
- `src/core/backtest/engine.py`
- `src/core/backtest/engine_precompute.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/features_asof.py`
- `src/core/strategy/decision.py`
- `src/core/intelligence/regime/authority.py`
- `src/core/strategy/regime.py`
- `src/core/strategy/model_registry.py`
- `src/core/strategy/champion_loader.py`
- `config/models/registry.json`
- `config/models/tAPTUSD_1h.json`
- `config/strategy/champions/tBTCUSD_1h.json`
- `config/strategy/champions/tBTCUSD_3h.json`
- `src/core/strategy/features.py`
- `src/core/config/validator.py`

## Emitted artifact

- `results/research/runtime_truth_inventory/genesis_runtime_truth_inventory_2026-05-27.json`

## Observed

### 1. Current runtime SSOT is still the config-authority path and the loaded snapshot is legacy-shaped

The current runtime SSOT remains:

- `config/runtime.json`
- loaded and validated through `ConfigAuthority`

Current observed snapshot facts:

- runtime version = `630`
- `strategy_family = legacy`
- `multi_timeframe.regime_intelligence.authority_mode = legacy`
- `features = null`
- `htf_fib = null`
- `ltf_fib = null`
- `research_bull_high_persistence_override.enabled = false`
- `research_current_atr_high_vol_multiplier_override.enabled = false`

So the current runtime snapshot is not a branch-current RI authority snapshot.
It is a legacy-family runtime with selective multi-timeframe and risk controls enabled.

### 2. The active execution spine is already fairly clear

The current runtime-near / backtest-near execution spine is:

1. `scripts/run/run_backtest.py`
2. `ConfigAuthority.get()` loads runtime
3. `GenesisPipeline.setup_environment()` enforces canonical mode defaults unless explicit override
4. `GenesisPipeline.create_backtest_engine()` creates `BacktestEngine`
5. `BacktestEngine.run()` evaluates bar-by-bar through `evaluate_pipeline`
6. `evaluate.py` resolves config/champion behavior, extracts features, detects regime, loads model metadata, computes confidence, and delegates into `decision.py`

That means the branch already has one dominant runtime spine.
The main confusion is not “which spine exists,” but “which surrounding surfaces are truly authoritative versus merely present.”

### 3. Current family and regime authority are both legacy on the observed runtime snapshot

The family registry and authority resolver make the current branch state quite explicit:

- `strategy_family = legacy`
- `authority_mode = legacy`

`evaluate.py` then resolves the authoritative regime path accordingly:

- legacy authority path -> intelligence authority delegates with fallback through `regime_unified.detect_regime_unified`
- `regime.py` still exists as a shadow / alternative regime surface, but it is not the active authority on the current snapshot

So the current branch is **not** running an RI-primary authority shape by default.

### 4. Current model and champion resolution are active runtime surfaces, not dead paperwork

Model path:

- `predict_proba_for()` loads model metadata through `ModelRegistry`
- `ModelRegistry` resolves champion model files from `config/models/registry.json`
- sample model schemas still expose live feature names such as:
  - `rsi_inv_lag1`
  - `bb_position_inv_ma3`
  - `rsi_vol_interaction`

Champion path:

- `ChampionLoader` resolves timeframe champions from `config/strategy/champions/*.json`
- `evaluate.py` merges champion config unless explicit backtest config bypasses champion merge
- `run_backtest.py` merges runtime config unless a complete champion file provides `merged_config`

Observed champion state is mixed rather than uniformly fresh:

- `tBTCUSD_1h.json` is a legacy-family paper-trading champion from `2026-02-03`
- `tBTCUSD_3h.json` is an explicit bootstrap champion whose own metadata says Optuna/backtest follow-up is still recommended

So models and champions are active, but not necessarily uniformly recent or equally validated.

### 5. A non-trivial indicator stack is still active in runtime-near code

The current runtime-near feature and precompute path directly uses:

- `ATR`
- `EMA`
- `RSI`
- `Bollinger`
- `ADX`
- `Fibonacci`
- HTF Fibonacci mapping / context
- exit Fibonacci levels

This is visible in:

- `features_asof.py`
- `engine_precompute.py`
- `engine.py`
- `regime.py`

So the system has **not** been reduced to a tiny indicator-free shell.
Several of the indicators the repo has accumulated are still materially active in the runtime-support path.

### 6. Some declared surfaces are present in schema but are not currently active in the observed runtime snapshot

These are especially important because they create confusion if presence is mistaken for activity.

Currently schema-declared but null / absent / disabled on the loaded runtime snapshot include:

- `features`
- `htf_fib`
- `ltf_fib`
- research override surfaces that remain disabled
- optional research policy-router surface not present in the active canonical runtime payload

So “declared in schema” is not the same thing as “active in current runtime.”

### 7. Some code surfaces are explicitly compatibility / legacy layers rather than current SSOT

Two examples are already marked in code as non-authoritative compatibility surfaces:

- `src/core/strategy/features.py`
  - legacy compatibility shim that delegates to `features_asof`
- `src/core/config/validator.py`
  - legacy schema-v1 helper, explicitly not runtime-config authority

These are useful to keep for compatibility or tests, but they should not be confused with branch-current SSOT runtime surfaces.

### 8. A few indicator/helper surfaces appear present but were not observed on the active spine in this slice

This slice did **not** observe a strong active-runtime path for:

- `MACD` beyond vectorized helper code
- generic SMA helpers outside the indicator implementations that depend on them internally
- volume SMA as a core active runtime decision feature

That does **not** prove they are dead code.
It only means they were not observed as part of the current dominant runtime spine in this bounded inventory.

## Inferred

### 1. The current branch already has one dominant runtime truth, but it is buried under too many adjacent surfaces

The main problem is not total architectural chaos.
The runtime spine is visible.
The real problem is that the repo contains too many nearby:

- research surfaces
- compatibility layers
- optional schema surfaces
- legacy helpers
- stale-ish optimizer/champion clues

So the next useful step is classification, not more undirected proof generation.

### 2. Current Genesis is still a legacy-family system with a meaningful indicator stack

The branch-current system is not “just RI now,” and it is not “just a bare ML shell.”
It is still a legacy-family runtime that materially uses indicator-driven feature extraction, regime handling, model lookup, champion resolution, and Fibonacci-aware logic.

### 3. Any future V2 or archive split should be built from runtime truth, not from historical commits alone

Because the current spine is already identifiable, a future V2 can be built from:

- active runtime
- runtime support
- optional-but-currently-null surfaces
- compatibility / legacy
- present-but-not-observed-active

That is a stronger extraction basis than broad cherry-picking.

## Unverified

- whether paper/live API entrypoints differ materially from the currently inspected backtest/runtime spine
- whether every symbol/timeframe champion and model file is equally current or valid
- whether currently unobserved helpers such as MACD become active in specific niche flows not inspected in this slice
- whether the current legacy authority snapshot is the intended product target or simply the current temporary state

## Inventory summary

### Active runtime surfaces

- runtime SSOT: `config/runtime.json` via `ConfigAuthority`
- execution spine: `run_backtest.py` -> `pipeline.py` -> `BacktestEngine` -> `evaluate.py` -> `decision.py`
- feature SSOT: `features_asof.py`
- active family/authority on current snapshot: `legacy` / `legacy`
- model resolution: `ModelRegistry`
- champion resolution: `ChampionLoader`
- active indicator families observed: `ATR`, `EMA`, `RSI`, `Bollinger`, `ADX`, `Fibonacci`

### Runtime-support surfaces

- precompute and on-disk cache path in `engine_precompute.py` / `engine.py`
- HTF Fibonacci mapping/context support
- exit Fibonacci path
- merge policies for runtime/champion resolution

### Declared but currently null / disabled on runtime snapshot

- `features`
- `htf_fib`
- `ltf_fib`
- multiple research override surfaces

### Compatibility / legacy surfaces

- `core.strategy.features`
- `core.config.validator`
- non-authoritative regime alternatives outside the current legacy authority path

### Present but not observed active in this slice

- `MACD` helper surfaces
- generic SMA helper surfaces outside the indicator implementations that already embed them
- volume SMA as a dominant runtime decision feature

## Consequence

The repo is now at the point where a small classification pass can likely unlock more value than more generalized docs layering.

The best immediate uses of this inventory are:

1. define `keep / move / archive / legacy / maybe` buckets
2. clarify what belongs in a future `Genesis-Core-V2`
3. avoid running new Optuna work against a misunderstood runtime spine

## What changed and what did not

What changed:

- the branch now has one bounded runtime truth inventory note
- the current active runtime spine is now frozen in one place
- active vs compatibility vs optional-null surfaces are now explicitly separated

What did **not** change:

- no runtime behavior changed
- no cleanup or archive move happened yet
- no V2 repo was created
- no indicators or configs were removed
- the locally modified Edge Topology docs and locally modified research JSON files were left untouched by this slice
