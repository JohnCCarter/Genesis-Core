"""HTF exit-dispatch logic extracted from BacktestEngine (no behavior change)."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

import pandas as pd

from core.backtest.engine_exit_utils import check_traditional_exit_conditions
from core.backtest.htf_exit_engine import ExitAction
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger("core.backtest.engine")


def check_htf_exit_conditions(
    engine: Any,
    current_price: float,
    timestamp: datetime,
    bar_data: dict,
    result: dict,
    meta: dict,
    configs: dict,
    bar_index: int | None = None,
) -> str | None:
    """Check HTF Fibonacci exit conditions and return exit reason if any."""
    if not engine.position_tracker.has_position():
        return None

    position = engine.position_tracker.position
    decision_state = (meta.get("decision") or {}).get("state_out") or {}

    # Get exit config (top-level in merged configs)
    exit_cfg = configs.get("exit", {})
    enabled = exit_cfg.get("enabled", True)

    if not enabled:
        return None

    # Prefer explicit bar_index (passed from main loop). Fallback to configs['_global_index'].
    idx = bar_index
    if idx is None:
        try:
            idx = int(configs.get("_global_index"))
        except Exception:
            idx = None

    # Get HTF Fibonacci context - prefer precomputed if available
    htf_fib_context = {}
    if (
        idx is not None
        and engine._precomputed_features
        and "htf_fib_0382" in engine._precomputed_features
    ):
        # Fast path: use precomputed HTF mapping
        try:

            def _to_positive_finite(value: Any) -> float | None:
                try:
                    parsed = float(value)
                except (TypeError, ValueError):
                    return None
                if not math.isfinite(parsed) or parsed <= 0.0:
                    return None
                return parsed

            level_0382 = _to_positive_finite(engine._precomputed_features["htf_fib_0382"][idx])
            level_05 = _to_positive_finite(engine._precomputed_features["htf_fib_05"][idx])
            level_0618 = _to_positive_finite(engine._precomputed_features["htf_fib_0618"][idx])
            swing_high = _to_positive_finite(
                engine._precomputed_features.get("htf_swing_high", [0.0] * (idx + 1))[idx]
            )
            swing_low = _to_positive_finite(
                engine._precomputed_features.get("htf_swing_low", [0.0] * (idx + 1))[idx]
            )

            levels_complete = all(v is not None for v in (level_0382, level_05, level_0618))
            swings_valid = (
                swing_high is not None
                and swing_low is not None
                and float(swing_high) > float(swing_low)
            )

            if levels_complete and swings_valid:
                htf_fib_context = {
                    "available": True,
                    "levels": {
                        0.382: float(level_0382),
                        0.5: float(level_05),
                        0.618: float(level_0618),
                    },
                    "swing_high": float(swing_high),
                    "swing_low": float(swing_low),
                }
            else:
                htf_fib_context = {"available": False}
        except (IndexError, KeyError, TypeError, ValueError):
            htf_fib_context = {"available": False}
    else:
        # Fallback: use meta from evaluate_pipeline
        features_meta = meta.get("features", {})
        htf_fib_context = features_meta.get("htf_fibonacci", {})

    # Track whether HTF context was ever available during this run.
    if isinstance(htf_fib_context, dict) and htf_fib_context.get("available"):
        engine._htf_context_seen = True

    # Calculate ATR for exit logic (use last 14 bars AS OF current bar)
    from core.indicators.atr import calculate_atr

    current_atr = 100.0
    if idx is not None and engine._np_arrays is not None:
        window_size = min(14, idx + 1)
        if window_size >= 2:
            i0 = max(0, idx - window_size + 1)
            i1 = idx + 1
            recent_highs = engine._np_arrays["high"][i0:i1]
            recent_lows = engine._np_arrays["low"][i0:i1]
            recent_closes = engine._np_arrays["close"][i0:i1]
            atr_values = calculate_atr(recent_highs, recent_lows, recent_closes, period=14)
            current_atr = float(atr_values[-1]) if len(atr_values) > 0 else 100.0
    elif engine.candles_df is not None:
        # Defensive fallback for callers that don't supply an index.
        window_size = min(14, len(engine.candles_df))
        if window_size >= 2:
            recent_highs = engine.candles_df["high"].iloc[-window_size:].values
            recent_lows = engine.candles_df["low"].iloc[-window_size:].values
            recent_closes = engine.candles_df["close"].iloc[-window_size:].values
            atr_values = calculate_atr(recent_highs, recent_lows, recent_closes, period=14)
            current_atr = float(atr_values[-1]) if len(atr_values) > 0 else 100.0

    # Prepare indicators for exit engine
    features = result.get("features", {})
    indicators = {
        "atr": current_atr,
        "ema50": features.get("ema", current_price),  # Use ema feature (EMA50)
        "ema_slope50_z": features.get("ema_slope50_z", 0.0),
    }

    # Check HTF exit conditions
    if getattr(engine, "_use_new_exit_engine", False):
        # Adapter for New Engine (Phase 1)
        side_int = 1 if position.side == "LONG" else -1
        # Normalize levels to the keys expected by the strategy-level engine.
        # The strategy engine reads: htf_fib_0382, htf_fib_05, htf_fib_0618.
        # Our context may store levels keyed by floats (0.382/0.5/0.618) or strings.
        htf_levels = htf_fib_context.get("levels", {})
        if not isinstance(htf_levels, dict):
            htf_levels = {}

        def _coerce_float(value: Any) -> float | None:
            try:
                return float(value)
            except Exception:  # nosec B110
                return None

        def _get_level(*candidates: Any) -> float | None:
            for cand in candidates:
                if cand in htf_levels:
                    v = _coerce_float(htf_levels.get(cand))
                    if v is not None:
                        return v
                s = str(cand)
                if s in htf_levels:
                    v = _coerce_float(htf_levels.get(s))
                    if v is not None:
                        return v
            return None

        htf_data = pd.Series(
            {
                "htf_fib_0382": _get_level("htf_fib_0382", 0.382),
                "htf_fib_05": _get_level("htf_fib_05", 0.5),
                "htf_fib_0618": _get_level("htf_fib_0618", 0.618),
            }
        )

        try:
            signal_or_actions = engine.htf_exit_engine.check_exits(
                current_price=current_price,
                position_size=float(position.current_size),
                entry_price=float(position.entry_price),
                side=side_int,
                current_atr=current_atr,
                htf_data=htf_data,
            )
        except TypeError as exc:
            err = str(exc)
            legacy_signature = (
                "unexpected keyword" in err
                or "required positional argument" in err
                or "positional arguments" in err
            )
            if not legacy_signature:
                raise
            signal_or_actions = engine.htf_exit_engine.check_exits(
                position,
                bar_data,
                htf_fib_context,
                indicators,
            )

        # Some tests monkeypatch `check_exits` to return a list of ExitAction.
        # Accept that shape directly to keep `_check_htf_exit_conditions` focused on ATR/no-lookahead.
        if isinstance(signal_or_actions, list):
            exit_actions = signal_or_actions
        else:
            signal = signal_or_actions
            exit_actions = []
            if signal is None:
                exit_actions = []
            else:
                enable_partials = bool(getattr(engine.htf_exit_engine, "enable_partials", True))
                enable_trailing = bool(getattr(engine.htf_exit_engine, "enable_trailing", True))

                if signal.action in ["PARTIAL_EXIT", "FULL_EXIT"]:
                    if signal.action == "PARTIAL_EXIT" and not enable_partials:
                        pass
                    else:
                        # Map to Legacy ExitAction
                        # PARTIAL_EXIT usually implies a size. FULL_EXIT implies size=current.
                        action_map = "PARTIAL" if signal.action == "PARTIAL_EXIT" else "FULL_EXIT"

                        # Calculate size amount
                        if getattr(signal, "quantity_pct", 0.0) and signal.quantity_pct > 0:
                            size_val = float(position.current_size) * float(signal.quantity_pct)
                        else:
                            # No explicit quantity => treat as full for FULL_EXIT, else no-op.
                            size_val = (
                                float(position.current_size) if action_map == "FULL_EXIT" else 0.0
                            )

                        exit_actions.append(
                            ExitAction(action=action_map, size=size_val, reason=signal.reason)
                        )

                elif signal.action == "UPDATE_STOP":
                    if enable_trailing and getattr(signal, "new_stop_price", None) is not None:
                        exit_actions.append(
                            ExitAction(
                                action="TRAIL_UPDATE",
                                stop_price=float(signal.new_stop_price),
                                reason=signal.reason,
                            )
                        )
    else:
        # Legacy Call
        exit_actions = engine.htf_exit_engine.check_exits(
            position, bar_data, htf_fib_context, indicators
        )
    meta.setdefault("signal", {})
    meta["signal"]["current_atr"] = current_atr

    # Execute exit actions
    exit_cfg = configs.get("exit", {})
    break_even_trigger = exit_cfg.get("break_even_trigger")
    break_even_offset = exit_cfg.get("break_even_offset", 0.0)
    partial_break_even = exit_cfg.get("partial_break_even", False)
    partial_break_even_offset = exit_cfg.get("partial_break_even_offset", break_even_offset)

    if exit_actions:
        meaningful_actions = [
            {
                "action": action.action,
                "size": action.size,
                "stop_price": action.stop_price,
                "reason": action.reason,
            }
            for action in exit_actions
            if action.action not in {"DEBUG", "TRAIL_UPDATE"}
        ]
        if meaningful_actions:
            exit_debug = {
                "timestamp": timestamp.isoformat(),
                "price": current_price,
                "actions": meaningful_actions,
                "position_side": position.side,
                "current_atr": current_atr,
                "fib_gate_summary": decision_state.get("fib_gate_summary"),
                "htf_entry_debug": decision_state.get("htf_fib_entry_debug"),
                "ltf_entry_debug": decision_state.get("ltf_fib_entry_debug"),
                "htf_exit_config": {
                    "fib_threshold_atr": engine.htf_exit_config.get("fib_threshold_atr"),
                    "trail_atr_multiplier": engine.htf_exit_config.get("trail_atr_multiplier"),
                },
            }
            engine.position_tracker.append_exit_fib_debug(exit_debug)

    for action in exit_actions:
        if action.action == "PARTIAL":
            # Execute partial exit
            trade = engine.position_tracker.partial_close(
                close_size=action.size,
                price=current_price,
                timestamp=timestamp,
                reason=action.reason,
            )
            if trade:  # Always log partial exits
                _LOGGER.info(
                    "PARTIAL exit: %s | size=%.3f @ $%s | pnl=$%s",
                    action.reason,
                    float(trade.size),
                    f"{float(trade.exit_price):,.0f}",
                    f"{float(trade.pnl):,.2f}",
                )
                if partial_break_even and trade.remaining_size > 0:
                    if position.side == "LONG":
                        be_price = position.entry_price * (1 + partial_break_even_offset)
                        position.trail_stop = max(position.trail_stop or -float("inf"), be_price)
                    else:
                        be_price = position.entry_price * (1 - partial_break_even_offset)
                        position.trail_stop = min(position.trail_stop or float("inf"), be_price)

        elif action.action == "TRAIL_UPDATE":
            # Update trailing stop (store in position for next bar)
            if hasattr(position, "trail_stop"):
                position.trail_stop = action.stop_price
            else:
                # Add trail_stop attribute if not exists
                position.trail_stop = action.stop_price
            # Break-even promotion if configured
            if break_even_trigger is not None:
                pnl_pct = engine.position_tracker.get_unrealized_pnl_pct(current_price) / 100.0
                if pnl_pct >= break_even_trigger:
                    if position.side == "LONG":
                        be_price = position.entry_price * (1 + break_even_offset)
                        position.trail_stop = max(position.trail_stop, be_price)
                    else:
                        be_price = position.entry_price * (1 - break_even_offset)
                        position.trail_stop = min(position.trail_stop, be_price)

        elif action.action == "FULL_EXIT":
            # Full exit - return reason to trigger standard exit logic
            engine.position_tracker.append_exit_fib_debug(
                {
                    "timestamp": timestamp.isoformat(),
                    "price": current_price,
                    "reason": action.reason,
                    "source": "HTF_FULL_EXIT",
                    "fib_gate_summary": decision_state.get("fib_gate_summary"),
                }
            )
            return action.reason

    # Check if trail stop hit (from previous bars)
    if (
        hasattr(position, "trail_stop")
        and position.trail_stop
        and (
            (position.side == "LONG" and current_price <= position.trail_stop)
            or (position.side == "SHORT" and current_price >= position.trail_stop)
        )
    ):
        engine.position_tracker.append_exit_fib_debug(
            {
                "timestamp": timestamp.isoformat(),
                "price": current_price,
                "reason": "TRAIL_STOP",
                "source": "TRAIL_STOP",
                "fib_gate_summary": decision_state.get("fib_gate_summary"),
            }
        )
        return "TRAIL_STOP"

    # Fallback to traditional exit conditions for safety
    fallback_reason = check_traditional_exit_conditions(
        engine.position_tracker, current_price, result, configs
    )
    if fallback_reason:
        engine.position_tracker.append_exit_fib_debug(
            {
                "timestamp": timestamp.isoformat(),
                "price": current_price,
                "reason": fallback_reason,
                "source": "TRADITIONAL_EXIT",
                "fib_gate_summary": decision_state.get("fib_gate_summary"),
            }
        )
    return fallback_reason
