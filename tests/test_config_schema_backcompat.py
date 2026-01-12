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


def test_fib_entry_missing_policy_defaults_to_pass_for_backcompat() -> None:
    """Back-compat: older champions/configs omitted fib.entry.missing_policy.

    If missing_policy is absent (or null), we must not silently treat it as a hard block,
    otherwise previously valid champions can degenerate into 0-trade configs after schema
    validation/model_dump.
    """

    proposal = {
        "htf_fib": {"entry": {"enabled": True, "tolerance_atr": 1.0}},
        "ltf_fib": {"entry": {"enabled": True, "tolerance_atr": 1.0, "missing_policy": None}},
    }

    cfg = ConfigAuthority().validate(proposal)

    assert cfg.htf_fib is not None
    assert cfg.htf_fib.entry is not None
    assert cfg.htf_fib.entry.missing_policy == "pass"

    assert cfg.ltf_fib is not None
    assert cfg.ltf_fib.entry is not None
    assert cfg.ltf_fib.entry.missing_policy == "pass"
