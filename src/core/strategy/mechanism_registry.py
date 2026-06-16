"""Edge-mechanism register (Phase 4, concept lane).

This is a *measurement-honest* container for the causal edge hypotheses the
trading system implicitly bets on. It deliberately does NOT introduce a new
strategy family or any runtime wiring (see CLAUDE.md working-lane model:
"prefer cheaper shapes first: concept lane"; "Do not introduce a new strategy
family merely to give early research a container").

Each mechanism states:
  - the causal claim (why an edge should exist),
  - the surfaces that express it (signal / gates),
  - a falsification condition that, if met, flips its status to REJECTED.

The falsification conditions are deliberately tied to the Phase 1 cost-stress
edge-death thresholds (Sharpe < 1.0, PF < 1.1 at realistic cost) so that the
register stays consistent with how we actually measure edges. Until a mechanism
has direct out-of-sample support it remains UNVERIFIED, which is why the global
EDGE_MAP is UNRESOLVED.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MechanismStatus = Literal["UNVERIFIED", "EXPERIMENTAL", "CANDIDATE", "REJECTED"]

STATUS_UNVERIFIED: MechanismStatus = "UNVERIFIED"
STATUS_EXPERIMENTAL: MechanismStatus = "EXPERIMENTAL"
STATUS_CANDIDATE: MechanismStatus = "CANDIDATE"
STATUS_REJECTED: MechanismStatus = "REJECTED"

MECHANISM_REGISTRY_SOURCE = "mechanism_registry_v1"

# Phase 1 edge-death thresholds (kept in sync with scripts/analyze/cost_stress_sweep.py).
EDGE_DEAD_SHARPE = 1.0
EDGE_DEAD_PF = 1.1


class MechanismRegistryError(ValueError):
    """Raised on invalid mechanism lookups or malformed definitions."""


@dataclass(frozen=True, slots=True)
class EdgeMechanism:
    """A single causal edge hypothesis the system may bet on."""

    mechanism_id: str
    name: str
    causal_claim: str
    signal_surface: str
    gate_surfaces: tuple[str, ...]
    falsification_condition: str
    status: MechanismStatus
    evidence_refs: tuple[str, ...]

    def is_falsified_by(self, *, sharpe: float, profit_factor: float) -> bool:
        """Return True if observed metrics meet this mechanism's death condition.

        Uses the shared Phase 1 edge-death thresholds: an edge is considered
        dead when annualized Sharpe < 1.0 AND profit factor < 1.1 at realistic
        cost. Both must hold so a thin-but-positive edge is not prematurely
        rejected on Sharpe noise alone.
        """
        return sharpe < EDGE_DEAD_SHARPE and profit_factor < EDGE_DEAD_PF


_MECHANISMS: tuple[EdgeMechanism, ...] = (
    EdgeMechanism(
        mechanism_id="ml_confidence_v1",
        name="ML confidence threshold",
        causal_claim=(
            "A gradient-boosted confidence score above a tuned threshold marks "
            "bars whose forward return distribution has positive expectancy."
        ),
        signal_surface="components.ml_confidence (legacy) / thresholds.entry_conf_overall",
        gate_surfaces=("regime_filter", "ev_gate", "cooldown"),
        falsification_condition=(
            "tBTCUSD_1h profit_factor < 1.1 at realistic cost (>=10 bps total), "
            "or no profitable confidence threshold exists with >=30 trades."
        ),
        # Phase 1 sweep: edge only survives at conf>=0.60 (PF=1.24, Sharpe=0.72,
        # 183 trades); unprofitable below. Thin, not yet OOS-validated.
        status=STATUS_UNVERIFIED,
        evidence_refs=(
            "artifacts/diagnostics/cost_stress_sweep_2026-06-16.md",
            "config/strategy/champions/tBTCUSD_1h.json",
        ),
    ),
    EdgeMechanism(
        mechanism_id="regime_intelligence_v1",
        name="Regime-conditioned entry",
        causal_claim=(
            "Conditioning entries on detected market-regime persistence (trend "
            "vs range) raises expectancy by avoiding low-edge regimes."
        ),
        signal_surface="thresholds.signal_adaptation + multi_timeframe.regime_intelligence",
        gate_surfaces=("regime_filter", "htf_gate", "ev_gate"),
        falsification_condition=(
            "tBTCUSD_3h profit_factor < 1.1 at realistic cost, "
            "i.e. edge does not survive slippage >= 40 bps."
        ),
        # Phase 1 sweep: 3h PF=1.585 at low cost but Sharpe<1.0 everywhere and
        # PF collapses to ~1.11 by slip=40bps. Backtest-only support.
        status=STATUS_EXPERIMENTAL,
        evidence_refs=(
            "artifacts/diagnostics/cost_stress_sweep_2026-06-16.md",
            "config/strategy/champions/tBTCUSD_3h.json",
            "src/core/optimizer/robustness.py",
        ),
    ),
)

MECHANISM_REGISTRY: dict[str, EdgeMechanism] = {m.mechanism_id: m for m in _MECHANISMS}


def get_mechanism(mechanism_id: str) -> EdgeMechanism:
    """Return the mechanism with the given id or raise MechanismRegistryError."""
    try:
        return MECHANISM_REGISTRY[mechanism_id]
    except KeyError as e:
        raise MechanismRegistryError(f"unknown_mechanism:{mechanism_id}") from e


def list_mechanisms(status: MechanismStatus | None = None) -> tuple[EdgeMechanism, ...]:
    """Return all mechanisms, optionally filtered by status."""
    if status is None:
        return tuple(MECHANISM_REGISTRY.values())
    return tuple(m for m in MECHANISM_REGISTRY.values() if m.status == status)


def has_verified_edge() -> bool:
    """True only if at least one mechanism has reached CANDIDATE status.

    While this returns False the global EDGE_MAP must remain UNRESOLVED.
    """
    return any(m.status == STATUS_CANDIDATE for m in MECHANISM_REGISTRY.values())


__all__ = [
    "EDGE_DEAD_PF",
    "EDGE_DEAD_SHARPE",
    "MECHANISM_REGISTRY",
    "MECHANISM_REGISTRY_SOURCE",
    "STATUS_CANDIDATE",
    "STATUS_EXPERIMENTAL",
    "STATUS_REJECTED",
    "STATUS_UNVERIFIED",
    "EdgeMechanism",
    "MechanismRegistryError",
    "MechanismStatus",
    "get_mechanism",
    "has_verified_edge",
    "list_mechanisms",
]
