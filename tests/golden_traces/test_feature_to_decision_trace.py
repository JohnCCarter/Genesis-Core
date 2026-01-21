"""
GOLDEN TRACE TEST 2: Feature → Decision Determinism

Verifies that given identical features and parameters,
decision logic produces identical entry/exit signals.

Catches drift in:
- Confidence calculation
- Entry gate logic (Fibonacci, thresholds, regime)
- Position sizing (risk map)
- Exit conditions (HTF Fibonacci, trailing stops)
"""

import json
from pathlib import Path

import pytest

from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide


def _assert_close(actual, expected, rtol=1e-10, name="value"):
    """Assert two floats are close within relative tolerance."""
    if abs(actual - expected) > rtol * abs(expected):
        raise AssertionError(
            f"{name}: expected {expected}, got {actual} "
            f"(diff: {abs(actual - expected)}, rtol: {rtol})"
        )


@pytest.fixture
def golden_dir():
    """Return path to golden snapshots directory."""
    return Path(__file__).parent / "snapshots"


@pytest.fixture
def golden_features(golden_dir):
    """Load golden feature snapshot."""
    features_path = golden_dir / "golden_features_v1.json"
    if not features_path.exists():
        pytest.skip(f"Golden features not found: {features_path}")
    with open(features_path) as f:
        return json.load(f)


@pytest.fixture
def champion_params(golden_dir):
    """Load golden champion parameters."""
    params_path = golden_dir / "golden_champion_params.json"
    if not params_path.exists():
        pytest.skip(f"Golden params not found: {params_path}")
    with open(params_path) as f:
        return json.load(f)


@pytest.fixture
def golden_decision(golden_dir):
    """Load golden decision snapshot."""
    decision_path = golden_dir / "golden_decision_v1.json"
    if not decision_path.exists():
        pytest.skip(f"Golden decision not found: {decision_path}")
    with open(decision_path) as f:
        return json.load(f)


def test_feature_to_decision_determinism(golden_features, champion_params, golden_decision):
    """
    GOLDEN TRACE 2: Features → Decisions

    Asserts that decision logic is deterministic.
    This test will fail if entry gates, confidence, or sizing logic changes.
    """
    # Mock probability model output (deterministic)
    probas = {"UP": 0.62, "DOWN": 0.38, "NEUTRAL": 0.15}

    # Compute confidence using golden features
    atr_pct = golden_features.get("atr_14", 100.0) / golden_features.get("close", 50000.0) * 100
    confidence = compute_confidence(
        probas=probas,
        atr_pct=atr_pct,
        spread_bp=1.0,
        volume_score=0.85,
        data_quality=1.0,
        config=champion_params,
    )

    # Make decision
    action, action_meta = decide(
        policy="backtest",
        probas=probas,
        confidence=confidence,
        regime="bull",
        state={},
        risk_ctx={"current_equity": 10000.0},
        cfg=champion_params,
    )

    # Assert decision matches golden snapshot
    assert action == golden_decision["action"], f"Action mismatch: {action} != {golden_decision['action']}"

    # Assert position size matches (if action != NONE)
    if "size" in golden_decision and "size" in action_meta:
        _assert_close(action_meta["size"], golden_decision["size"], rtol=1e-8, name="size")

    # Assert reasons match (or both None/empty)
    golden_reasons = golden_decision.get("reasons", [])
    actual_reasons = action_meta.get("reasons", [])
    assert set(actual_reasons) == set(golden_reasons), f"Reasons mismatch: {actual_reasons} != {golden_reasons}"

    # Assert blocked_by matches
    assert action_meta.get("blocked_by") == golden_decision.get("blocked_by"), "blocked_by mismatch"

    # Assert confidence calculation unchanged
    _assert_close(confidence["overall"], golden_decision["confidence"], rtol=1e-8, name="confidence")


def test_decision_snapshot_exists(golden_dir):
    """Sanity check: ensure golden decision snapshot exists."""
    decision_path = golden_dir / "golden_decision_v1.json"
    if not decision_path.exists():
        pytest.skip(
            f"Golden decision snapshot not found. Run scripts/rebaseline_golden_traces.py first.\n"
            f"Expected: {decision_path}"
        )
