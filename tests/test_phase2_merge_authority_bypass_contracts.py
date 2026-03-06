from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
from typing import Any

import core.strategy.evaluate as evaluate_mod
from core.config.authority import _deep_merge_dicts
from core.strategy.evaluate import _deep_merge as _evaluate_deep_merge
from core.strategy.regime_intelligence import resolve_authority_mode_with_source


def _minimal_candles() -> dict[str, list[float]]:
    return {
        "timestamp": [0.0, 3600.0],
        "open": [1.0, 1.0],
        "high": [1.0, 1.0],
        "low": [1.0, 1.0],
        "close": [1.0, 1.0],
        "volume": [1.0, 1.0],
    }


def test_deep_merge_contract_current_semantics_and_immutability() -> None:
    """Contract lock for current deep-merge behavior.

    Audit coverage:
    - DUP-001 (duplicate deep-merge implementations)
    - CFG-002 (authority write-merge semantics)
    - CFG-007 (merge path parity concerns)
    """

    base = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "nested": {"keep": True, "replace_me": 1},
        },
        "risk": {"risk_map": {"ranging": 1.0}},
        "list_value": [1, 2],
        "scalar": "base",
    }
    override = {
        "thresholds": {
            "nested": {"replace_me": 99, "new_leaf": "x"},
            "new_top": 7,
        },
        "risk": {"risk_map": {"bull": 1.3}},
        "list_value": [9],
        "scalar": {"replaced": True},
        "added": "yes",
    }

    base_before = deepcopy(base)
    override_before = deepcopy(override)

    expected = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "nested": {"keep": True, "replace_me": 99, "new_leaf": "x"},
            "new_top": 7,
        },
        "risk": {"risk_map": {"ranging": 1.0, "bull": 1.3}},
        "list_value": [9],
        "scalar": {"replaced": True},
        "added": "yes",
    }

    assert _deep_merge_dicts(base, override) == expected
    assert _evaluate_deep_merge(base, override) == expected

    assert base == base_before
    assert override == override_before


def test_champion_merge_bypass_contract_backtest_vs_live(monkeypatch) -> None:
    """Contract lock for champion merge/bypass decision behavior.

    Audit coverage:
    - DUP-003 (multiple bypass mechanisms)
    - CFG-004 (explicit backtest flag semantics)
    - CFG-005 (evaluate path bypass behavior)
    """

    dummy_champion = SimpleNamespace(
        config={
            "champion_only": {"sentinel": True},
            "thresholds": {"entry_conf_overall": 0.11},
        },
        source="dummy",
    )
    monkeypatch.setattr(
        evaluate_mod.champion_loader,
        "load_cached",
        lambda _symbol, _timeframe: dummy_champion,
    )

    captured: dict[str, dict[str, Any]] = {}

    def fake_extract_features_backtest(candles, asof_bar, *, config, timeframe, symbol):
        _ = (candles, asof_bar, timeframe, symbol)
        captured["backtest"] = config
        return {}, {}

    def fake_extract_features_live(candles, *, config, timeframe, symbol):
        _ = (candles, timeframe, symbol)
        captured["live"] = config
        return {}, {}

    monkeypatch.setattr(evaluate_mod, "extract_features_backtest", fake_extract_features_backtest)
    monkeypatch.setattr(evaluate_mod, "extract_features_live", fake_extract_features_live)
    monkeypatch.setattr(
        evaluate_mod,
        "predict_proba_for",
        lambda *_args, **_kwargs: ({"buy": 0.6, "sell": 0.4}, {"schema": [], "versions": {}}),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "compute_confidence",
        lambda *_args, **_kwargs: ({"buy": 0.6, "sell": 0.4, "overall": 0.6}, {"versions": {}}),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "decide",
        lambda *_args, **_kwargs: ("NONE", {"versions": {}, "reasons": [], "state_out": {}}),
    )

    candles = _minimal_candles()

    backtest_cfg = {
        "_global_index": 1,
        "thresholds": {"entry_conf_overall": 0.5},
        "precomputed_features": {"ema_50": [1.0, 1.0]},
    }
    evaluate_mod.evaluate_pipeline(
        candles,
        policy={"symbol": "tBTCUSD", "timeframe": "1h"},
        configs=deepcopy(backtest_cfg),
        state={},
    )

    live_cfg = {
        "thresholds": {"entry_conf_overall": 0.5},
        "precomputed_features": {"ema_50": [1.0, 1.0]},
    }
    evaluate_mod.evaluate_pipeline(
        candles,
        policy={"symbol": "tBTCUSD", "timeframe": "1h"},
        configs=deepcopy(live_cfg),
        state={},
    )

    backtest_effective = captured["backtest"]
    live_effective = captured["live"]

    assert "champion_only" not in backtest_effective
    assert backtest_effective["thresholds"]["entry_conf_overall"] == 0.5
    assert backtest_effective.get("meta", {}).get("champion_source") == "explicit_backtest_config"

    assert "champion_only" in live_effective
    assert live_effective["thresholds"]["entry_conf_overall"] == 0.5
    assert live_effective.get("meta", {}).get("champion_source") == "dummy"


def test_authority_mode_precedence_contract_matrix() -> None:
    """Direct contract lock for authority-mode normalization and precedence.

    Audit coverage:
    - DUP-002 (authority-mode logic duplicated across layers)
    - CFG-008 (defaults/fallbacks precedence drift risk)
    """

    scenarios = [
        ({}, ("legacy", "default_legacy")),
        (
            {"regime_unified": {"authority_mode": "regime_module"}},
            ("regime_module", "regime_unified.authority_mode"),
        ),
        (
            {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": " LEGACY "}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            ("legacy", "multi_timeframe.regime_intelligence.authority_mode"),
        ),
        (
            {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode"}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            ("legacy", "canonical_invalid_fallback_legacy"),
        ),
        (
            {"regime_unified": {"authority_mode": "invalid_mode"}},
            ("legacy", "alias_invalid_fallback_legacy"),
        ),
    ]

    for cfg, expected in scenarios:
        assert resolve_authority_mode_with_source(cfg) == expected
