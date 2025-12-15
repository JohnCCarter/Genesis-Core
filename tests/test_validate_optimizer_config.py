from __future__ import annotations

from scripts.validate_optimizer_config import normalize_champion_payload


def test_normalize_champion_payload_prefers_cfg() -> None:
    payload = {
        "cfg": {"risk": {"risk_map": [[0.48, 0.01]]}, "thresholds": {"entry_conf_overall": 0.3}},
        "parameters": {"risk": {"risk_map": [[0.48, 0.99]]}},
        "merged_config": {"risk": {"risk_map": [[0.48, 0.88]]}},
    }
    cfg = normalize_champion_payload(payload)
    assert cfg["risk"]["risk_map"] == [[0.48, 0.01]]


def test_normalize_champion_payload_uses_parameters_when_present() -> None:
    payload = {"parameters": {"risk": {"risk_map": [[0.48, 0.02]]}}}
    cfg = normalize_champion_payload(payload)
    assert cfg["risk"]["risk_map"] == [[0.48, 0.02]]


def test_normalize_champion_payload_uses_merged_config_when_present() -> None:
    payload = {"merged_config": {"risk": {"risk_map": [[0.48, 0.03]]}}}
    cfg = normalize_champion_payload(payload)
    assert cfg["risk"]["risk_map"] == [[0.48, 0.03]]


def test_normalize_champion_payload_falls_back_to_payload() -> None:
    payload = {"risk": {"risk_map": [[0.48, 0.04]]}}
    cfg = normalize_champion_payload(payload)
    assert cfg["risk"]["risk_map"] == [[0.48, 0.04]]
