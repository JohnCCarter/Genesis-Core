"""
Unit tests for composable strategy POC - base classes and composition logic.
"""

import pytest

from core.strategy.components import ComponentResult, StrategyComponent
from core.strategy.components.strategy import ComposableStrategy, StrategyDecision


class DummyPassComponent(StrategyComponent):
    """Test component that always passes."""

    def name(self) -> str:
        return "dummy_pass"

    def evaluate(self, context: dict) -> ComponentResult:
        return ComponentResult(allowed=True, confidence=0.8, metadata={"test": "pass"})


class DummyVetoComponent(StrategyComponent):
    """Test component that always vetoes."""

    def name(self) -> str:
        return "dummy_veto"

    def evaluate(self, context: dict) -> ComponentResult:
        return ComponentResult(
            allowed=False, confidence=0.2, reason="TEST_VETO", metadata={"test": "veto"}
        )


class DummyLowConfidenceComponent(StrategyComponent):
    """Test component that passes but with low confidence."""

    def name(self) -> str:
        return "dummy_low_conf"

    def evaluate(self, context: dict) -> ComponentResult:
        return ComponentResult(allowed=True, confidence=0.3, metadata={"test": "low"})


def test_component_result_validates_confidence():
    """ComponentResult should validate confidence is in 0-1 range."""
    with pytest.raises(ValueError, match="Confidence must be 0-1"):
        ComponentResult(allowed=True, confidence=1.5)

    with pytest.raises(ValueError, match="Confidence must be 0-1"):
        ComponentResult(allowed=True, confidence=-0.1)

    result = ComponentResult(allowed=True, confidence=0.5)
    assert result.confidence == 0.5


def test_component_result_is_immutable():
    """ComponentResult should be frozen (immutable)."""
    result = ComponentResult(allowed=True, confidence=0.5)
    with pytest.raises(AttributeError):
        result.allowed = False


def test_composable_strategy_requires_components():
    """ComposableStrategy should require at least one component."""
    with pytest.raises(ValueError, match="At least one component required"):
        ComposableStrategy([])


def test_composable_strategy_all_pass():
    """When all components pass, decision should be allowed with min confidence."""
    strategy = ComposableStrategy([DummyPassComponent(), DummyLowConfidenceComponent()])

    decision = strategy.evaluate({})

    assert decision.allowed is True
    assert decision.confidence == 0.3
    assert decision.veto_component is None
    assert decision.veto_reason is None
    assert len(decision.component_results) == 2


def test_composable_strategy_veto_blocks():
    """When any component vetoes, decision should be blocked."""
    strategy = ComposableStrategy(
        [DummyPassComponent(), DummyVetoComponent(), DummyLowConfidenceComponent()]
    )

    decision = strategy.evaluate({})

    assert decision.allowed is False
    assert decision.veto_component == "dummy_veto"
    assert decision.veto_reason == "TEST_VETO"
    assert len(decision.component_results) == 2


def test_composable_strategy_veto_stops_evaluation():
    """Veto should stop further component evaluation."""
    strategy = ComposableStrategy([DummyVetoComponent(), DummyPassComponent()])

    decision = strategy.evaluate({})

    assert len(decision.component_results) == 1
    assert "dummy_veto" in decision.component_results
    assert "dummy_pass" not in decision.component_results


def test_composable_strategy_min_confidence():
    """Confidence should be minimum across all evaluated components."""
    comp1 = DummyPassComponent()
    comp2 = DummyLowConfidenceComponent()

    strategy = ComposableStrategy([comp1, comp2])
    decision = strategy.evaluate({})

    assert decision.confidence == 0.3


def test_strategy_decision_structure():
    """StrategyDecision should have expected structure."""
    decision = StrategyDecision(
        allowed=True,
        confidence=0.8,
        veto_component=None,
        veto_reason=None,
        component_results={},
    )

    assert decision.allowed is True
    assert decision.confidence == 0.8
    assert decision.veto_component is None
    assert decision.veto_reason is None
    assert decision.component_results == {}
