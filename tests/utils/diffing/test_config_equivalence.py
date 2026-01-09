from __future__ import annotations

from core.utils.diffing.config_equivalence import compare_trial_config_to_results


def test_compare_trial_config_to_results_ok_with_float_rounding():
    trial_cfg = {
        "merged_config": {
            "thresholds": {"entry_conf_overall": 0.4500000001},
            "risk": {"risk_map": [[0.6, 0.010000001], [0.7, 0.02]]},
        },
        "runtime_version": 5,
    }

    results = {
        "merged_config": {
            "risk": {"risk_map": [[0.6, 0.01], [0.7, 0.02]]},
            "thresholds": {"entry_conf_overall": 0.45},
        },
        "runtime_version": 5,
        "config_provenance": {
            "used_runtime_merge": False,
            "config_file_is_complete": True,
        },
    }

    ok, report = compare_trial_config_to_results(trial_cfg, results, precision=6)
    assert ok is True
    assert report["ok"] is True
    assert report["issues"] == []


def test_compare_trial_config_to_results_detects_value_mismatch():
    trial_cfg = {
        "merged_config": {"exit": {"exit_conf_threshold": 0.4}},
        "runtime_version": 1,
    }
    results = {
        "merged_config": {"exit": {"exit_conf_threshold": 0.35}},
        "runtime_version": 1,
        "config_provenance": {"used_runtime_merge": False, "config_file_is_complete": True},
    }

    ok, report = compare_trial_config_to_results(trial_cfg, results)
    assert ok is False
    assert "merged_config mismatch" in report["issues"]
    assert any(d["path"] == "exit.exit_conf_threshold" for d in report["diffs"])


def test_compare_trial_config_to_results_detects_runtime_version_mismatch():
    trial_cfg = {"merged_config": {"a": 1}, "runtime_version": 2}
    results = {
        "merged_config": {"a": 1},
        "runtime_version": 3,
        "config_provenance": {"used_runtime_merge": False, "config_file_is_complete": True},
    }

    ok, report = compare_trial_config_to_results(trial_cfg, results)
    assert ok is False
    assert any("runtime_version mismatch" in msg for msg in report["issues"])


def test_compare_trial_config_to_results_flags_provenance_inconsistency():
    trial_cfg = {"merged_config": {"a": 1}, "runtime_version": 2}
    results = {
        "merged_config": {"a": 1},
        "runtime_version": 2,
        "config_provenance": {
            "used_runtime_merge": True,
            "config_file_is_complete": False,
        },
    }

    ok, report = compare_trial_config_to_results(trial_cfg, results)
    assert ok is False
    assert any("used_runtime_merge" in msg for msg in report["issues"])
    assert any("config_file_is_complete" in msg for msg in report["issues"])
