from __future__ import annotations


def test_evaluate_pipeline_regime_uses_global_index_for_precomputed_ema50(monkeypatch):
    """Regression: windowed candles + full precomputed EMA50 must use _global_index.

    Bug behavior (before fix): index EMA50 by len(closes)-1 (local window index), which is
    wrong when candles are windowed (e.g. last 200 bars) but precomputed features are full-series.
    """

    # Disable metrics side-effects
    monkeypatch.setenv("GENESIS_DISABLE_METRICS", "1")

    from core.strategy import evaluate as ev

    captured: dict[str, str | None] = {"regime": None}

    # --- Stubs / monkeypatches to isolate regime selection ---
    class _DummyChampion:
        config: dict = {}
        source: str = "dummy"

    monkeypatch.setattr(ev.champion_loader, "load_cached", lambda *_a, **_k: _DummyChampion())

    def fake_extract_features(*_a, **_k):
        feats = {"atr_14": 1.0}
        meta = {
            "current_atr_used": 1.0,
            "atr_percentiles": None,
            "htf_fibonacci": {"available": False},
            "ltf_fibonacci": {"available": False},
        }
        return feats, meta

    def fake_extract_features_backtest(*_a, **_k):
        return fake_extract_features(*_a, **_k)

    monkeypatch.setattr(ev, "extract_features_backtest", fake_extract_features_backtest)

    def fake_predict_proba_for(_symbol, _timeframe, _feats, *, regime=None):
        captured["regime"] = str(regime) if regime is not None else None
        return {"up": 0.5, "down": 0.5}, {"schema": [], "versions": {}}

    monkeypatch.setattr(ev, "predict_proba_for", fake_predict_proba_for)

    def fake_compute_confidence(_probas, **_kwargs):
        return {"buy": 0.0, "sell": 0.0, "overall": 0.0}, {}

    monkeypatch.setattr(ev, "compute_confidence", fake_compute_confidence)

    monkeypatch.setattr(ev, "log_fib_flow", lambda *_a, **_k: None)

    def fake_decide(_policy, **_kwargs):
        return "NONE", {"size": 0.0, "reasons": [], "state_out": {}}

    monkeypatch.setattr(ev, "decide", fake_decide)

    # --- Build windowed candles + full precomputed EMA50 ---
    window_len = 200
    candles = {
        "open": [1.0] * window_len,
        "high": [2.0] * window_len,
        "low": [0.5] * window_len,
        "close": [1000.0] * window_len,
        "volume": [1.0] * window_len,
        "timestamp": list(range(window_len)),
    }

    ema_len = 600
    ema50 = [1000.0] * ema_len
    # Current price is 1000.0. Threshold is 2%.
    # If code (incorrectly) uses local index 199, EMA=1100 -> trend negative (bear).
    ema50[window_len - 1] = 1100.0
    # Correct global index (500) should have EMA=900 -> trend positive (bull).
    ema50[500] = 900.0

    configs = {
        "_global_index": 500,
        "precomputed_features": {"ema_50": ema50},
        "quality": {"pipeline": {}},
        "meta": {},
    }

    result, _meta = ev.evaluate_pipeline(
        candles,
        policy={"symbol": "tBTCUSD", "timeframe": "1h"},
        configs=configs,
        state={},
    )

    assert captured["regime"] == "bull"
    assert result["regime"] == "bull"
