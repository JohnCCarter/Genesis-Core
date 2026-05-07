from __future__ import annotations

import json

from core.agent.decision_record import (
    DecisionRecord,
    append_decision,
    append_followup,
    candles_hash,
    canonical_hash,
    find_decision,
    read_decisions,
)


def _make_record(symbol: str = "tBTCUSD", action: str = "LONG") -> DecisionRecord:
    return DecisionRecord(
        ts_utc="2026-05-07T00:00:00+00:00",
        symbol=symbol,
        trend_tf="6h",
        entry_tf="1h",
        candles_hash={"htf": "h1", "ltf": "l1"},
        params_hash="p1",
        fib_signal={"action": action, "reason": "ltf_confirmation"},
        risk_check={"passed": True, "reasons": []},
    )


def test_canonical_hash_is_key_order_invariant() -> None:
    a = canonical_hash({"a": 1, "b": [2, 3], "c": {"x": "y"}})
    b = canonical_hash({"c": {"x": "y"}, "b": [2, 3], "a": 1})
    assert a == b


def test_candles_hash_changes_when_last_close_differs() -> None:
    base = {"close": [1.0, 2.0, 3.0, 4.0, 5.0]}
    other = {"close": [1.0, 2.0, 3.0, 4.0, 5.5]}
    assert candles_hash(base) != candles_hash(other)


def test_candles_hash_same_for_identical_tail() -> None:
    a = {"close": [1.0, 2.0, 3.0, 4.0, 5.0]}
    b = {"close": [1.0, 2.0, 3.0, 4.0, 5.0]}
    assert candles_hash(a) == candles_hash(b)


def test_append_then_read_roundtrip(tmp_path) -> None:
    log = tmp_path / "decisions.jsonl"
    rec1 = _make_record(symbol="tBTCUSD")
    rec2 = _make_record(symbol="tETHUSD")
    rec3 = _make_record(symbol="tBTCUSD", action="SHORT")
    append_decision(rec1, path=log)
    append_decision(rec2, path=log)
    append_decision(rec3, path=log)

    all_recs = read_decisions(path=log, limit=10)
    assert len(all_recs) == 3

    btc = read_decisions(path=log, limit=10, symbol="tBTCUSD")
    assert len(btc) == 2
    assert all(r["symbol"] == "tBTCUSD" for r in btc)


def test_read_decisions_missing_file_returns_empty(tmp_path) -> None:
    assert read_decisions(path=tmp_path / "nope.jsonl") == []


def test_find_decision_skips_followup_records(tmp_path) -> None:
    log = tmp_path / "decisions.jsonl"
    rec = _make_record()
    append_decision(rec, path=log)
    append_followup(
        decision_id=rec.decision_id,
        submission={"submitted": True, "request": {}, "response": {}},
        path=log,
    )
    found = find_decision(rec.decision_id, path=log)
    assert found is not None
    assert found.get("kind") != "submission_followup"
    assert found["fib_signal"]["action"] == "LONG"


def test_appended_lines_are_valid_json(tmp_path) -> None:
    log = tmp_path / "decisions.jsonl"
    append_decision(_make_record(), path=log)
    content = log.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 1
    parsed = json.loads(content[0])
    assert parsed["symbol"] == "tBTCUSD"
    assert parsed["schema_version"] == "v1"
