from __future__ import annotations

import pytest

from core.strategy.mechanism_registry import (
    EDGE_DEAD_PF,
    EDGE_DEAD_SHARPE,
    MECHANISM_REGISTRY,
    STATUS_CANDIDATE,
    STATUS_EXPERIMENTAL,
    STATUS_UNVERIFIED,
    EdgeMechanism,
    MechanismRegistryError,
    get_mechanism,
    has_verified_edge,
    list_mechanisms,
)


def test_registry_is_non_empty_and_keyed_by_id() -> None:
    assert MECHANISM_REGISTRY
    for mech_id, mech in MECHANISM_REGISTRY.items():
        assert mech_id == mech.mechanism_id


def test_known_mechanisms_present() -> None:
    assert "ml_confidence_v1" in MECHANISM_REGISTRY
    assert "regime_intelligence_v1" in MECHANISM_REGISTRY


def test_get_mechanism_returns_definition() -> None:
    mech = get_mechanism("ml_confidence_v1")
    assert isinstance(mech, EdgeMechanism)
    assert mech.causal_claim
    assert mech.falsification_condition
    assert mech.evidence_refs


def test_get_unknown_mechanism_raises() -> None:
    with pytest.raises(MechanismRegistryError):
        get_mechanism("does_not_exist")


def test_list_mechanisms_filters_by_status() -> None:
    unverified = list_mechanisms(STATUS_UNVERIFIED)
    assert all(m.status == STATUS_UNVERIFIED for m in unverified)
    experimental = list_mechanisms(STATUS_EXPERIMENTAL)
    assert all(m.status == STATUS_EXPERIMENTAL for m in experimental)


def test_no_verified_edge_keeps_edge_map_unresolved() -> None:
    # Until any mechanism reaches CANDIDATE the global edge claim must be False.
    assert has_verified_edge() is False
    assert not list_mechanisms(STATUS_CANDIDATE)


def test_falsification_uses_phase1_thresholds() -> None:
    mech = get_mechanism("regime_intelligence_v1")
    # Dead: both below thresholds.
    assert mech.is_falsified_by(sharpe=0.2, profit_factor=1.05) is True
    # Alive: PF above death threshold (thin but positive).
    assert mech.is_falsified_by(sharpe=0.2, profit_factor=1.5) is False
    # Alive: Sharpe above threshold.
    assert mech.is_falsified_by(sharpe=1.2, profit_factor=1.05) is False


def test_thresholds_match_cost_sweep_constants() -> None:
    assert EDGE_DEAD_SHARPE == 1.0
    assert EDGE_DEAD_PF == 1.1


def test_every_mechanism_has_falsification_and_evidence() -> None:
    for mech in MECHANISM_REGISTRY.values():
        assert mech.falsification_condition.strip()
        assert mech.evidence_refs, f"{mech.mechanism_id} lacks evidence refs"
        assert mech.signal_surface.strip()
