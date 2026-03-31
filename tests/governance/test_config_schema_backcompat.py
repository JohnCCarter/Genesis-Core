from __future__ import annotations

import json
from pathlib import Path

import pytest

import core.config.authority as authority_module
from core.config.authority import ConfigAuthority


def test_validate_accepts_scalar_regime_proba_in_signal_adaptation_zones() -> None:
    """Back-compat: older Optuna configs used scalar regime_proba inside signal_adaptation zones."""

    proposal = {
        "strategy_family": "legacy",
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
        },
    }

    cfg = ConfigAuthority().validate(proposal)
    zones = (cfg.thresholds.signal_adaptation or {}).zones  # type: ignore[union-attr]
    assert zones["low"].regime_proba == 0.36
    assert zones["mid"].regime_proba == 0.44
    assert zones["high"].regime_proba == 0.56


def test_validate_preserves_signal_adaptation_enabled_flag_in_canonical_dump() -> None:
    proposal = {
        "strategy_family": "legacy",
        "thresholds": {
            "entry_conf_overall": 0.3,
            "regime_proba": {"balanced": 0.5},
            "signal_adaptation": {
                "enabled": False,
                "atr_period": 28,
                "zones": {
                    "low": {"entry_conf_overall": 0.25, "regime_proba": 0.36, "pct": None},
                    "mid": {"entry_conf_overall": 0.32, "regime_proba": 0.44, "pct": None},
                    "high": {"entry_conf_overall": 0.38, "regime_proba": 0.56, "pct": None},
                },
            },
        },
    }

    cfg = ConfigAuthority().validate(proposal)
    dumped = cfg.model_dump_canonical()

    assert dumped["thresholds"]["signal_adaptation"]["enabled"] is False


def test_validate_accepts_scalar_top_level_regime_proba() -> None:
    proposal = {
        "strategy_family": "legacy",
        "thresholds": {
            "entry_conf_overall": 0.3,
            "regime_proba": 0.5,
        },
    }

    cfg = ConfigAuthority().validate(proposal)
    assert cfg.thresholds.regime_proba == 0.5


def test_validate_top_level_regime_proba_none_uses_balanced_default() -> None:
    proposal = {
        "strategy_family": "legacy",
        "thresholds": {
            "entry_conf_overall": 0.3,
            "regime_proba": None,
        },
    }

    cfg = ConfigAuthority().validate(proposal)
    assert cfg.thresholds.regime_proba == {"balanced": 0.58}


def test_fib_entry_missing_policy_defaults_to_pass_for_backcompat() -> None:
    """Back-compat: older champions/configs omitted fib.entry.missing_policy.

    If missing_policy is absent (or null), we must not silently treat it as a hard block,
    otherwise previously valid champions can degenerate into 0-trade configs after schema
    validation/model_dump.
    """

    proposal = {
        "strategy_family": "legacy",
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


def test_load_injects_legacy_strategy_family_for_persisted_snapshot_backcompat(
    tmp_path: Path,
) -> None:
    runtime_path = tmp_path / "runtime.json"
    runtime_path.write_text(
        json.dumps(
            {
                "version": 7,
                "cfg": {
                    "thresholds": {
                        "entry_conf_overall": 0.26,
                        "regime_proba": {"balanced": 0.5},
                        "signal_adaptation": {
                            "atr_period": 28,
                            "zones": {
                                "low": {"entry_conf_overall": 0.24, "regime_proba": 0.36},
                                "mid": {"entry_conf_overall": 0.30, "regime_proba": 0.44},
                                "high": {"entry_conf_overall": 0.36, "regime_proba": 0.56},
                            },
                        },
                    },
                    "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
                    "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
                },
            }
        ),
        encoding="utf-8",
    )

    snapshot = ConfigAuthority(path=runtime_path).load()

    assert snapshot.version == 7
    assert snapshot.cfg.strategy_family == "legacy"


def test_load_rejects_missing_strategy_family_for_non_legacy_snapshot_backcompat(
    tmp_path: Path,
) -> None:
    runtime_path = tmp_path / "runtime.json"
    runtime_path.write_text(
        json.dumps(
            {
                "version": 9,
                "cfg": {
                    "thresholds": {
                        "entry_conf_overall": 0.25,
                        "regime_proba": {"balanced": 0.36},
                        "signal_adaptation": {
                            "atr_period": 14,
                            "zones": {
                                "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                                "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                                "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                            },
                        },
                    },
                    "gates": {"hysteresis_steps": 3, "cooldown_bars": 2},
                    "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}},
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError, match="missing_strategy_family_backcompat_requires_legacy_signature"
    ):
        ConfigAuthority(path=runtime_path).load()


def test_load_uses_seed_backcompat_for_missing_legacy_strategy_family(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_path = tmp_path / "runtime.json"
    seed_path = tmp_path / "runtime.seed.json"
    seed_path.write_text(
        json.dumps(
            {
                "version": 3,
                "cfg": {
                    "thresholds": {
                        "entry_conf_overall": 0.26,
                        "regime_proba": {"balanced": 0.5},
                        "signal_adaptation": {
                            "atr_period": 28,
                            "zones": {
                                "low": {"entry_conf_overall": 0.24, "regime_proba": 0.36},
                                "mid": {"entry_conf_overall": 0.30, "regime_proba": 0.44},
                                "high": {"entry_conf_overall": 0.36, "regime_proba": 0.56},
                            },
                        },
                    },
                    "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
                    "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(authority_module, "SEED_PATH", seed_path)

    snapshot = ConfigAuthority(path=runtime_path).load()

    assert snapshot.version == 3
    assert snapshot.cfg.strategy_family == "legacy"


def test_load_rejects_seed_backcompat_for_non_legacy_missing_strategy_family(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_path = tmp_path / "runtime.json"
    seed_path = tmp_path / "runtime.seed.json"
    seed_path.write_text(
        json.dumps(
            {
                "version": 4,
                "cfg": {
                    "thresholds": {
                        "entry_conf_overall": 0.25,
                        "regime_proba": {"balanced": 0.36},
                        "signal_adaptation": {
                            "atr_period": 14,
                            "zones": {
                                "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                                "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                                "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                            },
                        },
                    },
                    "gates": {"hysteresis_steps": 3, "cooldown_bars": 2},
                    "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}},
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(authority_module, "SEED_PATH", seed_path)

    with pytest.raises(
        ValueError, match="missing_strategy_family_backcompat_requires_legacy_signature"
    ):
        ConfigAuthority(path=runtime_path).load()
