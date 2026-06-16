from __future__ import annotations

import json
from pathlib import Path

from tools.reconcile_forward_backtest import (
    ACTION_DRIFT,
    BACKTEST_ONLY,
    FORWARD_ONLY,
    MATCH,
    PRICE_SLIPPAGE,
    SIZE_DRIFT,
    build_artifact,
    main,
    reconcile,
)


def _row(ts: int, action: str, *, size=None, price=None, symbol="tBTCUSD", tf="1h") -> dict:
    row = {"timestamp": ts, "symbol": symbol, "timeframe": tf, "action": action}
    if size is not None:
        row["size"] = size
    if price is not None:
        row["price"] = price
    return row


def test_perfect_transfer_is_full_fidelity() -> None:
    bt = [_row(1, "LONG", size=0.005, price=100.0), _row(2, "NONE")]
    fw = [_row(1, "LONG", size=0.005, price=100.0), _row(2, "NONE")]
    result = reconcile(backtest_rows=bt, forward_rows=fw)
    assert result.fidelity_ratio == 1.0
    assert result.counts == {MATCH: 2}


def test_action_drift_detected() -> None:
    bt = [_row(1, "LONG")]
    fw = [_row(1, "SHORT")]
    result = reconcile(backtest_rows=bt, forward_rows=fw)
    assert result.counts.get(ACTION_DRIFT) == 1
    assert result.fidelity_ratio == 0.0


def test_size_drift_detected_above_tolerance() -> None:
    bt = [_row(1, "LONG", size=0.005)]
    fw = [_row(1, "LONG", size=0.010)]
    result = reconcile(backtest_rows=bt, forward_rows=fw)
    assert result.counts.get(SIZE_DRIFT) == 1
    out = next(o for o in result.outcomes if o.key.startswith("ts=1"))
    assert out.size_delta == 0.005


def test_price_slippage_classified_when_action_and_size_match() -> None:
    bt = [_row(1, "LONG", size=0.005, price=100.0)]
    fw = [_row(1, "LONG", size=0.005, price=100.2)]  # +20 bps
    result = reconcile(backtest_rows=bt, forward_rows=fw, slippage_tolerance_bps=5.0)
    assert result.counts.get(PRICE_SLIPPAGE) == 1
    assert result.mean_abs_slippage_bps is not None
    assert round(result.mean_abs_slippage_bps, 1) == 20.0


def test_slippage_within_tolerance_is_match() -> None:
    bt = [_row(1, "LONG", size=0.005, price=100.0)]
    fw = [_row(1, "LONG", size=0.005, price=100.02)]  # +2 bps < 5 bps tol
    result = reconcile(backtest_rows=bt, forward_rows=fw, slippage_tolerance_bps=5.0)
    assert result.counts.get(MATCH) == 1


def test_forward_only_and_backtest_only() -> None:
    bt = [_row(1, "LONG")]
    fw = [_row(2, "SHORT")]
    result = reconcile(backtest_rows=bt, forward_rows=fw)
    assert result.counts.get(BACKTEST_ONLY) == 1
    assert result.counts.get(FORWARD_ONLY) == 1
    assert result.total_keys == 2


def test_action_drift_takes_precedence_over_size() -> None:
    bt = [_row(1, "LONG", size=0.005)]
    fw = [_row(1, "SHORT", size=0.010)]
    result = reconcile(backtest_rows=bt, forward_rows=fw)
    assert result.counts.get(ACTION_DRIFT) == 1
    assert SIZE_DRIFT not in result.counts


def test_artifact_excludes_matches_and_rounds() -> None:
    bt = [_row(1, "LONG", size=0.005, price=100.0), _row(2, "LONG")]
    fw = [_row(1, "LONG", size=0.005, price=100.0), _row(2, "SHORT")]
    result = reconcile(backtest_rows=bt, forward_rows=fw)
    artifact = build_artifact(result, run_id="t1")
    assert artifact["run_id"] == "t1"
    assert artifact["counts"].get(MATCH) == 1
    # Only the divergent row appears in detail list.
    assert len(artifact["divergences"]) == 1
    assert artifact["divergences"][0]["label"] == ACTION_DRIFT


def test_cli_writes_artifact(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt.json"
    fw_path = tmp_path / "fw.json"
    out_path = tmp_path / "recon.json"
    bt_path.write_text(json.dumps([_row(1, "LONG", size=0.005)]), encoding="utf-8")
    fw_path.write_text(json.dumps([_row(1, "NONE")]), encoding="utf-8")
    rc = main([str(bt_path), str(fw_path), "--run-id", "cli", "--artifact-out", str(out_path)])
    assert rc == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "cli"
    assert payload["counts"].get(ACTION_DRIFT) == 1


def test_ndjson_input_supported(tmp_path: Path) -> None:
    bt_path = tmp_path / "bt.ndjson"
    fw_path = tmp_path / "fw.ndjson"
    bt_path.write_text("\n".join(json.dumps(_row(i, "LONG")) for i in range(1, 4)), encoding="utf-8")
    fw_path.write_text("\n".join(json.dumps(_row(i, "LONG")) for i in range(1, 4)), encoding="utf-8")
    rc = main([str(bt_path), str(fw_path)])
    assert rc == 0
