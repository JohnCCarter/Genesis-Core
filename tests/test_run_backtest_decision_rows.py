from __future__ import annotations

import json

import scripts.run.run_backtest as run_backtest


def test_decision_row_capture_hook_is_identity_and_records_semantic_row() -> None:
    rows: list[dict] = []

    result = {"action": "LONG", "confidence": {"overall": 0.8}}
    meta = {"decision": {"size": 0.125, "reasons": ["ENTRY_LONG"]}}
    candles = {
        "timestamp": ["2025-01-01T00:00:00Z"],
        "bar_index": 42,
    }

    hook = run_backtest._compose_decision_row_capture_hook(
        symbol="tTESTBTC:TESTUSD",
        timeframe="1h",
        row_sink=rows,
        upstream_hook=None,
    )

    out_result, out_meta = hook(result, meta, candles)

    assert out_result is result
    assert out_meta is meta
    assert len(rows) == 1

    row = rows[0]
    assert row["row_id"] == "tTESTBTC:TESTUSD|1h|42"
    assert row["bar_index"] == 42
    assert row["timestamp"] == "2025-01-01T00:00:00Z"
    assert row["symbol"] == "tTESTBTC:TESTUSD"
    assert row["timeframe"] == "1h"
    assert row["action"] == "LONG"
    assert row["reasons"] == ["ENTRY_LONG"]
    assert row["size"] == 0.125


def test_decision_row_capture_hook_respects_upstream_hook_output() -> None:
    rows: list[dict] = []

    result = {"action": "LONG"}
    meta = {"decision": {"size": 0.3, "reasons": ["ENTRY_LONG"]}}
    candles = {"timestamp": ["2025-01-01T01:00:00Z"], "bar_index": 7}

    def upstream_hook(result_in: dict, meta_in: dict, candles_in: dict):
        result_in["action"] = "NONE"
        meta_in["decision"]["reasons"] = ["UPSTREAM_VETO"]
        return result_in, meta_in

    hook = run_backtest._compose_decision_row_capture_hook(
        symbol="tTESTBTC:TESTUSD",
        timeframe="1h",
        row_sink=rows,
        upstream_hook=upstream_hook,
    )

    out_result, out_meta = hook(result, meta, candles)

    assert out_result["action"] == "NONE"
    assert out_meta["decision"]["reasons"] == ["UPSTREAM_VETO"]
    assert rows[0]["action"] == "NONE"
    assert rows[0]["reasons"] == ["UPSTREAM_VETO"]


def test_write_decision_rows_json_and_ndjson(tmp_path) -> None:
    rows = [
        {
            "row_id": "tTESTBTC:TESTUSD|1h|0",
            "bar_index": 0,
            "timestamp": "2025-01-01T00:00:00Z",
            "symbol": "tTESTBTC:TESTUSD",
            "timeframe": "1h",
            "action": "NONE",
            "reasons": [],
            "size": 0.0,
        }
    ]

    json_path = tmp_path / "rows.json"
    ndjson_path = tmp_path / "rows.ndjson"

    run_backtest._write_decision_rows(json_path, rows, "json")
    run_backtest._write_decision_rows(ndjson_path, rows, "ndjson")

    assert json.loads(json_path.read_text(encoding="utf-8")) == rows

    lines = [line for line in ndjson_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0]) == rows[0]
