from __future__ import annotations

from core.intelligence.regime.authority import (
    detect_authoritative_regime_from_precomputed_ema50,
    detect_authoritative_regime_legacy,
    normalize_authoritative_regime,
)


def test_normalize_authoritative_regime_preserves_allowed_values() -> None:
    assert normalize_authoritative_regime("bull") == "bull"
    assert normalize_authoritative_regime("bear") == "bear"
    assert normalize_authoritative_regime("ranging") == "ranging"
    assert normalize_authoritative_regime("balanced") == "balanced"


def test_normalize_authoritative_regime_falls_back_to_balanced() -> None:
    assert normalize_authoritative_regime(None) == "balanced"
    assert normalize_authoritative_regime("") == "balanced"
    assert normalize_authoritative_regime("trend") == "balanced"
    assert normalize_authoritative_regime("weird_value") == "balanced"


def test_detect_authoritative_regime_from_precomputed_ema50_uses_global_index() -> None:
    window_len = 200
    candles = {
        "close": [1000.0] * window_len,
    }
    ema50 = [1000.0] * 600
    ema50[window_len - 1] = 1100.0
    ema50[500] = 900.0

    regime = detect_authoritative_regime_from_precomputed_ema50(
        candles,
        {
            "_global_index": 500,
            "precomputed_features": {"ema_50": ema50},
        },
    )

    assert regime == "bull"


def test_detect_authoritative_regime_from_precomputed_ema50_falls_back_to_local_index() -> None:
    candles = {
        "close": [1000.0] * 3,
    }
    regime = detect_authoritative_regime_from_precomputed_ema50(
        candles,
        {
            "precomputed_features": {"ema_50": [1000.0, 1000.0, 1100.0]},
        },
    )

    assert regime == "bear"


def test_detect_authoritative_regime_from_precomputed_ema50_returns_balanced_for_zero_ema() -> None:
    regime = detect_authoritative_regime_from_precomputed_ema50(
        {"close": [1000.0]},
        {
            "precomputed_features": {"ema_50": [0.0]},
        },
    )

    assert regime == "balanced"


def test_detect_authoritative_regime_legacy_uses_fallback_when_precomputed_path_unavailable() -> (
    None
):
    calls: list[dict[str, object]] = []

    def _fallback(candles: dict[str, object]) -> str:
        calls.append(candles)
        return "ranging"

    regime = detect_authoritative_regime_legacy(
        {"close": [1000.0]},
        {"precomputed_features": {}},
        fallback_detect_regime_unified=_fallback,
    )

    assert regime == "ranging"
    assert calls == [{"close": [1000.0]}]
