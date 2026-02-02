"""
Component Context Builder - Maps evaluate_pipeline output to component context.

Transforms the complex nested structure from evaluate_pipeline into a flat
dictionary that components can consume.
"""

from typing import Any


class ComponentContextBuilder:
    """
    Builds component context from evaluate_pipeline output.

    Maps the result and meta dictionaries from evaluate_pipeline into a flat
    context dict that components can consume with clear, predictable keys.
    """

    @staticmethod
    def build(
        result: dict[str, Any], meta: dict[str, Any], *, candles: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Build component context from pipeline output.

        Args:
            result: Result dict from evaluate_pipeline (first return value)
            meta: Meta dict from evaluate_pipeline (second return value)
            candles: Optional candles dict for additional context

        Returns:
            Flat dictionary with component-friendly keys
        """
        context = {}

        # ML Confidence (from probas or confidence)
        probas = result.get("probas", {})
        confidence = result.get("confidence", {})

        if isinstance(probas, dict) and probas:
            # Normalize keys to handle both 'buy'/'sell' (model output) and 'LONG'/'SHORT' (legacy)
            # Case-insensitive lookup with explicit fallback chain
            probas_normalized = {k.lower(): v for k, v in probas.items()}

            p_long = (
                probas_normalized.get("buy")  # Primary: model output
                or probas_normalized.get("long")  # Fallback: legacy key
                or 0.0
            )
            p_short = (
                probas_normalized.get("sell")  # Primary: model output
                or probas_normalized.get("short")  # Fallback: legacy key
                or 0.0
            )

            # Only set proba keys if we have valid values
            if p_long > 0 or p_short > 0:
                context["ml_proba_long"] = p_long
                context["ml_proba_short"] = p_short

        if isinstance(confidence, dict) and confidence:
            context["ml_confidence_long"] = confidence.get("buy", 0.0)
            context["ml_confidence_short"] = confidence.get("sell", 0.0)

        # For backward compat with POC components, map to single "ml_confidence"
        # (use LONG as default for now, components can be updated later)
        if "ml_confidence_long" in context:
            context["ml_confidence"] = context["ml_confidence_long"]
        elif "ml_proba_long" in context:
            context["ml_confidence"] = context["ml_proba_long"]

        # Expected Value (EV) calculation
        # ===================================
        # EV measures expected profit/loss per trade based on win probability.
        #
        # Formula (simplified with R=1.0 risk-reward ratio):
        #   EV_long  = proba_long * R - proba_short
        #   EV_short = proba_short * R - proba_long
        #   expected_value = max(EV_long, EV_short)
        #
        # Where:
        #   - proba_long: Probability of LONG win (from ML model)
        #   - proba_short: Probability of SHORT win (from ML model)
        #   - R: Reward-to-risk ratio (default 1.0 = equal R:R)
        #
        # Interpretation:
        #   - EV > 0: Positive expected value (profitable on average)
        #   - EV = 0: Break-even
        #   - EV < 0: Negative expected value (unprofitable on average)
        #
        # IMPORTANT: This is a SIMPLIFIED calculation.
        # Full EV should account for:
        #   - Actual position size
        #   - Slippage and commissions
        #   - Dynamic R:R based on market conditions
        #
        # Phase 2: Uses R=1.0 for simplicity and consistency.
        # Phase 3: May enhance with dynamic R:R from configs.
        #
        # IMPORTANT: Only calculate EV when probas are present and valid (no degenerate 0.0)
        if "ml_proba_long" in context and "ml_proba_short" in context:
            p_long = context["ml_proba_long"]
            p_short = context["ml_proba_short"]

            # Only emit EV fields if probas are meaningful (not both zero)
            if p_long > 0 or p_short > 0:
                R = 1.0  # Simplified reward-to-risk ratio (1:1)

                ev_long = p_long * R - p_short
                ev_short = p_short * R - p_long

                # Store both directions and max EV
                context["ev_long"] = ev_long
                context["ev_short"] = ev_short
                context["expected_value"] = max(ev_long, ev_short)  # SSOT key for EVGate

        # Regime (from result)
        context["regime"] = result.get("regime", "unknown")
        context["htf_regime"] = result.get("htf_regime", "unknown")

        # Features (flatten commonly used ones)
        features = result.get("features", {})
        if isinstance(features, dict) and features:
            atr_val = features.get("atr_14")
            if atr_val is not None:
                context["atr"] = atr_val
                # ATR MA for ATR filter (approximation)
                context["atr_ma"] = atr_val * 0.9

            rsi_val = features.get("rsi")
            if rsi_val is not None:
                context["rsi"] = rsi_val

            adx_val = features.get("adx")
            if adx_val is not None:
                context["adx"] = adx_val

            ema_delta = features.get("ema_delta_pct")
            if ema_delta is not None:
                context["ema_delta_pct"] = ema_delta

        # Action (for hysteresis/cooldown components)
        context["action"] = result.get("action", "NONE")

        # Meta data
        features_meta = meta.get("features", {})
        if isinstance(features_meta, dict) and features_meta:
            current_atr = features_meta.get("current_atr_used")
            if current_atr is not None:
                context["current_atr"] = current_atr

            htf_fib = features_meta.get("htf_fibonacci", {})
            if isinstance(htf_fib, dict):
                context["htf_fib_available"] = htf_fib.get("available", False)

            ltf_fib = features_meta.get("ltf_fibonacci", {})
            if isinstance(ltf_fib, dict):
                context["ltf_fib_available"] = ltf_fib.get("available", False)

        # Candles (if provided)
        if candles is not None:
            closes = candles.get("close")
            if closes is not None and len(closes) > 0:
                context["current_price"] = float(closes[-1])

            timestamps = candles.get("timestamp")
            if timestamps is not None and len(timestamps) > 0:
                context["timestamp"] = timestamps[-1]

            # Bar index for stateful components (Cooldown, Hysteresis)
            # Injected by BacktestEngine before hook call
            bar_index = candles.get("bar_index")
            if bar_index is not None:
                context["bar_index"] = int(bar_index)

            # Symbol for multi-symbol state isolation
            # Injected by BacktestEngine before hook call
            symbol = candles.get("symbol")
            if symbol is not None:
                context["symbol"] = str(symbol)

        return context

    @staticmethod
    def get_required_keys() -> list[str]:
        """
        Return list of keys that are expected to be present.

        Components should handle missing keys gracefully, but this list
        helps with debugging and validation.
        """
        return [
            "ml_confidence",
            "regime",
            "htf_regime",
            "atr",
            "action",
        ]

    @staticmethod
    def get_optional_keys() -> list[str]:
        """Return list of optional context keys."""
        return [
            "ml_proba_long",
            "ml_proba_short",
            "ml_confidence_long",
            "ml_confidence_short",
            "ev_long",
            "ev_short",
            "expected_value",
            "atr_ma",
            "rsi",
            "adx",
            "ema_delta_pct",
            "current_price",
            "timestamp",
            "bar_index",
            "symbol",
            "current_atr",
            "htf_fib_available",
            "ltf_fib_available",
        ]
