from __future__ import annotations

from core.agent.agent_runtime import _coerce_params, _evaluate_risk, evaluate_and_record
from core.agent.fib_strategy import FibStrategyParams


def test_coerce_params_from_dict_handles_tuples() -> None:
    p = _coerce_params({"extension_levels": [1.5, 2.0], "atr_depth": 4.0})
    assert isinstance(p, FibStrategyParams)
    assert p.extension_levels == (1.5, 2.0)
    assert p.atr_depth == 4.0


def test_coerce_params_filters_unknown_keys() -> None:
    p = _coerce_params({"entry_zone_low": 0.4, "ignored_key": 999})
    assert p.entry_zone_low == 0.4


def test_coerce_params_allows_nested_strategy_knobs() -> None:
    p = _coerce_params(
        {
            "mega_atr_depth": 7.0,
            "major_atr_depth": 4.5,
            "minor_atr_depth": 3.5,
            "mega_zone_touch_required": False,
        }
    )
    assert p.mega_atr_depth == 7.0
    assert p.major_atr_depth == 4.5
    assert p.minor_atr_depth == 3.5
    assert p.mega_zone_touch_required is False


def test_evaluate_risk_default_passes() -> None:
    out = _evaluate_risk(None)
    assert out["passed"] is True
    assert out["reasons"] == []


def test_evaluate_risk_blocks_on_daily_loss() -> None:
    out = _evaluate_risk(
        {
            "baseline_equity_usd": 1000.0,
            "current_equity_usd": 700.0,
            "max_daily_loss_usd": 200.0,
        }
    )
    assert out["passed"] is False
    assert "daily_loss_breached" in out["reasons"]


def test_evaluate_risk_blocks_on_drawdown() -> None:
    out = _evaluate_risk(
        {
            "equity_peak_usd": 1000.0,
            "current_equity_usd": 850.0,
            "max_dd_pct": 10.0,
        }
    )
    assert out["passed"] is False
    assert "max_drawdown_breached" in out["reasons"]


def test_evaluate_and_record_persists_when_persist_true(
    htf_uptrend_pullback, ltf_uptrend_pullback, tmp_log_path
) -> None:
    record = evaluate_and_record(
        htf_candles=htf_uptrend_pullback,
        ltf_candles=ltf_uptrend_pullback,
        symbol="tBTCUSD",
        trend_tf="6h",
        entry_tf="1h",
        risk_state={"current_equity_usd": 1000.0},
        persist=True,
    )
    assert record.symbol == "tBTCUSD"
    assert record.fib_signal["action"] in {"LONG", "SHORT", "NONE"}
    assert tmp_log_path.exists()
    assert tmp_log_path.read_text(encoding="utf-8").strip() != ""


def test_evaluate_and_record_skip_persist(
    htf_uptrend_pullback, ltf_uptrend_pullback, tmp_log_path
) -> None:
    evaluate_and_record(
        htf_candles=htf_uptrend_pullback,
        ltf_candles=ltf_uptrend_pullback,
        symbol="tBTCUSD",
        trend_tf="6h",
        entry_tf="1h",
        persist=False,
    )
    assert not tmp_log_path.exists()


def test_evaluate_and_record_blocked_record_still_returned(
    htf_uptrend_pullback, ltf_uptrend_pullback
) -> None:
    record = evaluate_and_record(
        htf_candles=htf_uptrend_pullback,
        ltf_candles=ltf_uptrend_pullback,
        symbol="tBTCUSD",
        trend_tf="6h",
        entry_tf="1h",
        risk_state={
            "baseline_equity_usd": 1000.0,
            "current_equity_usd": 700.0,
            "max_daily_loss_usd": 200.0,
        },
        persist=False,
    )
    assert record.risk_check["passed"] is False
    assert "daily_loss_breached" in record.risk_check["reasons"]


def test_evaluate_and_record_persists_mid_tf_when_nested(
    htf_uptrend_pullback, ltf_uptrend_pullback
) -> None:
    record = evaluate_and_record(
        htf_candles=htf_uptrend_pullback,
        mid_candles=htf_uptrend_pullback,
        ltf_candles=ltf_uptrend_pullback,
        symbol="tBTCUSD",
        trend_tf="1D",
        mid_tf="6h",
        entry_tf="1h",
        persist=False,
    )
    assert record.mid_tf == "6h"
