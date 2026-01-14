from __future__ import annotations

from scripts.extract_backtest_provenance import extract_provenance


def test_extract_provenance_minimal_payload() -> None:
    payload = {
        "backtest_info": {
            "symbol": "tBTCUSD",
            "timeframe": "1h",
            "start_date": "2024-01-01 00:00:00+00:00",
            "end_date": "2024-12-31 00:00:00+00:00",
            "git_hash": "abc123",
            "seed": 42,
            "timestamp": "2026-01-12T14:21:53Z",
            "execution_mode": {
                "fast_window": True,
                "env_precompute_features": "1",
                "precomputed_ready": True,
                "mode_explicit": "0",
                "env_htf_exits": "1",
            },
        },
        "config_provenance": {
            "config_file": "config\\strategy\\champions\\tBTCUSD_1h.json",
            "runtime_version_used": 22,
            "runtime_version_current": 23,
        },
        "merged_config": {"thresholds": {"entry_conf_overall": 0.35}},
    }

    out = extract_provenance(payload)

    assert out["symbol"] == "tBTCUSD"
    assert out["timeframe"] == "1h"
    assert out["period"]["start_date"] == "2024-01-01 00:00:00+00:00"
    assert out["execution_mode"]["fast_window"] is True
    assert out["provenance"]["config_file"].endswith("tBTCUSD_1h.json")
    assert out["provenance"]["runtime_version_used"] == 22
    assert out["provenance"]["runtime_version_current"] == 23
    assert out["provenance"]["has_merged_config"] is True
