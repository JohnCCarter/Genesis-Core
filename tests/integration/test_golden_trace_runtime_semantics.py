from __future__ import annotations

from copy import deepcopy

import pytest

from core.backtest.engine import BacktestEngine
from core.strategy.decision import decide


def test_effective_config_fingerprint_scrubs_volatile_keys() -> None:
    """Golden trace: effective_config_fingerprint must ignore volatile/huge keys.

    Contract (BacktestEngine._config_fingerprint):
    - ignores configs['_global_index']
    - ignores configs['precomputed_features']
    - ignores configs['meta']['champion_loaded_at']

    If any of these start affecting the fingerprint, reproducibility tooling becomes noisy
    and configs appear to "drift" even when the effective decision config is identical.
    """

    engine = BacktestEngine(symbol="tBTCUSD", timeframe="1h")

    base = {
        "meta": {
            "skip_champion_merge": True,
            "champion_loaded_at": "2026-01-01T00:00:00Z",
        },
        "thresholds": {"entry_conf_overall": 0.42},
        "risk": {"risk_map": [[0.4, 0.01]]},
        "_global_index": 123,
        "precomputed_features": {"ema_50": [1.0, 2.0, 3.0]},
    }

    fp_base = engine._config_fingerprint(base)

    mutated = deepcopy(base)
    mutated["_global_index"] = 999
    mutated["precomputed_features"] = {"ema_50": [9.0] * 100}
    mutated.setdefault("meta", {})["champion_loaded_at"] = "2099-12-31T23:59:59Z"

    fp_mutated = engine._config_fingerprint(mutated)
    assert fp_mutated == fp_base

    changed = deepcopy(base)
    changed["thresholds"]["entry_conf_overall"] = 0.43
    fp_changed = engine._config_fingerprint(changed)
    assert fp_changed != fp_base


def test_signal_adaptation_zone_overrides_base_thresholds() -> None:
    """Golden trace: signal_adaptation must override base thresholds when active.

    This locks the key runtime behavior that frequently makes params "inert":
    - thresholds.entry_conf_overall is overridden by zone.entry_conf_overall
    - thresholds.regime_proba is overridden by zone.regime_proba
    """

    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            # Base thresholds intentionally stricter than the zone.
            "entry_conf_overall": 0.95,
            "regime_proba": {"balanced": 0.90},
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {
                    "mid": {
                        "entry_conf_overall": 0.60,
                        "regime_proba": {"balanced": 0.60},
                    }
                },
            },
        },
        "risk": {"risk_map": [[0.60, 0.01]]},
    }

    # Choose ATR in the mid zone: p40 < atr <= p80
    state = {
        "current_atr": 2.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    action, meta = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.65, "sell": 0.20},
        confidence={"buy": 0.65, "sell": 0.20},
        regime="balanced",
        state=state,
        risk_ctx={},
        cfg=cfg,
    )

    reasons = list(meta.get("reasons") or [])
    assert any(r.startswith("ZONE:mid@") for r in reasons)
    assert action == "LONG"


def test_signal_adaptation_enabled_false_uses_base_entry_threshold() -> None:
    """Controlled intervention: enabled=false must restore base entry threshold ownership."""

    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.80,
            "regime_proba": {"balanced": 0.50},
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {
                    "mid": {
                        "entry_conf_overall": 0.60,
                        "regime_proba": {"balanced": 0.50},
                    }
                },
            },
        },
        "risk": {"risk_map": [[0.50, 0.01]]},
    }

    state = {
        "current_atr": 2.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    active_action, active_meta = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.65, "sell": 0.20},
        confidence={"buy": 0.65, "sell": 0.20},
        regime="balanced",
        state=state,
        risk_ctx={},
        cfg=cfg,
    )

    disabled_cfg = deepcopy(cfg)
    disabled_cfg["thresholds"]["signal_adaptation"]["enabled"] = False
    disabled_action, disabled_meta = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.65, "sell": 0.20},
        confidence={"buy": 0.65, "sell": 0.20},
        regime="balanced",
        state=state,
        risk_ctx={},
        cfg=disabled_cfg,
    )

    active_reasons = list(active_meta.get("reasons") or [])
    disabled_reasons = list(disabled_meta.get("reasons") or [])

    assert active_action == "LONG"
    assert any(r.startswith("ZONE:mid@0.600") for r in active_reasons)
    assert disabled_action == "NONE"
    assert any(r.startswith("ZONE:base@0.800") for r in disabled_reasons)
    assert "CONF_TOO_LOW" in disabled_reasons


def test_signal_adaptation_enabled_false_uses_base_regime_threshold() -> None:
    """Controlled intervention: enabled=false must restore base regime threshold ownership."""

    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.60,
            "regime_proba": {"balanced": 0.75},
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {
                    "mid": {
                        "entry_conf_overall": 0.60,
                        "regime_proba": {"balanced": 0.60},
                    }
                },
            },
        },
        "risk": {"risk_map": [[0.50, 0.01]]},
    }

    state = {
        "current_atr": 2.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    active_action, active_meta = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.65, "sell": 0.20},
        confidence={"buy": 0.65, "sell": 0.20},
        regime="balanced",
        state=state,
        risk_ctx={},
        cfg=cfg,
    )

    disabled_cfg = deepcopy(cfg)
    disabled_cfg["thresholds"]["signal_adaptation"]["enabled"] = False
    disabled_action, disabled_meta = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.65, "sell": 0.20},
        confidence={"buy": 0.65, "sell": 0.20},
        regime="balanced",
        state=state,
        risk_ctx={},
        cfg=disabled_cfg,
    )

    active_reasons = list(active_meta.get("reasons") or [])
    disabled_reasons = list(disabled_meta.get("reasons") or [])

    assert active_action == "LONG"
    assert any(r.startswith("ZONE:mid@0.600") for r in active_reasons)
    assert disabled_action == "NONE"
    assert any(r.startswith("ZONE:base@0.600") for r in disabled_reasons)
    assert "CONF_TOO_LOW" not in disabled_reasons


def test_signal_adaptation_missing_percentiles_locks_low_zone() -> None:
    """Golden trace: unknown atr_period falls back to p40=p80=atr => low zone.

    Current decision semantics:
    - if atr_percentiles lacks the requested atr_period, p40/p80 default to `atr`
    - since atr <= p40, zone becomes "low"

    This test is intentionally strict: if behavior changes, we want an explicit decision.
    """

    cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.99,
            "regime_proba": {"balanced": 0.99},
            "signal_adaptation": {
                # 20 is not produced by features_asof percentiles (typically 14/28/56)
                "atr_period": 20,
                "zones": {"low": {"entry_conf_overall": 0.30, "regime_proba": {"balanced": 0.30}}},
            },
        },
        "risk": {"risk_map": [[0.30, 0.01]]},
    }

    state = {
        "current_atr": 2.0,
        # Only unrelated percentiles exist.
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    action, meta = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.60, "sell": 0.10},
        confidence={"buy": 0.60, "sell": 0.10},
        regime="balanced",
        state=state,
        risk_ctx={},
        cfg=cfg,
    )

    reasons = list(meta.get("reasons") or [])
    assert any(r.startswith("ZONE:low@") for r in reasons)
    assert action == "LONG"


def test_research_bull_high_persistence_override_disabled_preserves_runtime_parity() -> None:
    base_cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "risk": {"risk_map": [[0.36, 0.01]]},
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
    }
    state = {
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    action_base, meta_base = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=base_cfg,
    )

    cfg_disabled = deepcopy(base_cfg)
    cfg_disabled["multi_timeframe"] = {
        "research_bull_high_persistence_override": {
            "enabled": False,
            "min_persistence": 2,
            "max_probability_gap": 0.06,
        }
    }
    action_disabled, meta_disabled = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=cfg_disabled,
    )

    assert action_base == action_disabled == "NONE"
    assert meta_base.get("reasons") == meta_disabled.get("reasons")
    assert meta_base.get("state_out") == meta_disabled.get("state_out")


def test_current_atr_selective_high_vol_multiplier_absent_matches_enabled_false() -> None:
    base_cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "regime_proba": {"bull": 0.6},
        },
        "risk": {
            "risk_map": [[0.6, 0.01]],
            "volatility_sizing": {
                "enabled": True,
                "high_vol_threshold": 80,
                "high_vol_multiplier": 0.9,
                "atr_period": 14,
            },
            "min_combined_multiplier": 0.01,
        },
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
    }
    state = {
        "current_atr": 4.0,
        "atr_percentiles": {"14": {"p80": 3.0}},
    }

    action_base, meta_base = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.6, "sell": 0.4},
        confidence={"buy": 0.6, "sell": 0.4},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=base_cfg,
    )

    cfg_disabled = deepcopy(base_cfg)
    cfg_disabled["multi_timeframe"] = {
        "research_current_atr_high_vol_multiplier_override": {
            "enabled": False,
            "current_atr_threshold": 763.415054,
            "high_vol_multiplier_override": 1.0,
        }
    }
    action_disabled, meta_disabled = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.6, "sell": 0.4},
        confidence={"buy": 0.6, "sell": 0.4},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=cfg_disabled,
    )

    assert action_base == action_disabled == "LONG"
    assert float(meta_base.get("size") or 0.0) == pytest.approx(
        float(meta_disabled.get("size") or 0.0)
    )
    assert meta_base.get("reasons") == meta_disabled.get("reasons")
    assert meta_base.get("state_out") == meta_disabled.get("state_out")


def test_research_defensive_transition_override_absent_matches_enabled_false() -> None:
    base_cfg = {
        "ev": {"R_default": 1.0},
        "thresholds": {
            "entry_conf_overall": 0.6,
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {"high": {"entry_conf_overall": 0.36, "regime_proba": 0.56}},
            },
        },
        "risk": {"risk_map": [[0.36, 0.01]]},
        "gates": {"cooldown_bars": 0, "hysteresis_steps": 1},
    }
    state = {
        "bars_since_regime_change": 2,
        "current_atr": 4.0,
        "atr_percentiles": {"28": {"p40": 1.0, "p80": 3.0}},
    }

    action_base, meta_base = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=base_cfg,
    )

    cfg_disabled = deepcopy(base_cfg)
    cfg_disabled["multi_timeframe"] = {
        "research_defensive_transition_override": {
            "enabled": False,
            "guard_bars": 5,
            "max_probability_gap": 0.08,
        }
    }
    action_disabled, meta_disabled = decide(
        {"symbol": "tBTCUSD", "timeframe": "1h"},
        probas={"buy": 0.52, "sell": 0.48},
        confidence={"buy": 0.52, "sell": 0.48},
        regime="bull",
        state=state,
        risk_ctx={},
        cfg=cfg_disabled,
    )

    assert action_base == action_disabled == "NONE"
    assert meta_base.get("reasons") == meta_disabled.get("reasons")
    assert meta_base.get("state_out") == meta_disabled.get("state_out")
