"""Tests for regime detection and classification."""

from __future__ import annotations

from core.strategy.regime import classify_regime, detect_regime_from_candles


class TestClassifyRegime:
    """Test regime classification logic."""

    def test_bull_regime(self):
        """Test bull regime detection."""
        # Disable hysteresis by setting prev_state to bull
        regime, state = classify_regime(
            {
                "adx": 30.0,  # Strong trend
                "price_vs_ema": 0.05,  # Price 5% above EMA
                "ema_slope": 0.01,  # Positive slope
                "volatility": 0.02,
            },
            prev_state={"regime": "bull", "steps": 0},
        )
        assert regime == "bull"
        assert isinstance(state, dict)
        assert state["regime"] == "bull"
        assert state["candidate"] == "bull"

    def test_bear_regime(self):
        """Test bear regime detection."""
        # Disable hysteresis by setting prev_state to bear
        regime, state = classify_regime(
            {
                "adx": 30.0,  # Strong trend
                "price_vs_ema": -0.05,  # Price 5% below EMA
                "ema_slope": -0.01,  # Negative slope
                "volatility": 0.02,
            },
            prev_state={"regime": "bear", "steps": 0},
        )
        assert regime == "bear"
        assert state["regime"] == "bear"
        assert state["candidate"] == "bear"

    def test_ranging_regime(self):
        """Test ranging regime detection."""
        # Disable hysteresis by setting prev_state to ranging
        regime, state = classify_regime(
            {
                "adx": 15.0,  # Low trend strength
                "price_vs_ema": 0.0,  # Price at EMA
                "ema_slope": 0.0,  # Flat
                "volatility": 0.01,  # Low volatility
            },
            prev_state={"regime": "ranging", "steps": 0},
        )
        assert regime == "ranging"
        assert state["regime"] == "ranging"
        assert state["candidate"] == "ranging"

    def test_balanced_regime(self):
        """Test balanced regime detection."""
        regime, state = classify_regime(
            {
                "adx": 22.0,  # Mid-range ADX
                "price_vs_ema": 0.01,
                "ema_slope": 0.0005,
                "volatility": 0.03,
            }
        )
        assert regime == "balanced"
        assert state["regime"] == "balanced"

    def test_regime_hysteresis(self):
        """Test hysteresis prevents rapid regime switching."""
        cfg = {"gates": {"hysteresis_steps": 2}}
        state = {"regime": "balanced", "steps": 0}

        # First observation: bull candidate (step 1) – no change yet
        r1, state = classify_regime(
            {
                "adx": 30.0,
                "price_vs_ema": 0.05,
                "ema_slope": 0.01,
                "volatility": 0.02,
            },
            prev_state=state,
            config=cfg,
        )
        assert state["regime"] == "balanced"  # Still balanced
        assert state["steps"] == 1
        assert state["candidate"] == "bull"

        # Second observation: bull again – now change
        r2, state = classify_regime(
            {
                "adx": 32.0,
                "price_vs_ema": 0.06,
                "ema_slope": 0.012,
                "volatility": 0.02,
            },
            prev_state=state,
            config=cfg,
        )
        assert state["regime"] == "bull"  # Changed to bull
        assert state["steps"] == 0

        # Third observation: different regime but hysteresis holds
        r3, state = classify_regime(
            {
                "adx": 15.0,  # Ranging candidate
                "price_vs_ema": 0.0,
                "ema_slope": 0.0,
                "volatility": 0.01,
            },
            prev_state=state,
            config=cfg,
        )
        assert state["regime"] == "bull"  # Still bull
        assert state["steps"] == 1
        assert state["candidate"] == "ranging"

    def test_regime_same_resets_steps(self):
        """Test that same regime resets step counter."""
        state = {"regime": "bull", "steps": 1}

        regime, state = classify_regime(
            {
                "adx": 30.0,
                "price_vs_ema": 0.05,
                "ema_slope": 0.01,
                "volatility": 0.02,
            },
            prev_state=state,
        )
        assert state["regime"] == "bull"
        assert state["steps"] == 0  # Reset

    def test_state_contains_features(self):
        """Test that state contains feature values."""
        regime, state = classify_regime(
            {
                "adx": 30.0,
                "price_vs_ema": 0.05,
                "ema_slope": 0.01,
                "volatility": 0.02,
            }
        )
        assert "features" in state
        assert state["features"]["adx"] == 30.0
        assert state["features"]["price_vs_ema"] == 0.05
        assert state["features"]["ema_slope"] == 0.01
        assert state["features"]["volatility"] == 0.02

    def test_classify_regime_respects_configured_adx_thresholds(self):
        """Configured regime-definition thresholds may open a narrower bull band."""
        features = {
            "adx": 24.0,
            "price_vs_ema": 0.03,
            "ema_slope": 0.002,
            "volatility": 0.02,
        }

        default_regime, _default_state = classify_regime(
            features,
            prev_state={"regime": "balanced", "steps": 0},
        )
        tuned_regime, tuned_state = classify_regime(
            features,
            prev_state={"regime": "bull", "steps": 0},
            config={
                "multi_timeframe": {
                    "regime_intelligence": {
                        "regime_definition": {
                            "adx_trend_threshold": 23.0,
                            "adx_range_threshold": 19.0,
                            "slope_threshold": 0.001,
                            "volatility_threshold": 0.05,
                        }
                    }
                }
            },
        )

        assert default_regime == "balanced"
        assert tuned_regime == "bull"
        assert tuned_state["candidate"] == "bull"


class TestDetectRegimeFromCandles:
    """Test regime detection from candle data."""

    def test_bull_from_candles(self):
        """Test bull regime detection from candles."""
        # Strong uptrend
        candles = {
            "close": [100.0 + i * 2 for i in range(60)],  # Rising prices
            "high": [102.0 + i * 2 for i in range(60)],
            "low": [99.0 + i * 2 for i in range(60)],
        }

        regime = detect_regime_from_candles(candles, ema_period=20, adx_period=14)
        # Should detect bull (ADX will be high, price above EMA, positive slope)
        assert regime in ["bull", "balanced"]  # Depends on exact calculation

    def test_ranging_from_candles(self):
        """Test ranging regime detection from candles."""
        # Sideways movement
        candles = {
            "close": [100.0, 101.0, 100.0, 99.0, 100.0] * 12,  # Oscillating
            "high": [102.0, 103.0, 102.0, 101.0, 102.0] * 12,
            "low": [99.0, 100.0, 99.0, 98.0, 99.0] * 12,
        }

        regime = detect_regime_from_candles(candles, ema_period=20, adx_period=14)
        # Should detect ranging or balanced (low ADX, flat)
        assert regime in ["ranging", "balanced"]

    def test_insufficient_data(self):
        """Test with insufficient data."""
        candles = {
            "close": [100.0, 101.0, 102.0],
            "high": [102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0],
        }

        regime = detect_regime_from_candles(candles, ema_period=50, adx_period=14)
        assert regime == "balanced"  # Default when not enough data

    def test_empty_candles(self):
        """Test with empty candles."""
        candles = {"close": [], "high": [], "low": []}
        regime = detect_regime_from_candles(candles)
        assert regime == "balanced"

    def test_detect_regime_from_candles_respects_regime_definition_override(self, monkeypatch):
        """Configured ADX band should affect regime-module classification."""
        from core.indicators import adx as adx_module
        from core.indicators import atr as atr_module
        from core.indicators import ema as ema_module

        candles = {
            "close": [100.0] * 60,
            "high": [101.0] * 60,
            "low": [99.0] * 60,
        }

        monkeypatch.setattr(ema_module, "calculate_ema", lambda *_a, **_k: [97.0] * 60)
        monkeypatch.setattr(adx_module, "calculate_adx", lambda *_a, **_k: [24.0] * 60)
        monkeypatch.setattr(atr_module, "calculate_atr", lambda *_a, **_k: [2.0] * 60)

        default_regime = detect_regime_from_candles(candles, ema_period=20, adx_period=14)
        tuned_regime = detect_regime_from_candles(
            candles,
            ema_period=20,
            adx_period=14,
            config={
                "gates": {"hysteresis_steps": 1},
                "multi_timeframe": {
                    "regime_intelligence": {
                        "regime_definition": {
                            "adx_trend_threshold": 23.0,
                            "adx_range_threshold": 19.0,
                            "slope_threshold": 0.001,
                            "volatility_threshold": 0.05,
                        }
                    }
                },
            },
        )

        assert default_regime == "balanced"
        assert tuned_regime == "bull"

    def test_detect_regime_from_candles_explicit_defaults_match_default_call(self, monkeypatch):
        """Explicit canonical defaults must match the no-override baseline exactly."""
        from core.indicators import adx as adx_module
        from core.indicators import atr as atr_module
        from core.indicators import ema as ema_module

        candles = {
            "close": [100.0] * 60,
            "high": [101.0] * 60,
            "low": [99.0] * 60,
        }

        monkeypatch.setattr(ema_module, "calculate_ema", lambda *_a, **_k: [101.0] * 60)
        monkeypatch.setattr(adx_module, "calculate_adx", lambda *_a, **_k: [18.0] * 60)
        monkeypatch.setattr(atr_module, "calculate_atr", lambda *_a, **_k: [1.0] * 60)

        baseline = detect_regime_from_candles(candles, ema_period=20, adx_period=14)
        explicit_defaults = detect_regime_from_candles(
            candles,
            ema_period=20,
            adx_period=14,
            config={
                "multi_timeframe": {
                    "regime_intelligence": {
                        "regime_definition": {
                            "adx_trend_threshold": 25.0,
                            "adx_range_threshold": 20.0,
                            "slope_threshold": 0.001,
                            "volatility_threshold": 0.05,
                        }
                    }
                }
            },
        )

        assert explicit_defaults == baseline == "balanced"
