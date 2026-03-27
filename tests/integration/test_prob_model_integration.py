from __future__ import annotations

import json

import pytest

from core.strategy.model_registry import ModelRegistry
from core.strategy.prob_model import predict_proba, predict_proba_for


def test_prob_model_integration_minimal():
    reg = ModelRegistry()
    meta = reg.get_meta("tBTCUSD", "1m")
    assert isinstance(meta, dict)
    feats = dict.fromkeys(meta.get("schema", []), 0.0)
    # Wrapper kommer justeras senare; tills dess validerar vi basfunktionen
    out = predict_proba(
        feats,
        schema=tuple(meta.get("schema", [])),
        buy_w=meta.get("buy", {}).get("w"),
        buy_b=meta.get("buy", {}).get("b", 0.0),
        sell_w=meta.get("sell", {}).get("w"),
        sell_b=meta.get("sell", {}).get("b", 0.0),
        calib_buy=(
            meta.get("buy", {}).get("calib", {}).get("a", 1.0),
            meta.get("buy", {}).get("calib", {}).get("b", 0.0),
        ),
        calib_sell=(
            meta.get("sell", {}).get("calib", {}).get("a", 1.0),
            meta.get("sell", {}).get("calib", {}).get("b", 0.0),
        ),
    )
    assert set(out.keys()) == {"buy", "sell", "hold"}


def test_prob_model_wrapper_applies_calibration_and_meta():
    reg = ModelRegistry()
    meta = reg.get_meta("tBTCUSD", "1m")
    feats = dict.fromkeys(meta.get("schema", []), 0.0)
    probas, pmeta = predict_proba_for("tBTCUSD", "1m", feats, model_meta=meta)
    assert set(probas.keys()) == {"buy", "sell", "hold"}
    assert "versions" in pmeta and isinstance(pmeta["versions"], dict)


def test_prob_model_research_meta_path_can_override_balanced_calibration(tmp_path) -> None:
    reg = ModelRegistry()
    meta = reg.get_meta("tBTCUSD", "3h")
    assert isinstance(meta, dict)

    research_meta = json.loads(json.dumps(meta))
    buy_ranging = research_meta["calibration_by_regime"]["buy"]["ranging"]
    sell_ranging = research_meta["calibration_by_regime"]["sell"]["ranging"]
    research_meta["calibration_by_regime"]["buy"]["balanced"] = dict(buy_ranging)
    research_meta["calibration_by_regime"]["sell"]["balanced"] = dict(sell_ranging)

    research_path = tmp_path / "tBTCUSD_3h_research.json"
    research_path.write_text(json.dumps(research_meta), encoding="utf-8")

    feats = dict.fromkeys(meta.get("schema", []), 0.0)
    _default_probas, default_meta = predict_proba_for("tBTCUSD", "3h", feats, regime="balanced")
    _research_probas, research_meta_out = predict_proba_for(
        "tBTCUSD",
        "3h",
        feats,
        regime="balanced",
        research_model_meta_path=str(research_path),
    )

    assert default_meta["calibration_used"]["regime"] == "balanced"
    assert default_meta["calibration_used"]["buy_calib"] == {"a": 1.0, "b": 0.0}
    assert default_meta["calibration_used"]["sell_calib"] == {"a": 1.0, "b": 0.0}
    assert research_meta_out["model_meta_source"] == "research_model_meta_path"
    assert research_meta_out["calibration_used"]["buy_calib"] == {
        "a": buy_ranging["a"],
        "b": buy_ranging["b"],
    }
    assert research_meta_out["calibration_used"]["sell_calib"] == {
        "a": sell_ranging["a"],
        "b": sell_ranging["b"],
    }


def test_prob_model_research_meta_path_rejects_active_model_paths() -> None:
    reg = ModelRegistry()
    meta = reg.get_meta("tBTCUSD", "3h")
    assert isinstance(meta, dict)
    feats = dict.fromkeys(meta.get("schema", []), 0.0)

    with pytest.raises(ValueError, match="research_model_meta_path_points_to_active_model_path"):
        predict_proba_for(
            "tBTCUSD",
            "3h",
            feats,
            regime="balanced",
            research_model_meta_path="config/models/tBTCUSD_3h.json",
        )
