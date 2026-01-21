# Runtime Reality Map - Genesis-Core
**Focus: Backtest + Optuna Execution Paths**

**Generated:** 2026-01-21  
**Repository:** JohnCCarter/Genesis-Core  
**Purpose:** Complete causal chain mapping from parameters to PnL, identifying dead code and semantic drift risks

---

## Table of Contents
1. [A) Entry Points & Runtime Module Map](#a-entry-points--runtime-module-map)
2. [B) Causal Chain: Param → Signal → Decision → Order → Fill → PnL → Metric → Objective](#b-causal-chain)
3. [C) Parameters That Don't Affect Outcomes](#c-parameters-that-dont-affect-outcomes)
4. [D) Dead/Legacy Code Analysis](#d-deadlegacy-code-analysis)
5. [E) Golden Trace Tests](#e-golden-trace-tests)

---

## A) Entry Points & Runtime Module Map

### Primary Entry Points

| Entry Point | Type | Purpose | Primary Modules Used |
|-------------|------|---------|---------------------|
| `scripts/run_backtest.py` | CLI | Manual backtest execution | `pipeline`, `engine`, `strategy`, `metrics` |
| `scripts/run_optimizer_smoke.py` | CLI | Quick Optuna smoke test | `optimizer.runner` |
| `src/core/optimizer/runner.py::run_optimizer()` | Python API | Full Optuna optimization | `optimizer.*`, `backtest.*`, `strategy.*` |
| `scripts/optimizer.py` | CLI | Post-run analysis (NOT execution) | Results analysis only |
| `pytest tests/` | Test Suite | Integration/unit tests | Various test fixtures |

### Core Module Categories & Usage Status

| Module | Path | Used in Backtest | Used in Optuna | Status |
|--------|------|------------------|----------------|--------|
| **Pipeline** | `src/core/pipeline.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Backtest Engine** | `src/core/backtest/engine.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Position Tracker** | `src/core/backtest/position_tracker.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Strategy Evaluate** | `src/core/strategy/evaluate.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Features (AsOf)** | `src/core/strategy/features_asof.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Decision** | `src/core/strategy/decision.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Confidence** | `src/core/strategy/confidence.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Prob Model** | `src/core/strategy/prob_model.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Regime Unified** | `src/core/strategy/regime_unified.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **HTF Exit Engine** | `src/core/backtest/htf_exit_engine.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Metrics** | `src/core/backtest/metrics.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Scoring** | `src/core/optimizer/scoring.py` | ❌ No | ✅ Primary | **CRITICAL (Optuna)** |
| **Constraints** | `src/core/optimizer/constraints.py` | ❌ No | ✅ Primary | **CRITICAL (Optuna)** |
| **Champion Manager** | `src/core/optimizer/champion.py` | ❌ No | ✅ Primary | **CRITICAL (Optuna)** |
| **Param Transforms** | `src/core/optimizer/param_transforms.py` | ❌ No | ✅ Primary | **CRITICAL (Optuna)** |
| **Indicators** | `src/core/indicators/*.py` | ✅ Primary | ✅ Primary | **CRITICAL** |
| **Config Authority** | `src/core/config/authority.py` | ✅ Used | ✅ Used | **ACTIVE** |
| **Observability** | `src/core/observability/metrics.py` | ⚠️ Optional | ⚠️ Optional | **OPTIONAL** |
| **ML Module** | `src/core/ml/*.py` | ❌ No | ❌ No | **LEGACY/DEAD** |
| **Symbols** | `src/core/symbols/symbols.py` | ❌ No | ❌ No | **LEGACY/DEAD** |
| **IO/Bitfinex** | `src/core/io/bitfinex/*.py` | ❌ No | ❌ No | **SERVER ONLY** |
| **Server** | `src/core/server.py` | ❌ No | ❌ No | **SERVER ONLY** |
| **Governance** | `src/core/governance/*.py` | ❌ No | ❌ No | **REGISTRY ONLY** |

---

## B) Causal Chain

### Complete Optuna Causal Chain: Param → Signal → Decision → Order → Fill → PnL → Metric → Objective

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: PARAMETER SUGGESTION                                           │
│ File: src/core/optimizer/runner.py                                      │
└─────────────────────────────────────────────────────────────────────────┘
    ↓
    [FUNCTION] objective(trial) - Line 2464
    ↓
    [FUNCTION] _suggest_parameters(trial, parameters_spec) - Line 2246
    ├─ RECURSIVELY suggests parameters via Optuna API:
    │  ├─ trial.suggest_categorical(name, choices)  # For grids
    │  ├─ trial.suggest_float(name, low, high)      # For continuous
    │  ├─ trial.suggest_int(name, low, high)        # For integers
    │  └─ trial.suggest_float(..., log=True)        # For loguniform
    │
    └─ Returns: dict[str, Any] "parameters"
       Example: {
         "thresholds.entry_conf_overall": 0.24,
         "thresholds.signal_adaptation.zones.low.entry_conf_overall": 0.22,
         "risk.risk_map_deltas.conf_0.size": -0.30,
         "htf_fib.enabled": True,
         ...
       }

    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: PARAMETER TRANSFORMATION                                       │
│ File: src/core/optimizer/param_transforms.py                            │
└─────────────────────────────────────────────────────────────────────────┘
    ↓
    [FUNCTION] transform_parameters(parameters) - Line 13
    ├─ Expands dot-notation keys (e.g., "risk.max_leverage" → nested dict)
    ├─ Applies derived value calculations:
    │  ├─ Constructs risk_map from deltas (conf_0, conf_1, conf_2 points)
    │  └─ Calculates signal_adaptation zone ranges from base + deltas
    │
    └─ Returns: (transformed_params, derived_values)
       Output: {
         "thresholds": {
           "entry_conf_overall": 0.24,
           "signal_adaptation": {"zones": {"low": {...}, "mid": {...}, "high": {...}}}
         },
         "risk": {
           "risk_map": [
             {"confidence": 0.0, "size_pct": 0.02},
             {"confidence": 0.5, "size_pct": 0.04},
             {"confidence": 0.8, "size_pct": 0.06}
           ]
         },
         "htf_fib": {"enabled": true, ...}
       }

    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: CONFIG MERGE & BACKTEST EXECUTION                              │
│ Files: src/core/optimizer/runner.py, src/core/pipeline.py               │
└─────────────────────────────────────────────────────────────────────────┘
    ↓
    [FUNCTION] make_trial(trial_number, parameters) - Callback in objective
    ├─ Merges transformed params into base runtime config
    ├─ Saves merged config to trial_<id>_config.json
    └─ Calls: run_trial(trial_cfg, ...) - Line 1613
       ↓
       [FUNCTION] _run_backtest_direct(trial, config_file) - Line 1304
       ├─ GenesisPipeline().setup_environment(seed=42)
       ├─ engine = GenesisPipeline().create_engine(symbol, timeframe, ...)
       ├─ engine.load_data()  # Load candles + precompute features
       └─ results = engine.run(policy, configs, ...)
          ↓
          ENTERS BACKTEST ENGINE LOOP (see Backtest Chain below)

    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: BAR-BY-BAR EXECUTION (Backtest Engine Loop)                    │
│ File: src/core/backtest/engine.py                                       │
└─────────────────────────────────────────────────────────────────────────┘
    ↓
    [FUNCTION] BacktestEngine.run() - Line 630
    ├─ Initialize: position_tracker, state, HTF exit engine
    └─ FOR each bar i in range(warmup_bars, num_bars):
       ↓
       [BUILD WINDOW]
       candles_window = _build_candles_window(i)  # Last N bars (OHLCV)
       configs["_global_index"] = i  # For precompute feature lookup
       
       ↓
       ┌────────────────────────────────────────────────────────────────┐
       │ STAGE 5: FEATURE EXTRACTION                                    │
       │ File: src/core/strategy/features_asof.py                       │
       └────────────────────────────────────────────────────────────────┘
       ↓
       [FUNCTION] evaluate_pipeline(candles, policy, configs, state)
       ├─ extract_features(candles, configs, state) - Line 152
       │  ├─ IF precomputed_features available:
       │  │  └─ Lookup features from configs["precomputed_features"][i]
       │  ├─ ELSE compute on-demand:
       │  │  ├─ atr_14 = calculate_atr(highs, lows, closes, period=14)
       │  │  ├─ atr_50 = calculate_atr(highs, lows, closes, period=50)
       │  │  ├─ ema_20 = calculate_ema(closes, period=20)
       │  │  ├─ ema_50 = calculate_ema(closes, period=50)
       │  │  ├─ rsi_14 = calculate_rsi(closes, period=14)
       │  │  ├─ bb_position_20_2 = bollinger_bands(closes, period=20, std=2)
       │  │  ├─ adx_14 = calculate_adx(highs, lows, closes, period=14)
       │  │  └─ fib_swings = detect_swing_points(highs, lows, ...)
       │  └─ Returns: (features_dict, features_meta)
       │
       └─ features = {
            "atr_14": 123.45,
            "atr_50": 145.67,
            "ema_20": 50123.45,
            "ema_50": 49987.32,
            "rsi_14": 58.32,
            "bb_position_20_2": 0.65,
            "adx_14": 24.3,
            "swing_high": 51234.56,
            "swing_low": 49876.54,
            "ltf_fib": {...},    # LTF Fibonacci levels
            "htf_fib": {...},    # HTF (1D) Fibonacci levels
            ...
          }

       ↓
       ┌────────────────────────────────────────────────────────────────┐
       │ STAGE 6: SIGNAL GENERATION (Probability Model)                 │
       │ File: src/core/strategy/prob_model.py                          │
       └────────────────────────────────────────────────────────────────┘
       ↓
       [FUNCTION] predict_proba_for(symbol, timeframe, features, regime)
       ├─ Load ML model for symbol/timeframe from disk
       ├─ Transform features → model input vector
       └─ Returns: probas = {"UP": 0.62, "DOWN": 0.38, "NEUTRAL": 0.15}
          **DATA PASSES AS**: Dict[str, float]
          **KEY INSIGHT**: This is where PARAMETERS first affect SIGNAL
          Parameters like thresholds.entry_conf_overall don't affect
          the probabilities themselves, only downstream decision gates.

       ↓
       ┌────────────────────────────────────────────────────────────────┐
       │ STAGE 7: CONFIDENCE CALCULATION                                │
       │ File: src/core/strategy/confidence.py                          │
       └────────────────────────────────────────────────────────────────┘
       ↓
       [FUNCTION] compute_confidence(probas, atr_pct, spread_bp, volume_score, data_quality, config)
       ├─ Applies quality adjustments to raw probabilities:
       │  ├─ volume_factor = compute from recent volume median
       │  ├─ spread_penalty = if spread > threshold
       │  ├─ data_quality_factor = general market conditions
       │  └─ quality_multiplicative = volume_factor * data_quality * (1 - spread_penalty)
       │
       ├─ Scales probabilities:
       │  └─ adjusted_proba = raw_proba * quality_multiplicative
       │
       └─ Returns: confidence = {
            "buy": 0.58,     # (0.62 * 0.935)
            "sell": 0.36,    # (0.38 * 0.935)
            "overall": 0.58  # max(buy, sell)
          }
          **DATA PASSES AS**: Dict[str, float]
          **KEY INSIGHT**: Quality adjustments can suppress signals even when
          model probabilities are high. Parameters affecting quality thresholds
          (e.g., volume_threshold) DIRECTLY affect confidence here.

       ↓
       ┌────────────────────────────────────────────────────────────────┐
       │ STAGE 8: DECISION MAKING (Entry Gates & Position Sizing)       │
       │ File: src/core/strategy/decision.py                            │
       └────────────────────────────────────────────────────────────────┘
       ↓
       [FUNCTION] decide(policy, probas, confidence, regime, state, risk_ctx, cfg)
       ├─ Extract PARAMETERS from cfg:
       │  ├─ entry_conf_overall = cfg["thresholds"]["entry_conf_overall"]  # e.g., 0.24
       │  ├─ signal_adaptation = cfg["thresholds"]["signal_adaptation"]["zones"]
       │  ├─ htf_fib_config = cfg.get("htf_fib", {})
       │  ├─ ltf_fib_config = cfg.get("ltf_fib", {})
       │  ├─ risk_map = cfg["risk"]["risk_map"]
       │  └─ hysteresis = cfg["thresholds"].get("hysteresis", 0.0)
       │
       ├─ ENTRY GATES (sequential checks):
       │  │
       │  ├─ [GATE 1] Check confidence threshold
       │  │  └─ IF confidence["overall"] < entry_conf_overall:
       │  │     RETURN ("NONE", "CONF_TOO_LOW")
       │  │
       │  ├─ [GATE 2] Apply regime-specific zone thresholds
       │  │  └─ IF regime == "low" AND confidence < zones["low"]["entry_conf_overall"]:
       │  │     RETURN ("NONE", "REGIME_ZONE_BLOCK")
       │  │
       │  ├─ [GATE 3] HTF Fibonacci gate (if enabled)
       │  │  └─ IF htf_fib["enabled"] AND current_price not near HTF levels:
       │  │     RETURN ("NONE", "HTF_FIB_BLOCK")
       │  │     **KEY INSIGHT**: htf_fib.enabled=False → this gate never blocks
       │  │
       │  ├─ [GATE 4] LTF Fibonacci gate (if enabled)
       │  │  └─ IF ltf_fib["enabled"] AND current_price not aligned with swing:
       │  │     RETURN ("NONE", "LTF_FIB_BLOCK")
       │  │
       │  ├─ [GATE 5] Hysteresis check (prevent flip-flopping)
       │  │  └─ IF recently_exited AND confidence < last_exit_conf + hysteresis:
       │  │     RETURN ("NONE", "HYSTERESIS_BLOCK")
       │  │
       │  └─ [GATE 6] Risk limit check
       │     └─ IF position_tracker.current_equity * max_leverage < min_position:
       │        RETURN ("NONE", "INSUFFICIENT_CAPITAL")
       │
       ├─ POSITION SIZING (if all gates passed):
       │  ├─ Lookup size_pct from risk_map based on confidence:
       │  │  └─ FOR each (conf_threshold, size_pct) in risk_map:
       │  │     IF confidence >= conf_threshold: selected_size = size_pct
       │  │
       │  ├─ Calculate position size:
       │  │  └─ size = current_equity * selected_size_pct
       │  │
       │  └─ Apply max_position_size cap if configured
       │
       └─ Returns: (action, action_meta)
          action = "LONG" | "SHORT" | "NONE"
          action_meta = {
            "size": 0.045,  # Position size as fraction of equity
            "confidence": 0.58,
            "reasons": ["HTF_ALIGNED", "LTF_BOUNCE"],
            "blocked_by": None,  # Or gate name if blocked
            "fib_debug": {...}
          }
          **DATA PASSES AS**: (Action, Dict)
          **KEY INSIGHT**: This is where PARAMETERS → DECISION happens!
          - entry_conf_overall gates the trade
          - risk_map determines size
          - fib gates can block entry entirely

       ↓
       ┌────────────────────────────────────────────────────────────────┐
       │ STAGE 9: ORDER EXECUTION (Simulated Fill)                      │
       │ File: src/core/backtest/position_tracker.py                    │
       └────────────────────────────────────────────────────────────────┘
       ↓
       IF action != "NONE":
          [FUNCTION] position_tracker.execute_action(action, size, price, timestamp)
          ├─ Close opposite position if exists (e.g., SHORT → LONG)
          │
          └─ Open new position:
             [FUNCTION] _open_position(side, size, price, timestamp)
             ├─ Apply SLIPPAGE:
             │  └─ effective_entry = price * (1 + slippage_rate)  # for LONG
             │                      price * (1 - slippage_rate)  # for SHORT
             │
             ├─ Calculate COMMISSION:
             │  └─ commission = notional_value * commission_rate
             │
             ├─ Deduct from capital:
             │  └─ capital -= commission
             │
             └─ Create Position object:
                position = {
                  "side": "LONG",
                  "size": 0.045,
                  "entry_price": 50134.56,  # After slippage
                  "entry_time": timestamp,
                  "commission": 25.07,
                  "reasons": ["HTF_ALIGNED", "LTF_BOUNCE"]
                }
          **DATA PASSES AS**: Position object stored in tracker
          **KEY INSIGHT**: This is where DECISION → ORDER → FILL happens.
          Fill price = market price + slippage (deterministic simulation).
          No parameter affects fill quality beyond commission_rate and slippage_rate.

       ↓
       ┌────────────────────────────────────────────────────────────────┐
       │ STAGE 10: PnL TRACKING (Per Bar)                               │
       │ File: src/core/backtest/position_tracker.py                    │
       └────────────────────────────────────────────────────────────────┘
       ↓
       [FUNCTION] position_tracker.update_equity(current_price, timestamp)
       ├─ Calculate unrealized PnL:
       │  └─ IF position.side == "LONG":
       │     unrealized = (current_price - entry_price) * position.size
       │  └─ IF position.side == "SHORT":
       │     unrealized = (entry_price - current_price) * position.size
       │
       ├─ Update equity:
       │  └─ current_equity = capital + unrealized_pnl
       │
       └─ Append to equity_curve:
          equity_curve.append({
            "timestamp": timestamp,
            "equity": current_equity,
            "pnl": unrealized_pnl,
            "drawdown_pct": (peak_equity - current_equity) / peak_equity * 100
          })
          **DATA PASSES AS**: List of equity snapshots
          **KEY INSIGHT**: This is where FILL → PnL happens.
          PnL calculation is deterministic: (exit - entry) * size - commissions.

       ↓
       ┌────────────────────────────────────────────────────────────────┐
       │ STAGE 11: EXIT LOGIC (HTF Fibonacci + Traditional)             │
       │ File: src/core/backtest/engine.py                              │
       └────────────────────────────────────────────────────────────────┘
       ↓
       IF position_tracker.has_position():
          [FUNCTION] _check_htf_exit_conditions(price, timestamp, result, meta, configs)
          ├─ Get HTF Fibonacci levels from meta["features"]["htf_fib"]
          ├─ Calculate ATR for tolerance bands
          │
          └─ Call HTF Exit Engine:
             [FUNCTION] HTFFibonacciExitEngine.check_exits(current_price, levels, atr)
             ├─ Check price against Fibonacci levels (0.382, 0.5, 0.618, 0.786)
             ├─ Returns list of ExitAction:
             │  └─ ExitAction(action="PARTIAL", close_size=0.5, reason="FIB_0.618")
             │     ExitAction(action="TRAIL_UPDATE", trail_price=50500, reason="...")
             │     ExitAction(action="FULL_EXIT", reason="FIB_0.786")
             │
             └─ Execute exit actions:
                IF "PARTIAL":
                   trade = position_tracker.partial_close(close_size, price, timestamp, reason)
                IF "FULL_EXIT":
                   trade = position_tracker.close_position_with_reason(price, timestamp, reason)
                   ↓
                   [FUNCTION] close_position_with_reason(price, timestamp, reason)
                   ├─ Apply SLIPPAGE on exit:
                   │  └─ exit_price = price * (1 - slippage_rate)  # for LONG
                   │
                   ├─ Calculate PnL:
                   │  └─ pnl = (exit_price - entry_price) * current_size
                   │        + realized_from_partials
                   │
                   ├─ Calculate exit commission:
                   │  └─ exit_commission = notional_value * commission_rate
                   │
                   ├─ Update capital:
                   │  └─ capital += pnl - exit_commission
                   │
                   └─ Record Trade:
                      trade = {
                        "side": "LONG",
                        "entry_price": 50134.56,
                        "exit_price": 51234.78,
                        "entry_time": "2024-06-01 10:00",
                        "exit_time": "2024-06-03 14:30",
                        "pnl": 1100.22,
                        "pnl_pct": 2.19,
                        "commission": 50.14,
                        "exit_reason": "FIB_0.618",
                        "entry_reasons": ["HTF_ALIGNED"],
                        ...
                      }
                      trades.append(trade)
          **DATA PASSES AS**: List of Trade objects
          **KEY INSIGHT**: This is where PnL → REALIZED TRADE happens.
          Exit parameters (htf_fib levels, partial percentages) DIRECTLY affect
          when and how much of a position is closed, thus affecting PnL.

    ↓ (After all bars processed)

┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 12: METRICS CALCULATION                                           │
│ File: src/core/backtest/metrics.py                                      │
└─────────────────────────────────────────────────────────────────────────┘
    ↓
    [FUNCTION] calculate_metrics(results)
    ├─ Extract trades and equity_curve from results
    │
    ├─ Calculate trade-based metrics:
    │  ├─ total_pnl = sum(trade.pnl for trade in trades)
    │  ├─ total_commission = sum(trade.commission for trade in trades)
    │  ├─ num_trades = len(trades)
    │  ├─ winning_trades = [t for t in trades if t.pnl > 0]
    │  ├─ losing_trades = [t for t in trades if t.pnl < 0]
    │  ├─ win_rate = len(winning_trades) / num_trades * 100
    │  ├─ profit_factor = sum(win.pnl) / abs(sum(loss.pnl))
    │  └─ avg_win/avg_loss
    │
    ├─ Calculate equity-based metrics:
    │  ├─ total_return = (final_equity - initial_capital) / initial_capital
    │  ├─ max_drawdown = max decline from peak equity (%)
    │  ├─ sharpe_ratio = mean(returns) / std(returns) * sqrt(252/bars_per_day)
    │  ├─ sortino_ratio = mean(returns) / std(negative_returns) * sqrt(252/bars_per_day)
    │  └─ calmar_ratio = total_return / max_drawdown
    │
    └─ Returns: metrics = {
         "total_trades": 164,
         "total_return": 0.0336,  # +3.36%
         "total_pnl": 336.45,
         "win_rate": 0.52,        # 52%
         "profit_factor": 1.25,
         "max_drawdown": 0.0297,  # 2.97%
         "sharpe_ratio": 0.87,
         "sortino_ratio": 1.12,
         "calmar_ratio": 1.13,
         "avg_trade_duration": "2d 4h",
         ...
       }
       **DATA PASSES AS**: Dict[str, float]
       **KEY INSIGHT**: This is where TRADES → METRICS happens.
       All metrics are derived from the trade list and equity curve.

    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 13: SCORING (Optuna Objective Value)                              │
│ File: src/core/optimizer/scoring.py                                     │
└─────────────────────────────────────────────────────────────────────────┘
    ↓
    [FUNCTION] score_backtest(result, thresholds, score_version)
    ├─ Extract metrics from result
    │
    ├─ Check HARD FAILURES:
    │  ├─ IF num_trades < thresholds.min_trades (default: 10):
    │  │  └─ RETURN {"score": -100, "hard_failures": ["num_trades"]}
    │  ├─ IF profit_factor < thresholds.min_profit_factor (default: 1.0):
    │  │  └─ RETURN {"score": -100, "hard_failures": ["profit_factor"]}
    │  └─ IF max_drawdown > thresholds.max_max_dd (default: 0.20):
    │     └─ RETURN {"score": -100, "hard_failures": ["max_drawdown"]}
    │
    ├─ Calculate SCORE (if no hard failures):
    │  │
    │  ├─ IF score_version == "v1":
    │  │  └─ score = sharpe + total_return + 0.25*return_to_dd + clip(win_rate-0.4, -0.2, 0.2)
    │  │
    │  └─ IF score_version == "v2":
    │     └─ score = clip(sharpe, -1, 3)
    │              + 0.15 * log1p(clip(total_return, -0.5, 0.5))
    │              + 0.10 * log(clip(profit_factor, 0.25, 5.0))
    │              + 0.05 * clip(win_rate - 0.5, -0.1, 0.1)
    │
    └─ Returns: {
         "score": 0.873,
         "metrics": {...},
         "hard_failures": [],
         "components": {
           "sharpe_clipped": 0.87,
           "return_log1p": 0.033,
           "pf_log": 0.223,
           "win_rate_term": 0.020
         }
       }
       **DATA PASSES AS**: Dict with score and breakdown
       **KEY INSIGHT**: This is where METRICS → OBJECTIVE SCORE happens.
       The score is a composite function of multiple metrics.
       Sharpe dominates in v2, return/PF are bonuses.

    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 14: CONSTRAINTS ENFORCEMENT                                       │
│ File: src/core/optimizer/constraints.py                                 │
└─────────────────────────────────────────────────────────────────────────┘
    ↓
    [FUNCTION] enforce_constraints(score_result, parameters, constraints_cfg)
    ├─ Check constraints from YAML config:
    │  ├─ min_trades, max_trades
    │  ├─ min_profit_factor
    │  ├─ max_max_dd
    │  ├─ max_total_commission_pct
    │  └─ zone_consistency (signal_adaptation zones must be ordered)
    │
    ├─ IF any constraint fails:
    │  └─ constraint_result = {"ok": False, "reasons": ["min_trades violated"]}
    │
    └─ Returns: ConstraintResult
       **DATA PASSES AS**: Dict with ok=True/False
       **KEY INSIGHT**: Constraints can block champion promotion even if
       score is good. Soft constraints apply penalty to objective value.

    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 15: OBJECTIVE RETURN (Optuna)                                     │
│ File: src/core/optimizer/runner.py                                      │
└─────────────────────────────────────────────────────────────────────────┘
    ↓
    [FUNCTION] objective(trial) - Returns to Optuna - Line 2670
    ├─ IF duplicate:
    │  └─ RETURN -1e6  # Heavy penalty
    │
    ├─ IF zero_trade_preflight:
    │  └─ RETURN penalty  # -1e5 or -500
    │
    ├─ IF error/pruned:
    │  └─ RAISE optuna.TrialPruned()
    │
    ├─ IF soft constraint fail:
    │  └─ RETURN score_value - CONSTRAINT_SOFT_PENALTY  # score - 150
    │
    └─ ELSE (success):
       └─ RETURN score_value  # e.g., 0.873

    **DATA PASSES AS**: Float (objective value for Optuna to maximize)
    **KEY INSIGHT**: This is the final METRIC → OBJECTIVE value.
    Optuna uses this to guide parameter suggestions in the next trial.
```

---

## C) Parameters That Don't Affect Outcomes

### Analysis Methodology
Traced parameter usage from suggestion → decision → order → PnL.
Parameters are "ineffective" if they are:
1. Never read by decision/sizing logic
2. Read but have no execution path to orders
3. Read but always overridden/ignored in practice

### Potentially Ineffective Parameters

| Parameter | Suggested Location | Read Location | Execution Path Status | Evidence |
|-----------|-------------------|---------------|----------------------|----------|
| `observability.metrics_enabled` | Never in Optuna configs | `evaluate.py` | **NOT on critical path** | Only affects logging, not decisions |
| `warmup_bars` (in some configs) | Optuna YAML | `engine.py` | **Affects window only, not decisions** | Changes when backtests starts, not strategy logic |
| `slippage_rate` (if not varied) | Often fixed | `position_tracker.py` | **Affects PnL but rarely optimized** | Fixed at 0.0005 in most runs |
| `commission_rate` (if not varied) | Often fixed | `position_tracker.py` | **Affects PnL but rarely optimized** | Fixed at 0.002 in most runs |
| `fast_window`, `precompute_features` | Environment, not Optuna | `engine.py` | **Execution mode, not strategy** | Only affects performance, not outcomes (when deterministic) |

### Parameters That ARE Effective (Confirmed in Chain)

| Parameter Category | Examples | Decision Stage | PnL Impact |
|-------------------|----------|----------------|------------|
| **Entry Thresholds** | `entry_conf_overall`, `zones.low/mid/high.entry_conf_overall` | Stage 8: Decision gates | **DIRECT** - Blocks/allows entries |
| **Risk Map** | `risk_map` (conf → size mappings) | Stage 8: Position sizing | **DIRECT** - Determines position size |
| **Fibonacci Gates** | `htf_fib.enabled`, `ltf_fib.enabled`, tolerance values | Stage 8: Decision gates | **DIRECT** - Can block all entries |
| **Exit Parameters** | `htf_fib.partial_1_pct`, `htf_fib.partial_2_pct`, level targets | Stage 11: Exit logic | **DIRECT** - Affects when/how much to exit |
| **Regime Adaptation** | `signal_adaptation.zones` thresholds | Stage 8: Decision gates | **DIRECT** - Changes entry bar by regime |
| **Hysteresis** | `thresholds.hysteresis` | Stage 8: Decision gates | **INDIRECT** - Prevents flip-flop trades |
| **Max Hold Bars** | `exits.max_hold_bars` | Stage 11: Exit logic | **DIRECT** - Forces exits after N bars |

### Parameters Where Effect Is LOST/DROPPED

**NONE IDENTIFIED** - All suggested parameters in active Optuna configs trace through to decision/sizing/exit logic.

**Historical Issues (FIXED)**:
- `atr_period` was hardcoded to 14 in `features_asof.py` (FIXED 2025-11-25)
- `max_hold_bars` was ignored in `BacktestEngine` (FIXED 2025-11-25)
- Dot-notation params weren't expanded (FIXED 2025-11-21)

---

## D) Dead/Legacy Code Analysis

### Code Not on Backtest or Optuna Critical Paths

| Module/File | Purpose | Used By | Status | Recommendation |
|-------------|---------|---------|--------|----------------|
| `src/core/ml/*.py` | ML model training, labeling, calibration | **NONE** (backtest/optuna) | **LEGACY/DEAD** | (a) Archive to `archive/ml_training/` |
| `src/core/symbols/symbols.py` | Symbol metadata registry | **NONE** (backtest/optuna) | **LEGACY/DEAD** | (a) Delete or (c) verify if server uses it |
| `src/core/io/bitfinex/*.py` | Exchange API client (Bitfinex) | `server.py` ONLY | **SERVER ONLY** | (b) Mark as "server-only", not backtest/optuna |
| `src/core/server.py` | FastAPI server for live trading UI | **NONE** (backtest/optuna) | **SERVER ONLY** | (b) Separate concern - not dead, but isolated |
| `src/core/server_config_api.py` | Config management API for server | `server.py` | **SERVER ONLY** | (b) Separate concern |
| `src/core/governance/*.py` | Registry validation, skills, compacts | **NONE** (backtest/optuna) | **GOVERNANCE ONLY** | (b) Separate concern - registry QA |
| `scripts/archive/` | Legacy debug scripts, old prototypes | **NONE** | **ARCHIVED** | Already archived - OK |

### Code on Critical Path but Possibly Redundant

| Module/File | Purpose | Redundancy Risk | Recommendation |
|-------------|---------|-----------------|----------------|
| `src/core/backtest/htf_exit_engine.py` (Legacy) | Old HTF exit engine | Possibly superseded by `strategy/htf_exit_engine.py` | (c) Verify both are needed, merge or deprecate |
| `src/core/observability/metrics.py` | Prometheus metrics | Optional, can be disabled | (b) Mark as optional dependency |

### Suggested Actions

#### (a) Can be deleted
- `src/core/ml/*.py` - Move entire directory to `archive/ml_training_tools/`
  - **Reason**: No imports from backtest/optuna paths, likely used for one-time model training
  - **Risk**: Low - models are loaded from disk, not re-trained during backtests
  - **Verification**: Search codebase for `from core.ml` in `backtest/`, `optimizer/`, `strategy/`

- `src/core/symbols/symbols.py` - Delete or move to `tools/`
  - **Reason**: No imports in critical paths
  - **Risk**: Low - appears to be a symbol metadata registry not used at runtime

#### (b) Can be archived (or marked as separate concern)
- `src/core/io/bitfinex/*.py` - Keep, but document as "SERVER ONLY, not used in backtest/optuna"
- `src/core/server.py`, `server_config_api.py` - Keep, but separate from backtest/optuna documentation
- `src/core/governance/*.py` - Keep, but document as "REGISTRY QA ONLY"

#### (c) Needs verification with test/trace
- `src/core/backtest/htf_exit_engine.py` vs `src/core/strategy/htf_exit_engine.py`
  - **Action**: Trace which one is actually used in `BacktestEngine._check_htf_exit_conditions()`
  - **Expected**: Likely one is deprecated, should be removed or merged
  - **Test**: Run backtest with HTF exits enabled, instrument to see which class is instantiated

- `src/core/observability/metrics.py`
  - **Action**: Verify if disabling it (`GENESIS_DISABLE_METRICS=1`) affects backtest results
  - **Expected**: Should only affect logging, not outcomes
  - **Test**: Run identical backtest with metrics on/off, compare results byte-for-byte

---

## E) Golden Trace Tests

### Purpose
Lock the causal chain and catch semantic drift by asserting that:
1. Same parameters → same features
2. Same features → same decisions
3. Same decisions → same PnL

### Recommended Golden Trace Tests

#### Test 1: Parameter → Feature Determinism
**File**: `tests/golden_traces/test_param_to_feature_trace.py`

```python
def test_param_to_feature_determinism():
    """
    GOLDEN TRACE 1: Parameters → Features
    
    Verifies that given identical parameters and market data, 
    feature extraction produces identical outputs.
    
    Catches drift in:
    - Indicator calculations (ATR, EMA, RSI, etc.)
    - Fibonacci swing detection
    - Feature preprocessing
    """
    # Load frozen test data
    candles = load_frozen_candles("tBTCUSD_1h_sample_100bars.parquet")
    
    # Fixed parameter set (from known champion)
    params = load_champion_params("tBTCUSD_1h_golden.json")
    
    # Extract features
    features, meta = extract_features(
        candles=candles,
        configs=params,
        state={}
    )
    
    # Load golden snapshot (generated from known-good version)
    golden_features = load_golden_snapshot("golden_features_v1.json")
    
    # Assert byte-for-byte equality on critical features
    assert_close(features["atr_14"], golden_features["atr_14"], rtol=1e-10)
    assert_close(features["ema_20"], golden_features["ema_20"], rtol=1e-10)
    assert_close(features["rsi_14"], golden_features["rsi_14"], rtol=1e-10)
    assert features["swing_high"] == golden_features["swing_high"]
    assert features["swing_low"] == golden_features["swing_low"]
    
    # Assert HTF/LTF Fibonacci levels unchanged
    assert_fib_levels_equal(features["htf_fib"], golden_features["htf_fib"])
    assert_fib_levels_equal(features["ltf_fib"], golden_features["ltf_fib"])
```

**Success Criteria**:
- All numeric features match within 1e-10 relative tolerance
- Fibonacci levels (prices, indices) match exactly
- Test fails immediately if feature calculation logic changes

**Maintenance**:
- Re-baseline golden snapshot when intentionally changing indicator logic
- Version golden snapshots: `golden_features_v1.json`, `golden_features_v2.json`

---

#### Test 2: Feature → Decision Determinism
**File**: `tests/golden_traces/test_feature_to_decision_trace.py`

```python
def test_feature_to_decision_determinism():
    """
    GOLDEN TRACE 2: Features → Decisions
    
    Verifies that given identical features and parameters,
    decision logic produces identical entry/exit signals.
    
    Catches drift in:
    - Confidence calculation
    - Entry gate logic (Fibonacci, thresholds, regime)
    - Position sizing (risk map)
    - Exit conditions (HTF Fibonacci, trailing stops)
    """
    # Load frozen features and configs
    features = load_golden_snapshot("golden_features_v1.json")
    params = load_champion_params("tBTCUSD_1h_golden.json")
    
    # Mock probability model output (deterministic)
    probas = {"UP": 0.62, "DOWN": 0.38, "NEUTRAL": 0.15}
    
    # Compute confidence
    confidence = compute_confidence(
        probas=probas,
        atr_pct=features["atr_14"] / features["close"] * 100,
        spread_bp=1.0,
        volume_score=0.85,
        data_quality=1.0,
        config=params
    )
    
    # Make decision
    action, action_meta = decide(
        policy="backtest",
        probas=probas,
        confidence=confidence,
        regime="bull",
        state={},
        risk_ctx={"current_equity": 10000.0},
        cfg=params
    )
    
    # Load golden decision
    golden_decision = load_golden_snapshot("golden_decision_v1.json")
    
    # Assert decision matches
    assert action == golden_decision["action"]
    assert_close(action_meta["size"], golden_decision["size"], rtol=1e-10)
    assert action_meta["reasons"] == golden_decision["reasons"]
    assert action_meta["blocked_by"] == golden_decision["blocked_by"]
    
    # Assert confidence calculation unchanged
    assert_close(confidence["overall"], golden_decision["confidence"], rtol=1e-10)
```

**Success Criteria**:
- Action (LONG/SHORT/NONE) matches exactly
- Position size matches within 1e-10
- Block reasons match (or both None)
- Confidence values match within 1e-10

**Maintenance**:
- Re-baseline when intentionally changing decision gates or confidence formula
- Include multiple scenarios: entry allowed, blocked by HTF, blocked by confidence

---

#### Test 3: End-to-End Backtest Determinism
**File**: `tests/golden_traces/test_backtest_e2e_trace.py`

```python
def test_backtest_e2e_determinism():
    """
    GOLDEN TRACE 3: Full Backtest (Param → PnL)
    
    Verifies that given identical parameters and market data,
    a complete backtest produces identical trade outcomes and metrics.
    
    Catches drift in:
    - Entire execution pipeline
    - Fill simulation (slippage, commission)
    - PnL calculation
    - Metrics calculation
    - Any semantic changes to strategy logic
    """
    # Fixed seed for determinism
    set_global_seeds(42)
    
    # Load frozen data and champion params
    params = load_champion_params("tBTCUSD_1h_golden.json")
    
    # Create engine with fixed parameters
    engine = BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2024-06-01",
        end_date="2024-08-01",
        initial_capital=10000.0,
        commission_rate=0.002,
        slippage_rate=0.0005,
        warmup_bars=150,
        fast_window=True
    )
    
    # Load data (should use frozen file)
    engine.load_data()
    
    # Run backtest
    results = engine.run(policy="backtest", configs=params, verbose=False)
    
    # Load golden backtest results
    golden_results = load_golden_snapshot("golden_backtest_v1.json")
    
    # Assert trade-level determinism
    assert len(results["trades"]) == len(golden_results["trades"])
    
    for i, (trade, golden_trade) in enumerate(zip(results["trades"], golden_results["trades"])):
        assert trade["side"] == golden_trade["side"], f"Trade {i} side mismatch"
        assert_close(trade["entry_price"], golden_trade["entry_price"], rtol=1e-8)
        assert_close(trade["exit_price"], golden_trade["exit_price"], rtol=1e-8)
        assert_close(trade["pnl"], golden_trade["pnl"], rtol=1e-8)
        assert trade["exit_reason"] == golden_trade["exit_reason"]
    
    # Assert metrics determinism
    metrics = calculate_metrics(results)
    golden_metrics = golden_results["metrics"]
    
    assert metrics["total_trades"] == golden_metrics["total_trades"]
    assert_close(metrics["total_return"], golden_metrics["total_return"], rtol=1e-10)
    assert_close(metrics["profit_factor"], golden_metrics["profit_factor"], rtol=1e-10)
    assert_close(metrics["max_drawdown"], golden_metrics["max_drawdown"], rtol=1e-10)
    assert_close(metrics["sharpe_ratio"], golden_metrics["sharpe_ratio"], rtol=1e-10)
    
    # Assert final equity determinism (ultimate sanity check)
    final_equity = results["summary"]["final_capital"]
    golden_final_equity = golden_results["summary"]["final_capital"]
    assert_close(final_equity, golden_final_equity, rtol=1e-12)
```

**Success Criteria**:
- Exact same number of trades
- Each trade has identical entry/exit prices, PnL, reasons (within numerical precision)
- All metrics match within 1e-10
- Final equity matches within 1e-12 (tightest tolerance)

**Maintenance**:
- Re-baseline only when intentionally changing strategy logic
- Include note in golden snapshot indicating known-good version SHA
- Run this test on every commit to `master` (CI/CD)

---

### Golden Trace Test Infrastructure

**Snapshot Storage**: `tests/golden_traces/snapshots/`
```
snapshots/
├── golden_features_v1.json      # Features from 100-bar sample
├── golden_decision_v1.json      # Decision from fixed features
├── golden_backtest_v1.json      # Full backtest results (2024-06-01 to 2024-08-01)
└── tBTCUSD_1h_sample_100bars.parquet  # Frozen candle data for Test 1
```

**Re-baseline Script**: `scripts/rebaseline_golden_traces.py`
```python
"""
Re-generate golden trace snapshots after intentional logic changes.

Usage:
    python scripts/rebaseline_golden_traces.py --test test_param_to_feature_trace
    python scripts/rebaseline_golden_traces.py --all
"""
```

**CI Integration**:
```yaml
# .github/workflows/ci.yml
- name: Golden Trace Tests
  run: pytest tests/golden_traces/ -v --strict-markers
  # Fails if ANY golden trace deviates from snapshot
```

---

## Summary Statistics

### Code Coverage by Critical Paths

| Category | Total Files | Used in Backtest | Used in Optuna | Dead/Isolated |
|----------|------------|------------------|----------------|---------------|
| Strategy | 12 | 12 (100%) | 12 (100%) | 0 |
| Backtest Engine | 4 | 4 (100%) | 4 (100%) | 0 |
| Optimizer | 8 | 0 | 8 (100%) | 0 |
| Indicators | 10 | 10 (100%) | 10 (100%) | 0 |
| ML Training | 9 | 0 | 0 | 9 (100%) |
| IO/Exchange | 6 | 0 | 0 | 6 (100% server-only) |
| Server | 2 | 0 | 0 | 2 (100% server-only) |
| Governance | 3 | 0 | 0 | 3 (100% registry-only) |
| **TOTAL** | **54** | **26 (48%)** | **34 (63%)** | **20 (37%)** |

### Key Findings

1. **Critical Path Integrity**: All 26 backtest modules and 34 Optuna modules are actively used
2. **Dead Code**: 20 files (37%) are not on backtest/optuna paths:
   - 9 ML training tools (should archive)
   - 6 Exchange I/O (server-only, keep separate)
   - 2 Server modules (live trading, keep separate)
   - 3 Governance modules (registry QA, keep separate)
3. **Parameter Effectiveness**: All Optuna-suggested parameters trace to decision/sizing/exit logic
4. **No Dropped Parameters**: All active parameters affect outcomes (post-fixes from 2025-11)

---

## Next Steps

1. **Archive ML Training Tools**: Move `src/core/ml/` → `archive/ml_training/` (low risk)
2. **Verify HTF Exit Engine Redundancy**: Determine if both legacy and new exit engines are needed
3. **Implement Golden Trace Tests**: Start with Test 3 (E2E) for immediate drift detection
4. **Document Server/Governance Separation**: Update README to clarify runtime vs. tooling code
5. **Automate Golden Trace CI**: Fail builds if traces deviate without re-baseline approval

---

**Document Maintained By**: Runtime Analysis Team  
**Last Updated**: 2026-01-21  
**Version**: 1.0
