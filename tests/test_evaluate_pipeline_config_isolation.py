from __future__ import annotations

from types import SimpleNamespace

import core.strategy.evaluate as evaluate_mod


def _minimal_candles() -> dict:
    # Keep timestamps numeric so evaluate_pipeline's staleness check can float() them.
    return {
        "timestamp": [0.0, 3600.0],
        "open": [1.0, 1.0],
        "high": [1.0, 1.0],
        "low": [1.0, 1.0],
        "close": [1.0, 1.0],
        "volume": [1.0, 1.0],
    }


def test_evaluate_pipeline_does_not_merge_champion_in_backtest_mode(monkeypatch):
    dummy_champion = SimpleNamespace(
        config={"champion_only": {"sentinel": True}, "thresholds": {"entry_conf_overall": 0.11}},
        source="dummy",
    )
    monkeypatch.setattr(
        evaluate_mod.champion_loader,
        "load_cached",
        lambda symbol, timeframe: dummy_champion,
    )

    captured: dict[str, object] = {}

    def fake_extract_features(candles, *, config, timeframe, symbol, now_index):
        captured["config"] = config
        return {}, {}

    monkeypatch.setattr(evaluate_mod, "extract_features", fake_extract_features)
    monkeypatch.setattr(
        evaluate_mod,
        "predict_proba_for",
        lambda *args, **kwargs: ({"buy": 0.6, "sell": 0.4}, {"schema": [], "versions": {}}),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "compute_confidence",
        lambda *args, **kwargs: ({"buy": 0.6, "sell": 0.4, "overall": 0.6}, {"versions": {}}),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "decide",
        lambda *args, **kwargs: ("NONE", {"versions": {}, "reasons": [], "state_out": {}}),
    )

    candles = _minimal_candles()
    configs = {
        "_global_index": 1,
        "thresholds": {"entry_conf_overall": 0.5},
        # Ensure regime detection stays on the fast-path (no imports/heavy logic).
        "precomputed_features": {"ema_50": [1.0, 1.0]},
    }

    evaluate_mod.evaluate_pipeline(
        candles,
        policy={"symbol": "tBTCUSD", "timeframe": "1h"},
        configs=configs,
        state={},
    )

    effective = captured["config"]
    assert isinstance(effective, dict)
    assert "champion_only" not in effective, "Champion config must not leak into backtest mode"
    assert effective["thresholds"]["entry_conf_overall"] == 0.5
    assert effective.get("meta", {}).get("champion_source") == "explicit_backtest_config"


def test_evaluate_pipeline_merges_champion_in_live_mode(monkeypatch):
    dummy_champion = SimpleNamespace(
        config={"champion_only": {"sentinel": True}, "thresholds": {"entry_conf_overall": 0.11}},
        source="dummy",
    )
    monkeypatch.setattr(
        evaluate_mod.champion_loader,
        "load_cached",
        lambda symbol, timeframe: dummy_champion,
    )

    captured: dict[str, object] = {}

    def fake_extract_features(candles, *, config, timeframe, symbol, now_index):
        captured["config"] = config
        return {}, {}

    monkeypatch.setattr(evaluate_mod, "extract_features", fake_extract_features)
    monkeypatch.setattr(
        evaluate_mod,
        "predict_proba_for",
        lambda *args, **kwargs: ({"buy": 0.6, "sell": 0.4}, {"schema": [], "versions": {}}),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "compute_confidence",
        lambda *args, **kwargs: ({"buy": 0.6, "sell": 0.4, "overall": 0.6}, {"versions": {}}),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "decide",
        lambda *args, **kwargs: ("NONE", {"versions": {}, "reasons": [], "state_out": {}}),
    )

    candles = _minimal_candles()
    configs = {
        "thresholds": {"entry_conf_overall": 0.5},
        "precomputed_features": {"ema_50": [1.0, 1.0]},
    }

    evaluate_mod.evaluate_pipeline(
        candles,
        policy={"symbol": "tBTCUSD", "timeframe": "1h"},
        configs=configs,
        state={},
    )

    effective = captured["config"]
    assert isinstance(effective, dict)
    assert "champion_only" in effective, "Champion config should be used as baseline in live mode"
    assert effective["thresholds"]["entry_conf_overall"] == 0.5
    assert effective.get("meta", {}).get("champion_source") == "dummy"
