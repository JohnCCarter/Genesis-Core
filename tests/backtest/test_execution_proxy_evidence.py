from __future__ import annotations

import json
from pathlib import Path

from scripts.analyze.execution_proxy_evidence import (
    ExecutionProxyEvidenceError,
    main,
    normalize_timestamp,
    run_execution_proxy_evidence,
)


def _trace_row(
    *,
    bar_index: int,
    timestamp: str,
    price: float | None,
    sizing_present: bool,
) -> dict[str, object]:
    return {
        "bar_index": bar_index,
        "timestamp": timestamp,
        "sizing_phase": ({"final_size": 1.0} if sizing_present else None),
        "fib_phase": (
            None
            if price is None
            else {
                "ltf_debug": {
                    "price": price,
                    "atr": 100.0,
                    "tolerance": 125.0,
                }
            }
        ),
    }


def _build_payload() -> dict[str, object]:
    return {
        "name": "baseline_current",
        "trade_signatures": [
            {
                "entry_timestamp": "2024-01-01T00:00:00",
                "exit_timestamp": "2024-01-01T06:00:00",
                "side": "CLOSE_LONG",
                "size": 1.0,
                "pnl": 5.0,
            },
            {
                "entry_timestamp": "2024-01-01T12:00:00",
                "exit_timestamp": "2024-01-01T12:00:00",
                "side": "CLOSE_SHORT",
                "size": 1.0,
                "pnl": -1.0,
            },
        ],
        "trace_rows": [
            _trace_row(
                bar_index=0,
                timestamp="2024-01-01T00:00:00+00:00",
                price=100.0,
                sizing_present=True,
            ),
            _trace_row(
                bar_index=1,
                timestamp="2024-01-01T03:00:00+00:00",
                price=95.0,
                sizing_present=False,
            ),
            _trace_row(
                bar_index=2,
                timestamp="2024-01-01T06:00:00+00:00",
                price=110.0,
                sizing_present=False,
            ),
            _trace_row(
                bar_index=3,
                timestamp="2024-01-01T09:00:00+00:00",
                price=104.0,
                sizing_present=False,
            ),
            _trace_row(
                bar_index=4,
                timestamp="2024-01-01T12:00:00+00:00",
                price=90.0,
                sizing_present=True,
            ),
        ],
    }


def _deep_copy_payload() -> dict[str, object]:
    return json.loads(json.dumps(_build_payload()))


def test_normalize_timestamp_removes_suffix_once() -> None:
    assert normalize_timestamp("2024-01-01T00:00:00+00:00") == "2024-01-01T00:00:00"
    assert normalize_timestamp("2024-01-01T00:00:00") == "2024-01-01T00:00:00"


def test_run_execution_proxy_evidence_outputs_proxy_surfaces() -> None:
    outputs = run_execution_proxy_evidence(_build_payload(), horizons=(1,))

    assert sorted(outputs) == sorted(
        [
            "audit_execution_proxy_determinism.json",
            "execution_proxy_evidence.json",
            "execution_proxy_summary.md",
        ]
    )

    evidence = outputs["execution_proxy_evidence.json"]
    assert evidence["analysis_population"]["join_status"] == "EXACT_ONE_MATCH_PER_TRADE"
    assert evidence["proxy_surface"]["window_semantics"] == "inclusive_entry_exit_bar_index_window"
    assert evidence["proxy_surface"]["full_window_attested_trade_count"] == 2
    assert evidence["proxy_surface"]["sparse_window_trade_count"] == 0

    first_trade = evidence["trade_proxy_metrics"][0]
    assert first_trade["entry_bar_index"] == 0
    assert first_trade["exit_bar_index"] == 2
    assert first_trade["window_row_count"] == 3
    assert first_trade["observed_price_row_count"] == 3
    assert first_trade["entry_proxy_price"] == 100.0
    assert first_trade["exit_proxy_price"] == 110.0
    assert first_trade["proxy_mae_price_delta"] == -5.0
    assert first_trade["proxy_mfe_price_delta"] == 10.0
    assert first_trade["fixed_horizon_deltas"] == [
        {
            "horizon_bars": 1,
            "status": "PASS",
            "target_bar_index": 1,
            "proxy_price_delta": -5.0,
        }
    ]

    second_trade = evidence["trade_proxy_metrics"][1]
    assert second_trade["entry_bar_index"] == 4
    assert second_trade["exit_bar_index"] == 4
    assert second_trade["window_row_count"] == 1
    assert second_trade["observed_price_row_count"] == 1
    assert second_trade["proxy_mae_price_delta"] == 0.0
    assert second_trade["proxy_mfe_price_delta"] == 0.0

    horizon_summary = evidence["fixed_horizon_summaries"]
    assert horizon_summary == [
        {
            "horizon_bars": 1,
            "resolved_trade_count": 1,
            "omitted_trade_count": 1,
            "status": "PASS",
            "mean_proxy_price_delta": -5.0,
            "median_proxy_price_delta": -5.0,
        }
    ]

    audit = outputs["audit_execution_proxy_determinism.json"]
    assert audit["match"] is True
    assert "does not attest realized execution price" in outputs["execution_proxy_summary.md"]


def test_run_execution_proxy_evidence_same_input_is_repeatable() -> None:
    payload = _build_payload()
    run1 = run_execution_proxy_evidence(payload, horizons=(1, 2))
    run2 = run_execution_proxy_evidence(payload, horizons=(1, 2))
    assert run1 == run2


def test_run_execution_proxy_evidence_rejects_duplicate_entry_timestamp() -> None:
    payload = _deep_copy_payload()
    trace_rows = list(payload["trace_rows"])
    trace_rows.append(
        _trace_row(
            bar_index=99,
            timestamp="2024-01-01T12:00:00",
            price=91.0,
            sizing_present=True,
        )
    )
    payload["trace_rows"] = trace_rows

    try:
        run_execution_proxy_evidence(payload, horizons=(1,))
    except ExecutionProxyEvidenceError as exc:
        assert "duplicate normalized baseline trace timestamps" in str(exc)
    else:
        raise AssertionError("expected duplicate entry-timestamp failure")


def test_run_execution_proxy_evidence_rejects_missing_exit_row() -> None:
    payload = _deep_copy_payload()
    payload["trade_signatures"][0]["exit_timestamp"] = "2024-01-02T00:00:00"

    try:
        run_execution_proxy_evidence(payload, horizons=(1,))
    except ExecutionProxyEvidenceError as exc:
        assert "exit row must resolve exactly once" in str(exc)
    else:
        raise AssertionError("expected missing exit-row failure")


def test_run_execution_proxy_evidence_rejects_duplicate_exit_row_resolution() -> None:
    payload = _deep_copy_payload()
    payload["trace_rows"].append(
        _trace_row(
            bar_index=6,
            timestamp="2024-01-01T06:00:00",
            price=111.0,
            sizing_present=False,
        )
    )

    try:
        run_execution_proxy_evidence(payload, horizons=(1,))
    except ExecutionProxyEvidenceError as exc:
        assert "exit row must resolve exactly once" in str(exc)
    else:
        raise AssertionError("expected duplicate exit-row resolution failure")


def test_run_execution_proxy_evidence_rejects_duplicate_bar_index() -> None:
    payload = _deep_copy_payload()
    payload["trace_rows"].append(
        _trace_row(
            bar_index=2,
            timestamp="2024-01-01T15:00:00",
            price=120.0,
            sizing_present=False,
        )
    )

    try:
        run_execution_proxy_evidence(payload, horizons=(1,))
    except ExecutionProxyEvidenceError as exc:
        assert "duplicate trace bar_index detected" in str(exc)
    else:
        raise AssertionError("expected duplicate bar_index failure")


def test_run_execution_proxy_evidence_rejects_gap_inside_inclusive_window() -> None:
    payload = _deep_copy_payload()
    payload["trace_rows"] = [row for row in payload["trace_rows"] if row["bar_index"] != 1]

    try:
        run_execution_proxy_evidence(payload, horizons=(1,))
    except ExecutionProxyEvidenceError as exc:
        assert "missing trace bar_index inside inclusive entry-exit window" in str(exc)
    else:
        raise AssertionError("expected inclusive-window gap failure")


def test_run_execution_proxy_evidence_rejects_missing_entry_proxy_price() -> None:
    payload = _deep_copy_payload()
    payload["trace_rows"][0]["fib_phase"] = None

    try:
        run_execution_proxy_evidence(payload, horizons=(1,))
    except ExecutionProxyEvidenceError as exc:
        assert "joined entry row must expose fib_phase.ltf_debug.price" in str(exc)
    else:
        raise AssertionError("expected missing entry proxy price failure")


def test_run_execution_proxy_evidence_rejects_flat_trade() -> None:
    payload = _deep_copy_payload()
    payload["trade_signatures"][0]["pnl"] = 0.0

    try:
        run_execution_proxy_evidence(payload, horizons=(1,))
    except ExecutionProxyEvidenceError as exc:
        assert "FLAT trades are forbidden" in str(exc)
    else:
        raise AssertionError("expected flat-trade failure")


def test_run_execution_proxy_evidence_sparse_window_omits_exit_proxy_price() -> None:
    payload = _deep_copy_payload()
    payload["trace_rows"][1]["fib_phase"] = None
    payload["trace_rows"][2]["fib_phase"] = None

    outputs = run_execution_proxy_evidence(payload, horizons=(1,))
    evidence = outputs["execution_proxy_evidence.json"]

    assert evidence["proxy_surface"]["full_window_attested_trade_count"] == 1
    assert evidence["proxy_surface"]["sparse_window_trade_count"] == 1

    first_trade = evidence["trade_proxy_metrics"][0]
    assert first_trade["observed_price_row_count"] == 1
    assert first_trade["full_window_price_attested"] is False
    assert first_trade["exit_proxy_price"] is None
    assert first_trade["exact_exit_proxy_price_status"] == "OMITTED_MISSING_PROXY_PRICE"
    assert first_trade["proxy_mae_price_delta"] == 0.0
    assert first_trade["proxy_mfe_price_delta"] == 0.0
    assert first_trade["fixed_horizon_deltas"] == [
        {
            "horizon_bars": 1,
            "status": "OMITTED_MISSING_PROXY_PRICE",
            "target_bar_index": 1,
            "proxy_price_delta": None,
        }
    ]


def test_execution_proxy_evidence_cli_smoke(tmp_path: Path, capsys) -> None:
    baseline_path = tmp_path / "trace_baseline_current.json"
    out_dir = tmp_path / "out"
    baseline_path.write_text(json.dumps(_build_payload()), encoding="utf-8")

    rc = main([str(baseline_path), "--out-dir", str(out_dir), "--horizons", "1", "--json"])
    assert rc == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"
    assert payload["match"] is True
    assert payload["horizons"] == [1]

    expected_files = {
        "execution_proxy_evidence.json",
        "execution_proxy_summary.md",
        "audit_execution_proxy_determinism.json",
    }
    assert expected_files == {path.name for path in out_dir.iterdir()}
