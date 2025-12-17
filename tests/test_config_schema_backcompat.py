from __future__ import annotations

from core.config.authority import ConfigAuthority


def test_validate_accepts_scalar_regime_proba_in_signal_adaptation_zones() -> None:
    """Back-compat: older Optuna configs used scalar regime_proba inside signal_adaptation zones."""

    proposal = {
        "thresholds": {
            "entry_conf_overall": 0.3,
            "regime_proba": {"balanced": 0.5},
            "signal_adaptation": {
                "atr_period": 28,
                "zones": {
                    "low": {"entry_conf_overall": 0.25, "regime_proba": 0.36, "pct": None},
                    "mid": {"entry_conf_overall": 0.32, "regime_proba": 0.44, "pct": None},
                    "high": {"entry_conf_overall": 0.38, "regime_proba": 0.56, "pct": None},
                },
            },
        }
    }

    cfg = ConfigAuthority().validate(proposal)
    zones = (cfg.thresholds.signal_adaptation or {}).zones  # type: ignore[union-attr]
    assert zones["low"].regime_proba == 0.36
    assert zones["mid"].regime_proba == 0.44
    assert zones["high"].regime_proba == 0.56


def test_validate_accepts_scalar_top_level_regime_proba() -> None:
    proposal = {
        "thresholds": {
            "entry_conf_overall": 0.3,
            "regime_proba": 0.5,
        }
    }

    cfg = ConfigAuthority().validate(proposal)
    assert cfg.thresholds.regime_proba == 0.5
