"""
Regression tests for code health fixes (2026-02).

Covers:
1. Direction-aware ML confidence (SHORT uses sell-side, not buy-side)
2. Proba 0.0 key-presence (0.0 is valid, must not fall through to legacy key)
3. Config mutation isolation (engine.run must not mutate caller's dict)
4. HTFGate empty-list semantics ([] blocks all regimes)
5. Component naming contract (all names are snake_case)
"""

import re

import pytest

# ---------------------------------------------------------------------------
# 1. Direction-aware ML confidence
# ---------------------------------------------------------------------------


class TestDirectionAwareMLConfidence:
    """Ensure ComponentContextBuilder + MLConfidenceComponent respect action direction."""

    def test_short_action_uses_sell_confidence(self):
        """SHORT action should map sell-side confidence, not buy-side."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        result = {
            "action": "SHORT",
            "probas": {"buy": 0.20, "sell": 0.80},
            "confidence": {"buy": 0.25, "sell": 0.85},
        }
        ctx = ComponentContextBuilder.build(result, meta={})

        assert ctx["ml_confidence_for_action"] == 0.85, "SHORT should use sell-side confidence"
        # backward-compat key should still be LONG side
        assert ctx["ml_confidence"] == 0.25

    def test_long_action_uses_buy_confidence(self):
        """LONG action should map buy-side confidence."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        result = {
            "action": "LONG",
            "probas": {"buy": 0.70, "sell": 0.30},
            "confidence": {"buy": 0.75, "sell": 0.35},
        }
        ctx = ComponentContextBuilder.build(result, meta={})

        assert ctx["ml_confidence_for_action"] == 0.75
        assert ctx["ml_confidence"] == 0.75

    def test_ml_component_prefers_direction_aware_key(self):
        """MLConfidenceComponent should use ml_confidence_for_action over ml_confidence."""
        from core.strategy.components.ml_confidence import MLConfidenceComponent

        component = MLConfidenceComponent(threshold=0.5)

        # Direction-aware key says 0.8 (above threshold), legacy key says 0.3 (below)
        context = {"ml_confidence_for_action": 0.8, "ml_confidence": 0.3}
        decision = component.evaluate(context)

        assert (
            decision.allowed is True
        ), "Component should use ml_confidence_for_action (0.8), not ml_confidence (0.3)"
        assert decision.confidence == 0.8

    def test_ml_component_falls_back_to_legacy_key(self):
        """Without direction-aware key, component should fall back to ml_confidence."""
        from core.strategy.components.ml_confidence import MLConfidenceComponent

        component = MLConfidenceComponent(threshold=0.5)

        context = {"ml_confidence": 0.7}
        decision = component.evaluate(context)

        assert decision.allowed is True
        assert decision.confidence == 0.7


# ---------------------------------------------------------------------------
# 2. Proba 0.0 key-presence (truthiness bug)
# ---------------------------------------------------------------------------


class TestProbaZeroPresence:
    """Verify that a probability of 0.0 is not treated as 'missing'."""

    def test_buy_zero_does_not_fall_through_to_long(self):
        """buy=0.0 is valid; must not fall through to legacy long key."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        result = {
            # sell>0 ensures proba keys are emitted; the test then validates that
            # buy=0.0 is preserved (and does not fall through to long=0.6).
            "probas": {"buy": 0.0, "long": 0.6, "sell": 0.8},
        }
        ctx = ComponentContextBuilder.build(result, meta={})

        assert "ml_proba_long" in ctx
        assert "ml_proba_short" in ctx
        assert ctx["ml_proba_long"] == 0.0, "buy=0.0 must NOT fall through to long=0.6"
        assert ctx["ml_proba_short"] == 0.8

    def test_sell_zero_does_not_fall_through_to_short(self):
        """sell=0.0 is valid; must not fall through to legacy short key."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        result = {
            # buy>0 ensures proba keys are emitted; the test then validates that
            # sell=0.0 is preserved (and does not fall through to short=0.7).
            "probas": {"buy": 0.4, "sell": 0.0, "short": 0.7},
        }
        ctx = ComponentContextBuilder.build(result, meta={})

        assert "ml_proba_long" in ctx
        assert "ml_proba_short" in ctx
        assert ctx["ml_proba_long"] == 0.4
        assert ctx["ml_proba_short"] == 0.0, "sell=0.0 must NOT fall through to short=0.7"

    def test_both_zero_probas_yields_no_proba_keys(self):
        """When both probas are exactly 0.0, no proba keys should be set (guard clause)."""
        from core.strategy.components.context_builder import ComponentContextBuilder

        result = {"probas": {"buy": 0.0, "sell": 0.0}}
        ctx = ComponentContextBuilder.build(result, meta={})

        # The builder skips setting keys when both are 0 (guard: p_long > 0 or p_short > 0)
        assert "ml_proba_long" not in ctx
        assert "ml_proba_short" not in ctx


# ---------------------------------------------------------------------------
# 3. Config mutation isolation
# ---------------------------------------------------------------------------


class TestConfigMutationIsolation:
    """BacktestEngine.run() must not leak internal state back to caller's config dict."""

    def test_configs_dict_unchanged_after_run(self):
        """Caller's configs dict should be identical before and after engine.run()."""
        import copy

        from core.backtest.engine import BacktestEngine

        original_configs = {
            "cfg": {
                "thresholds": {"entry_conf_overall": 0.30},
            },
            "meta": {"skip_champion_merge": True},
        }

        # Deep-freeze a snapshot of the original for comparison
        snapshot = copy.deepcopy(original_configs)

        engine = BacktestEngine(
            symbol="tTESTBTC:TESTUSD",
            timeframe="1h",
            initial_capital=10_000,
        )

        # Engine.run() will inject _global_index, meta keys, etc.
        # We don't need it to succeed — just not crash and not mutate.
        try:
            engine.run(configs=original_configs)
        except Exception:
            pass  # data loading may fail in test env — that's fine

        assert original_configs == snapshot, (
            "engine.run() must not mutate the caller's configs dict. "
            f"Diff keys: {set(original_configs) ^ set(snapshot)}"
        )


# ---------------------------------------------------------------------------
# 4. HTFGate empty-list semantics
# ---------------------------------------------------------------------------


class TestHTFGateEmptyList:
    """[] for required_regimes should block ALL, None should use defaults."""

    def test_empty_list_blocks_all_regimes(self):
        """An explicit empty list means 'no regime is acceptable'."""
        from core.strategy.components.htf_gate import HTFGateComponent

        gate = HTFGateComponent(required_regimes=[])

        for regime in ["trending", "bull", "bear", "ranging", "unknown"]:
            decision = gate.evaluate({"htf_regime": regime})
            assert decision.allowed is False, f"Empty required_regimes should block '{regime}'"

    def test_none_uses_defaults(self):
        """None (omitted) should default to ['trending', 'bull']."""
        from core.strategy.components.htf_gate import HTFGateComponent

        gate = HTFGateComponent(required_regimes=None)

        assert gate.evaluate({"htf_regime": "trending"}).allowed is True
        assert gate.evaluate({"htf_regime": "bull"}).allowed is True
        assert gate.evaluate({"htf_regime": "bear"}).allowed is False


# ---------------------------------------------------------------------------
# 5. Component naming contract
# ---------------------------------------------------------------------------


class TestComponentNamingContract:
    """All built-in component names must be snake_case."""

    SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")

    @pytest.mark.parametrize(
        "component_cls,kwargs",
        [
            ("MLConfidenceComponent", {}),
            ("EVGateComponent", {}),
            ("RegimeFilterComponent", {"allowed_regimes": ["trending"]}),
            ("HTFGateComponent", {}),
            (
                "CooldownComponent",
                {"config": {"min_bars_between_trades": 5}},
            ),
        ],
    )
    def test_default_name_is_snake_case(self, component_cls, kwargs):
        """Default component name must match ^[a-z][a-z0-9_]*$."""
        import importlib

        # Dynamic import to cover all components
        module_map = {
            "MLConfidenceComponent": "core.strategy.components.ml_confidence",
            "EVGateComponent": "core.strategy.components.ev_gate",
            "RegimeFilterComponent": "core.strategy.components.regime_filter",
            "HTFGateComponent": "core.strategy.components.htf_gate",
            "CooldownComponent": "core.strategy.components.cooldown",
        }
        mod = importlib.import_module(module_map[component_cls])
        cls = getattr(mod, component_cls)
        instance = cls(**kwargs)

        name = instance.name()
        assert self.SNAKE_CASE_RE.match(
            name
        ), f"{component_cls}.name() returned '{name}' — expected snake_case"
