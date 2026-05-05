from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.config.authority import ConfigAuthority
from core.strategy.family_registry import (
    has_ri_signature_markers,
    validate_strategy_family_identity_config,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CARRIER_PATH = (
    REPO_ROOT
    / "tmp"
    / "policy_router_evidence"
    / "legacy"
    / "tBTCUSD_3h_legacy_policy_router_2024_setup_carrier_20260430.json"
)


def _load_carrier_cfg() -> dict[str, Any]:
    payload = json.loads(CARRIER_PATH.read_text(encoding="utf-8"))
    return dict(payload["cfg"])


def test_legacy_policy_router_setup_carrier_validates_as_true_legacy() -> None:
    canonical = ConfigAuthority().validate(_load_carrier_cfg()).model_dump_canonical()

    assert validate_strategy_family_identity_config(canonical) == "legacy"
    assert canonical["strategy_family"] == "legacy"
    assert canonical["multi_timeframe"]["regime_intelligence"]["authority_mode"] == "legacy"
    assert canonical["multi_timeframe"]["research_policy_router"] == {
        "enabled": True,
        "switch_threshold": 2,
        "hysteresis": 1,
        "min_dwell": 3,
        "defensive_size_multiplier": 0.5,
    }
    assert canonical["warmup_bars"] == 120
    assert has_ri_signature_markers(canonical) is False


def test_legacy_policy_router_setup_carrier_absent_variant_stays_legacy() -> None:
    proposal = deepcopy(_load_carrier_cfg())
    proposal["multi_timeframe"].pop("research_policy_router", None)

    canonical = ConfigAuthority().validate(proposal).model_dump_canonical()

    assert validate_strategy_family_identity_config(canonical) == "legacy"
    assert canonical["multi_timeframe"]["regime_intelligence"]["authority_mode"] == "legacy"
    assert "research_policy_router" not in canonical["multi_timeframe"]
    assert has_ri_signature_markers(canonical) is False
