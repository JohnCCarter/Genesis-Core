from __future__ import annotations

import json
from pathlib import Path

from tools.compare_backtest_results import (
    build_ri_p1_off_parity_artifact,
    compare_backtest_payloads,
    compare_ri_p1_off_parity_rows,
    main,
)


def test_compare_backtest_payloads_pass_equal() -> None:
    baseline = {
        "score": 1.0,
        "summary": {
            "total_return": 0.1,
            "profit_factor": 1.2,
            "max_drawdown": 0.05,
            "total_trades": 10,
        },
    }
    candidate = json.loads(json.dumps(baseline))

    result = compare_backtest_payloads(baseline=baseline, candidate=candidate, mode="strict")
    assert result.status == "PASS"


def test_compare_backtest_payloads_fail_regression() -> None:
    baseline = {
        "score": 1.0,
        "summary": {
            "total_return": 0.1,
            "profit_factor": 1.2,
            "max_drawdown": 0.05,
            "total_trades": 10,
        },
    }
    candidate = {
        "score": 0.9,
        "summary": {
            "total_return": 0.0,
            "profit_factor": 1.1,
            "max_drawdown": 0.06,
            "total_trades": 9,
        },
    }

    result = compare_backtest_payloads(baseline=baseline, candidate=candidate, mode="strict")
    assert result.status == "FAIL"
    assert result.failure == "REGRESSION"


def test_compare_backtest_payloads_invalid_shape() -> None:
    result = compare_backtest_payloads(baseline=[], candidate={}, mode="strict")  # type: ignore[arg-type]
    assert result.status == "FAIL"
    assert result.failure == "INPUT_INVALID_SHAPE"


def test_compare_ri_p1_off_parity_rows_pass_order_insensitive() -> None:
    baseline_rows = [
        {"row_id": 1, "action": "LONG", "reason": ["ENTRY_LONG"], "size": 1.0},
        {"row_id": 2, "action": "NONE", "reason": "COOLDOWN", "size": 0.0},
    ]
    candidate_rows = [
        {"row_id": 2, "action": "NONE", "reason": "COOLDOWN", "size": 0.0},
        {"row_id": 1, "action": "LONG", "reason": ["ENTRY_LONG"], "size": 1.0},
    ]

    result = compare_ri_p1_off_parity_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
    )

    assert result.parity_verdict == "PASS"
    assert result.action_mismatch_count == 0
    assert result.reason_mismatch_count == 0
    assert result.size_mismatch_count == 0
    assert result.added_row_count == 0
    assert result.missing_row_count == 0


def test_compare_ri_p1_off_parity_rows_fail_action_mismatch() -> None:
    baseline_rows = [{"row_id": 1, "action": "LONG", "reason": "ENTRY_LONG", "size": 1.0}]
    candidate_rows = [{"row_id": 1, "action": "SHORT", "reason": "ENTRY_LONG", "size": 1.0}]

    result = compare_ri_p1_off_parity_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
    )

    assert result.parity_verdict == "FAIL"
    assert result.action_mismatch_count == 1
    assert result.reason_mismatch_count == 0
    assert result.size_mismatch_count == 0


def test_compare_ri_p1_off_parity_rows_fail_reason_mismatch() -> None:
    baseline_rows = [{"row_id": 1, "action": "LONG", "reason": "ENTRY_LONG", "size": 1.0}]
    candidate_rows = [{"row_id": 1, "action": "LONG", "reason": "ENTRY_SHORT", "size": 1.0}]

    result = compare_ri_p1_off_parity_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
    )

    assert result.parity_verdict == "FAIL"
    assert result.action_mismatch_count == 0
    assert result.reason_mismatch_count == 1
    assert result.size_mismatch_count == 0


def test_compare_ri_p1_off_parity_rows_fail_size_tolerance_breach() -> None:
    baseline_rows = [{"row_id": 1, "action": "LONG", "reason": "ENTRY_LONG", "size": 1.0}]
    candidate_rows = [{"row_id": 1, "action": "LONG", "reason": "ENTRY_LONG", "size": 1.0 + 2e-12}]

    result = compare_ri_p1_off_parity_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
        size_tolerance=1e-12,
    )

    assert result.parity_verdict == "FAIL"
    assert result.action_mismatch_count == 0
    assert result.reason_mismatch_count == 0
    assert result.size_mismatch_count == 1


def test_compare_ri_p1_off_parity_rows_pass_when_both_sizes_none() -> None:
    baseline_rows = [{"row_id": 1, "action": "NONE", "reason": "NO_ENTRY", "size": None}]
    candidate_rows = [{"row_id": 1, "action": "NONE", "reason": "NO_ENTRY", "size": None}]

    result = compare_ri_p1_off_parity_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
    )

    assert result.parity_verdict == "PASS"
    assert result.size_mismatch_count == 0


def test_compare_ri_p1_off_parity_rows_fail_when_only_one_size_none() -> None:
    baseline_rows = [{"row_id": 1, "action": "NONE", "reason": "NO_ENTRY", "size": None}]
    candidate_rows = [{"row_id": 1, "action": "NONE", "reason": "NO_ENTRY", "size": 0.0}]

    result = compare_ri_p1_off_parity_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
    )

    assert result.parity_verdict == "FAIL"
    assert result.size_mismatch_count == 1


def test_compare_ri_p1_off_parity_rows_fail_missing_row() -> None:
    baseline_rows = [
        {"row_id": 1, "action": "LONG", "reason": "ENTRY_LONG", "size": 1.0},
        {"row_id": 2, "action": "NONE", "reason": "COOLDOWN", "size": 0.0},
    ]
    candidate_rows = [{"row_id": 1, "action": "LONG", "reason": "ENTRY_LONG", "size": 1.0}]

    result = compare_ri_p1_off_parity_rows(
        baseline_rows=baseline_rows,
        candidate_rows=candidate_rows,
    )

    assert result.parity_verdict == "FAIL"
    assert result.missing_row_count == 1
    assert result.added_row_count == 0


def test_build_ri_p1_off_parity_artifact_required_fields() -> None:
    rows = [{"row_id": 1, "action": "LONG", "reason": "ENTRY_LONG", "size": 1.0}]

    artifact = build_ri_p1_off_parity_artifact(
        run_id="ri-20260303-001",
        git_sha="abc1234",
        symbols=["tTESTBTC:TESTUSD"],
        timeframes=["1h"],
        start_utc="2025-01-01T00:00:00Z",
        end_utc="2025-01-31T23:59:59Z",
        baseline_artifact_ref="results/evaluation/ri_p1_off_parity_v1_baseline.json",
        baseline_rows=rows,
        candidate_rows=rows,
    )

    assert artifact["window_spec_id"] == "ri_p1_off_parity_v1"
    assert artifact["run_id"] == "ri-20260303-001"
    assert artifact["git_sha"] == "abc1234"
    assert artifact["mode"] == "OFF"
    assert artifact["symbols"] == ["tTESTBTC:TESTUSD"]
    assert artifact["timeframes"] == ["1h"]
    assert artifact["start_utc"] == "2025-01-01T00:00:00Z"
    assert artifact["end_utc"] == "2025-01-31T23:59:59Z"
    assert artifact["baseline_artifact_ref"]
    assert artifact["parity_verdict"] == "PASS"
    assert artifact["action_mismatch_count"] == 0
    assert artifact["reason_mismatch_count"] == 0
    assert artifact["size_mismatch_count"] == 0
    assert artifact["size_tolerance"] == "1e-12"


def test_main_legacy_compare_path_unchanged(tmp_path: Path, capsys) -> None:
    baseline = {
        "score": 1.0,
        "summary": {
            "total_return": 0.1,
            "profit_factor": 1.2,
            "max_drawdown": 0.05,
            "total_trades": 10,
        },
    }
    candidate = json.loads(json.dumps(baseline))

    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

    rc = main([str(baseline_path), str(candidate_path), "--json"])
    assert rc == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"
    assert "baseline_metrics" in payload
    assert "candidate_metrics" in payload
    assert "deltas" in payload


def test_main_ri_off_parity_pass_writes_default_artifact(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    baseline_rows = [
        {"row_id": 1, "action": "LONG", "reason": ["ENTRY_LONG"], "size": 1.0},
        {"row_id": 2, "action": "NONE", "reason": "COOLDOWN", "size": 0.0},
    ]
    candidate_rows = [
        {"row_id": 2, "action": "NONE", "reason": "COOLDOWN", "size": 0.0},
        {"row_id": 1, "action": "LONG", "reason": ["ENTRY_LONG"], "size": 1.0},
    ]

    baseline_path = tmp_path / "baseline_rows.json"
    candidate_path = tmp_path / "candidate_rows.ndjson"

    baseline_path.write_text(json.dumps(baseline_rows), encoding="utf-8")
    with candidate_path.open("w", encoding="utf-8") as handle:
        for row in candidate_rows:
            handle.write(json.dumps(row, separators=(",", ":"), sort_keys=True))
            handle.write("\n")

    monkeypatch.chdir(tmp_path)
    run_id = "ri-20260303-002"
    rc = main(
        [
            str(baseline_path),
            str(candidate_path),
            "--ri-off-parity",
            "--run-id",
            run_id,
            "--git-sha",
            "abc1234",
            "--symbols",
            "tTESTBTC:TESTUSD",
            "--timeframes",
            "1h",
            "--start-utc",
            "2025-01-01T00:00:00Z",
            "--end-utc",
            "2025-01-31T23:59:59Z",
            "--baseline-artifact-ref",
            "results/evaluation/ri_p1_off_parity_v1_baseline.json",
            "--json",
        ]
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"

    artifact_path = Path(payload["artifact_path"])
    assert artifact_path == Path("results/evaluation") / f"ri_p1_off_parity_v1_{run_id}.json"
    assert artifact_path.exists()

    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["window_spec_id"] == "ri_p1_off_parity_v1"
    assert artifact["parity_verdict"] == "PASS"


def test_main_ri_off_parity_fail_returns_1(tmp_path: Path, capsys) -> None:
    baseline_rows = [{"row_id": 1, "action": "LONG", "reason": "ENTRY_LONG", "size": 1.0}]
    candidate_rows = [{"row_id": 1, "action": "SHORT", "reason": "ENTRY_LONG", "size": 1.0}]

    baseline_path = tmp_path / "baseline_rows.json"
    candidate_path = tmp_path / "candidate_rows.json"
    baseline_path.write_text(json.dumps(baseline_rows), encoding="utf-8")
    candidate_path.write_text(json.dumps(candidate_rows), encoding="utf-8")

    rc = main(
        [
            str(baseline_path),
            str(candidate_path),
            "--ri-off-parity",
            "--run-id",
            "ri-20260303-003",
            "--git-sha",
            "abc1234",
            "--symbols",
            "tTESTBTC:TESTUSD",
            "--timeframes",
            "1h",
            "--start-utc",
            "2025-01-01T00:00:00Z",
            "--end-utc",
            "2025-01-31T23:59:59Z",
            "--baseline-artifact-ref",
            "results/evaluation/ri_p1_off_parity_v1_baseline.json",
        ]
    )

    assert rc == 1
    text = capsys.readouterr().out
    assert "[RI-OFF-PARITY] FAIL" in text


def test_main_ri_off_parity_missing_required_args_returns_2(tmp_path: Path, capsys) -> None:
    baseline_path = tmp_path / "baseline_rows.json"
    candidate_path = tmp_path / "candidate_rows.json"
    baseline_path.write_text("[]", encoding="utf-8")
    candidate_path.write_text("[]", encoding="utf-8")

    rc = main([str(baseline_path), str(candidate_path), "--ri-off-parity"])
    assert rc == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["failure"] == "INPUT_INVALID_SHAPE"
    assert "Missing required args for --ri-off-parity" in payload["message"]
