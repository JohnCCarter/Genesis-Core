from __future__ import annotations

from types import SimpleNamespace

import pytest

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


def _patch_champion_loader(monkeypatch, *, source: str = "dummy"):
    dummy_champion = SimpleNamespace(
        config={"champion_only": {"sentinel": True}, "thresholds": {"entry_conf_overall": 0.11}},
        source=source,
    )
    monkeypatch.setattr(
        evaluate_mod.champion_loader,
        "load_cached",
        lambda *_args, **_kwargs: dummy_champion,
    )


def _patch_common_pipeline_stubs(monkeypatch) -> None:
    monkeypatch.setattr(
        evaluate_mod,
        "predict_proba_for",
        lambda *_args, **_kwargs: ({"buy": 0.6, "sell": 0.4}, {"schema": [], "versions": {}}),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "compute_confidence",
        lambda *_args, **_kwargs: (
            {"buy": 0.6, "sell": 0.4, "overall": 0.6},
            {"versions": {}},
        ),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "decide",
        lambda *_args, **_kwargs: ("NONE", {"versions": {}, "reasons": [], "state_out": {}}),
    )


def test_evaluate_pipeline_does_not_merge_champion_in_backtest_mode(monkeypatch):
    _patch_champion_loader(monkeypatch, source="dummy")

    captured: dict[str, object] = {}

    def fake_extract_features_backtest(candles, asof_bar, *, config, timeframe, symbol):
        _ = (candles, timeframe, symbol)
        captured["config"] = config
        captured["asof_bar"] = asof_bar
        return {}, {}

    monkeypatch.setattr(evaluate_mod, "extract_features_backtest", fake_extract_features_backtest)
    _patch_common_pipeline_stubs(monkeypatch)

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
    _patch_champion_loader(monkeypatch, source="dummy")

    captured: dict[str, object] = {}

    def fake_extract_features_live(candles, *, config, timeframe, symbol):
        _ = (candles, timeframe, symbol)
        captured["config"] = config
        return {}, {}

    monkeypatch.setattr(evaluate_mod, "extract_features_live", fake_extract_features_live)
    _patch_common_pipeline_stubs(monkeypatch)

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


def test_evaluate_pipeline_passes_research_model_meta_path_only_for_research_code_experiment(
    monkeypatch,
):
    _patch_champion_loader(monkeypatch, source="dummy")

    captured: dict[str, object] = {}

    def fake_extract_features_backtest(candles, asof_bar, *, config, timeframe, symbol):
        _ = (candles, asof_bar, config, timeframe, symbol)
        return {}, {}

    def fake_predict_proba_for(
        _symbol, _timeframe, _feats, *, regime=None, research_model_meta_path=None
    ):
        captured["regime"] = regime
        captured["research_model_meta_path"] = research_model_meta_path
        return {"buy": 0.6, "sell": 0.4}, {"schema": [], "versions": {}}

    monkeypatch.setattr(evaluate_mod, "extract_features_backtest", fake_extract_features_backtest)
    monkeypatch.setattr(evaluate_mod, "predict_proba_for", fake_predict_proba_for)
    monkeypatch.setattr(
        evaluate_mod,
        "compute_confidence",
        lambda *_args, **_kwargs: (
            {"buy": 0.6, "sell": 0.4, "overall": 0.6},
            {"versions": {}},
        ),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "decide",
        lambda *_args, **_kwargs: ("NONE", {"versions": {}, "reasons": [], "state_out": {}}),
    )

    evaluate_mod.evaluate_pipeline(
        _minimal_candles(),
        policy={"symbol": "tBTCUSD", "timeframe": "3h"},
        configs={
            "_global_index": 1,
            "precomputed_features": {"ema_50": [1.0, 1.0]},
            "meta": {
                "run_intent": "research_code_experiment",
                "research_model_meta_path": (
                    "config/research/model_meta/ri_regime_calibration_slice1/tBTCUSD_3h.json"
                ),
            },
        },
        state={},
    )

    assert (
        captured["research_model_meta_path"]
        == "config/research/model_meta/ri_regime_calibration_slice1/tBTCUSD_3h.json"
    )


def test_evaluate_pipeline_rejects_research_model_meta_path_without_research_code_experiment(
    monkeypatch,
):
    _patch_champion_loader(monkeypatch, source="dummy")
    monkeypatch.setattr(
        evaluate_mod,
        "extract_features_backtest",
        lambda *_args, **_kwargs: ({}, {}),
    )
    _patch_common_pipeline_stubs(monkeypatch)

    with pytest.raises(
        ValueError, match="research_model_meta_path_requires_research_code_experiment"
    ):
        evaluate_mod.evaluate_pipeline(
            _minimal_candles(),
            policy={"symbol": "tBTCUSD", "timeframe": "3h"},
            configs={
                "_global_index": 1,
                "precomputed_features": {"ema_50": [1.0, 1.0]},
                "meta": {
                    "research_model_meta_path": (
                        "config/research/model_meta/ri_regime_calibration_slice1/tBTCUSD_3h.json"
                    ),
                },
            },
            state={},
        )
