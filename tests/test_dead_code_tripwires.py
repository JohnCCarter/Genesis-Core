from __future__ import annotations

from datetime import UTC, datetime

import pytest


def test_deprecated_features_module_delegates_to_features_asof(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Runtime-bevis: legacy-blocket i core.strategy.features ska vara oexekverbart.

    Vi verifierar detta genom att monkeypatcha aliaset `_extract_features_asof` i
    `core.strategy.features` och kräva att `extract_features()` returnerar exakt
    vad den delegationen returnerar.

    Om legacy-koden efter `return` av misstag skulle aktiveras i framtiden, kommer
    detta test sannolikt att börja faila (antingen p.g.a. annan returform eller
    att patched funktion inte anropas).
    """

    import core.strategy.features as legacy

    sentinel_features = {"_sentinel": 1.0}
    sentinel_meta = {"_sentinel": True}

    calls: dict[str, int] = {"n": 0}

    def _fake_asof(*args, **kwargs):  # type: ignore[no-untyped-def]
        calls["n"] += 1
        return sentinel_features, sentinel_meta

    monkeypatch.setattr(legacy, "_extract_features_asof", _fake_asof)

    candles = {
        "open": [1.0, 2.0],
        "high": [2.0, 3.0],
        "low": [0.5, 1.5],
        "close": [1.5, 2.5],
        "volume": [10.0, 11.0],
    }
    feats, meta = legacy.extract_features(candles, config={}, timeframe="1h", symbol="tBTCUSD")

    assert calls["n"] == 1
    assert feats is sentinel_features
    assert meta is sentinel_meta


def test_position_tracker_does_not_use_legacy_close_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """Runtime-bevis: PositionTracker ska inte använda _close_position_legacy().

    Vi installerar en tripwire som kastar om legacy-metoden anropas och kör en
    minimal sequence som öppnar + stänger en position via nuvarande publika API.
    """

    from core.backtest.position_tracker import PositionTracker

    pt = PositionTracker(initial_capital=1000.0)

    def _boom(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("_close_position_legacy() should not be called")

    monkeypatch.setattr(pt, "_close_position_legacy", _boom)

    ts0 = datetime(2020, 1, 1, tzinfo=UTC)
    ts1 = datetime(2020, 1, 2, tzinfo=UTC)

    # Open LONG
    r0 = pt.execute_action("LONG", size=1.0, price=100.0, timestamp=ts0, symbol="tTESTBTC:TESTUSD")
    assert r0["executed"] is True

    # Close by opposite signal (this uses _close_position -> close_position_with_reason)
    r1 = pt.execute_action("SHORT", size=1.0, price=101.0, timestamp=ts1, symbol="tTESTBTC:TESTUSD")
    assert r1["executed"] is True

    # execute_action() overwrites the intermediate close reason with "opened" after opening the new position.
    assert pt.position is not None
    assert pt.position.side == "SHORT"

    # Ensure we recorded at least one trade
    assert len(pt.trades) >= 1
    assert any(t.exit_reason == "OPPOSITE_SIGNAL" for t in pt.trades)
