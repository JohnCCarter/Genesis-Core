from __future__ import annotations

import core.strategy.features_asof as features_asof
from core.strategy.features_asof_parts.extraction_context_utils import prepare_extraction_context


def _make_candles(length: int = 90) -> dict[str, list[float]]:
    close = [100.0 + (i * 0.25) + (0.1 if i % 2 == 0 else -0.1) for i in range(length)]
    return {
        "open": [value - 0.2 for value in close],
        "high": [value + 0.5 for value in close],
        "low": [value - 0.5 for value in close],
        "close": close,
        "volume": [1000.0 + i for i in range(length)],
    }


def test_prepare_extraction_context_remaps_precompute_to_local_window() -> None:
    candles = _make_candles(90)
    precomputed = {
        "rsi_14": [float(i) for i in range(150)],
        "atr_14": [float(i) / 10.0 for i in range(150)],
    }
    config = {
        "_global_index": 100,
        "precomputed_features": precomputed,
    }

    ctx = prepare_extraction_context(
        candles,
        60,
        config,
        features_asof._remap_precomputed_features,
    )

    assert ctx.lookup_idx == 100
    assert ctx.window_start_idx == 40
    assert ctx.pre_idx == 60
    assert ctx.pre["rsi_14"][0] == 40.0
    assert ctx.pre["rsi_14"][60] == 100.0
    assert len(ctx.closes) == 61


def test_prepare_extraction_context_uses_default_and_override_atr_period() -> None:
    candles = _make_candles(90)

    default_ctx = prepare_extraction_context(
        candles,
        60,
        {},
        features_asof._remap_precomputed_features,
    )
    override_ctx = prepare_extraction_context(
        candles,
        60,
        {"thresholds": {"signal_adaptation": {"atr_period": 21}}},
        features_asof._remap_precomputed_features,
    )

    assert default_ctx.atr_period == 14
    assert override_ctx.atr_period == 21


def test_prepare_extraction_context_disables_requested_precompute_without_data(
    monkeypatch,
) -> None:
    candles = _make_candles(90)
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")

    ctx = prepare_extraction_context(
        candles,
        60,
        {},
        features_asof._remap_precomputed_features,
    )

    assert ctx.warn_precompute_missing is True
    assert ctx.use_precompute is False
    assert ctx.pre == {}


def test_extract_features_backtest_precompute_fallback_warns_only_once(monkeypatch) -> None:
    candles = _make_candles(90)
    warnings: list[str] = []

    class _FakeLogger:
        def debug(self, *_args, **_kwargs) -> None:
            return None

        def warning(self, message: str) -> None:
            warnings.append(message)

    original_logger = features_asof._log
    original_warn_once = features_asof._PRECOMPUTE_WARN_ONCE
    try:
        features_asof._feature_cache.clear()
        features_asof._log = _FakeLogger()
        features_asof._PRECOMPUTE_WARN_ONCE = False
        monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")

        features_asof.extract_features_backtest(candles, 60)
        features_asof.extract_features_backtest(candles, 61)

        assert len(warnings) == 1
        assert "GENESIS_PRECOMPUTE_FEATURES=1 men precomputed_features saknas" in warnings[0]
        assert features_asof._PRECOMPUTE_WARN_ONCE is True
    finally:
        features_asof._log = original_logger
        features_asof._PRECOMPUTE_WARN_ONCE = original_warn_once
        features_asof._feature_cache.clear()
