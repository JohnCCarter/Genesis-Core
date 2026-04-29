from __future__ import annotations

import json
from pathlib import Path

from scripts.analyze.edge_origin_isolation import (
    EdgeOriginIsolationError,
    main,
    normalize_timestamp,
    run_edge_origin_isolation,
)


def _trace_row(
    *,
    bar_index: int,
    timestamp: str,
    base_size: float,
    final_size: float,
    selected_candidate: str = "LONG",
) -> dict[str, object]:
    return {
        "bar_index": bar_index,
        "timestamp": timestamp,
        "decision_phase": {
            "selected_candidate": selected_candidate,
            "p_buy": 0.61,
            "p_sell": 0.39,
            "ev_long": 0.22,
            "ev_short": -0.22,
            "max_ev": 0.22,
        },
        "sizing_phase": {
            "candidate": selected_candidate,
            "base_size": base_size,
            "size_scale": 1.25,
            "volatility_adjustment": 0.9,
            "regime_multiplier": 1.1,
            "htf_regime_multiplier": 0.95,
            "combined_multiplier": 1.175,
            "final_size": final_size,
        },
        "final": {
            "action": selected_candidate,
            "size": final_size,
            "regime": "trend",
            "htf_regime": "bullish",
            "reasons": ["ZONE:mid@0.300", f"ENTRY_{selected_candidate}"],
            "zone_debug": {"zone": "mid", "atr": 125.0},
        },
        "fib_phase": {
            "ltf_debug": {
                "price": 43000.0 + bar_index,
                "atr": 125.0,
                "tolerance": 156.25,
            }
        },
    }


def _build_payloads() -> tuple[dict[str, object], dict[str, object]]:
    baseline = {
        "name": "baseline_current",
        "trade_signatures": [
            {
                "entry_timestamp": "2024-01-01T00:00:00",
                "exit_timestamp": "2024-01-01T06:00:00",
                "side": "CLOSE_LONG",
                "size": 2.0,
                "pnl": 4.0,
            },
            {
                "entry_timestamp": "2024-01-01T03:00:00",
                "exit_timestamp": "2024-01-01T09:00:00",
                "side": "CLOSE_LONG",
                "size": 1.5,
                "pnl": -1.5,
            },
            {
                "entry_timestamp": "2024-01-01T03:00:00",
                "exit_timestamp": "2024-01-01T12:00:00",
                "side": "CLOSE_LONG",
                "size": 3.0,
                "pnl": 6.0,
            },
        ],
        "trace_rows": [
            _trace_row(
                bar_index=0, timestamp="2024-01-01T00:00:00+00:00", base_size=1.8, final_size=2.0
            ),
            _trace_row(
                bar_index=1, timestamp="2024-01-01T03:00:00+00:00", base_size=2.6, final_size=3.0
            ),
            _trace_row(
                bar_index=2, timestamp="2024-01-01T06:00:00+00:00", base_size=0.0, final_size=0.0
            ),
            _trace_row(
                bar_index=3, timestamp="2024-01-01T09:00:00+00:00", base_size=0.0, final_size=0.0
            ),
            _trace_row(
                bar_index=4, timestamp="2024-01-01T12:00:00+00:00", base_size=0.0, final_size=0.0
            ),
        ],
    }
    adaptation_off = {
        "name": "adaptation_off",
        "trade_signatures": [],
        "trace_rows": [
            _trace_row(
                bar_index=0, timestamp="2024-01-01T00:00:00+00:00", base_size=1.8, final_size=2.0
            ),
            _trace_row(
                bar_index=1, timestamp="2024-01-01T03:00:00+00:00", base_size=2.6, final_size=3.0
            ),
            _trace_row(
                bar_index=2, timestamp="2024-01-02T00:00:00+00:00", base_size=1.1, final_size=1.25
            ),
        ],
    }
    return baseline, adaptation_off


def test_normalize_timestamp_removes_suffix_once() -> None:
    assert normalize_timestamp("2024-01-01T00:00:00+00:00") == "2024-01-01T00:00:00"
    assert normalize_timestamp("2024-01-01T00:00:00") == "2024-01-01T00:00:00"


def test_run_edge_origin_isolation_outputs_required_surfaces() -> None:
    baseline, adaptation_off = _build_payloads()

    outputs = run_edge_origin_isolation(
        baseline, adaptation_off, seed=20260402, shuffle_iterations=32
    )

    assert sorted(outputs) == sorted(
        [
            "audit_phase10_determinism.json",
            "counterfactual_matrix.json",
            "execution_attribution.json",
            "execution_summary.md",
            "path_dependency.json",
            "path_summary.md",
            "selection_attribution.json",
            "selection_summary.md",
            "sizing_attribution.json",
            "sizing_summary.md",
        ]
    )
    execution = outputs["execution_attribution.json"]
    assert execution["analysis_population"]["join_status"] == "EXACT_ONE_MATCH_PER_TRADE"
    omitted = {item["name"] for item in execution["omitted_subtests"]}
    assert omitted == {
        "MAE_MFE",
        "price_path_fixed_exit",
        "deterministic_entry_shift",
        "fixed_horizon_exit_k_bars",
    }

    sizing = outputs["sizing_attribution.json"]
    assert sizing["baseline_metrics"]["trade_count"] == 3
    assert sizing["unit_size_metrics"]["trade_count"] == 3

    selection = outputs["selection_attribution.json"]
    assert selection["selection_surface_status"] == "CONTRAST_AVAILABLE"
    assert selection["selection_metrics"]["shared_opportunity_count"] == 2
    assert selection["selection_metrics"]["adaptation_off_only_opportunity_count"] == 1

    matrix = outputs["counterfactual_matrix.json"]
    assert [item["control_name"] for item in matrix] == [
        "unit_size_normalization",
        "trade_order_shuffle",
    ]
    assert all(item["status"] == "PASS" for item in matrix)

    audit = outputs["audit_phase10_determinism.json"]
    assert audit["match"] is True
    assert audit["join_integrity"]["join_status"] == "EXACT_ONE_MATCH_PER_TRADE"


def test_run_edge_origin_isolation_repeatable_with_same_seed() -> None:
    baseline, adaptation_off = _build_payloads()

    run1 = run_edge_origin_isolation(baseline, adaptation_off, seed=20260402, shuffle_iterations=24)
    run2 = run_edge_origin_isolation(baseline, adaptation_off, seed=20260402, shuffle_iterations=24)

    assert run1 == run2


def test_run_edge_origin_isolation_rejects_duplicate_normalized_trace_timestamp() -> None:
    baseline, adaptation_off = _build_payloads()
    baseline["trace_rows"] = list(baseline["trace_rows"])
    baseline["trace_rows"].append(
        _trace_row(bar_index=99, timestamp="2024-01-01T03:00:00", base_size=1.0, final_size=1.0)
    )

    try:
        run_edge_origin_isolation(baseline, adaptation_off, seed=20260402, shuffle_iterations=8)
    except EdgeOriginIsolationError as exc:
        assert "duplicate normalized baseline trace timestamps" in str(exc)
    else:
        raise AssertionError("expected duplicate normalized timestamp failure")


def test_edge_origin_isolation_cli_smoke(tmp_path: Path, capsys) -> None:
    baseline, adaptation_off = _build_payloads()
    baseline_path = tmp_path / "trace_baseline_current.json"
    adaptation_path = tmp_path / "trace_adaptation_off.json"
    out_dir = tmp_path / "out"

    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    adaptation_path.write_text(json.dumps(adaptation_off), encoding="utf-8")

    rc = main(
        [
            str(baseline_path),
            str(adaptation_path),
            "--out-dir",
            str(out_dir),
            "--seed",
            "20260402",
            "--shuffle-iterations",
            "16",
            "--json",
        ]
    )
    assert rc == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"
    assert payload["match"] is True
    assert payload["join_status"] == "EXACT_ONE_MATCH_PER_TRADE"

    expected_files = {
        "execution_attribution.json",
        "execution_summary.md",
        "sizing_attribution.json",
        "sizing_summary.md",
        "path_dependency.json",
        "path_summary.md",
        "selection_attribution.json",
        "selection_summary.md",
        "counterfactual_matrix.json",
        "audit_phase10_determinism.json",
    }
    assert expected_files == {path.name for path in out_dir.iterdir()}
