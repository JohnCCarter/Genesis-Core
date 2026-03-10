from __future__ import annotations

from copy import deepcopy

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
