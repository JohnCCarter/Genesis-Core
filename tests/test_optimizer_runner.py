from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml

try:
    import optuna
except ImportError:
    optuna = None

import core.optimizer.runner as runner
from core.optimizer.runner import run_optimizer


@pytest.fixture()
def search_config_tmp(tmp_path: Path) -> Path:
    config = {
        "meta": {
            "symbol": "tTEST",
            "timeframe": "1h",
            "snapshot_id": "tTEST_1h_20240101_20240201_v1",
            "warmup_bars": 50,
            "runs": {
                "max_trials": 2,
                "resume": False,
            },
        },
        "parameters": {
            "thresholds": {
                "entry_conf_overall": {
                    "type": "grid",
                    "values": [0.4, 0.5],
                }
            }
        },
    }
    config_path = tmp_path / "search.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def test_score_version_mismatch_is_fail_fast() -> None:
    with pytest.raises(ValueError, match="Inkompatibla scoring-versioner"):
        runner._enforce_score_version_compatibility(
            current_score_version="v1",
            candidate_score_version="v2",
            context="unit_test",
        )


def test_derive_dates_supports_snap_prefix_symbol_timeframe_iso_dates() -> None:
    start, end = runner._derive_dates("snap_tBTCUSD_3h_2024-01-02_2024-12-31_v1")
    assert start == "2024-01-02"
    assert end == "2024-12-31"


def test_collect_comparability_warnings_detects_drift_without_raising() -> None:
    current_info = {
        "execution_mode": {
            "fast_window": True,
            "env_precompute_features": "1",
            "precompute_enabled": True,
            "precomputed_ready": True,
            "mode_explicit": "0",
        },
        "commission_rate": 0.002,
        "slippage_rate": 0.0,
        "git_hash": "abc",
        "seed": "42",
        "htf": {
            "env_htf_exits": "1",
            "use_new_exit_engine": True,
            "htf_candles_loaded": True,
            "htf_context_seen": True,
        },
    }
    candidate_info = {
        "execution_mode": {
            "fast_window": False,
            "env_precompute_features": "1",
            "precompute_enabled": True,
            "precomputed_ready": False,
            "mode_explicit": "1",
        },
        "commission_rate": 0.001,
        "slippage_rate": 0.0,
        "git_hash": "def",
        "seed": "123",
        "htf": {
            "env_htf_exits": "0",
            "use_new_exit_engine": False,
            "htf_candles_loaded": False,
            "htf_context_seen": False,
        },
    }

    warnings = runner._collect_comparability_warnings(current_info, candidate_info)
    assert any("execution_mode.fast_window" in w for w in warnings)
    assert any("execution_mode.precomputed_ready" in w for w in warnings)
    assert any("commission_rate" in w for w in warnings)
    assert any("git_hash" in w for w in warnings)
    assert any("htf.env_htf_exits" in w for w in warnings)


def test_run_optimizer_updates_champion(
    tmp_path: Path, search_config_tmp: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results_root = tmp_path / "results" / "hparam_search"
    run_meta_payload = {
        "git_commit": "abc123",
        "snapshot_id": "tTEST_1h_20240101_20240201_v1",
    }

    trial_queue = {
        1: {
            "trial_id": "trial_001",
            "parameters": {"thresholds": {"entry_conf_overall": 0.4}},
            "score": {
                "score": 120.0,
                "metrics": {"sharpe_ratio": 0.5},
                "hard_failures": [],
            },
            "constraints": {"ok": True, "reasons": []},
            "results_path": "test_results.json",
        },
        2: {
            "trial_id": "trial_002",
            "parameters": {"thresholds": {"entry_conf_overall": 0.5}},
            "score": {
                "score": 80.0,
                "metrics": {"sharpe_ratio": 0.2},
                "hard_failures": ["MAX_DD_TOO_HIGH"],
            },
            "constraints": {"ok": False, "reasons": ["MAX_DD_TOO_HIGH"]},
            "results_path": "test_results_bad.json",
        },
    }

    created_run_dir: Path | None = None

    def fake_run_trial(*args: Any, **kwargs: Any) -> dict[str, Any]:
        index = kwargs.get("index")
        return trial_queue.get(
            index,
            {
                "trial_id": f"trial_extra_{index}",
                "parameters": {},
                "score": {"score": 0.0, "metrics": {}, "hard_failures": []},
                "constraints": {"ok": False},
            },
        )

    def fake_ensure(run_dir: Path, *_args: Any, **_kwargs: Any) -> None:
        nonlocal created_run_dir
        created_run_dir = run_dir
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_meta.json").write_text(json.dumps(run_meta_payload), encoding="utf-8")

    with (
        patch.dict(os.environ, {"GENESIS_MAX_CONCURRENT": "1"}),
        patch("core.optimizer.runner.RESULTS_DIR", results_root),
        patch(
            "core.optimizer.runner.expand_parameters",
            return_value=[
                {"thresholds": {"entry_conf_overall": 0.4}},
                {"thresholds": {"entry_conf_overall": 0.5}},
            ],
        ),
        patch("core.optimizer.runner.run_trial", side_effect=fake_run_trial),
        patch("core.optimizer.runner._ensure_run_metadata", side_effect=fake_ensure),
        patch("core.optimizer.runner.ChampionManager") as manager_cls,
        patch("core.strategy.champion_loader.CHAMPIONS_DIR", tmp_path / "champions"),
    ):
        monkeypatch.setenv("GENESIS_MAX_CONCURRENT", "1")
        manager_instance = manager_cls.return_value
        manager_instance.load_current.return_value = None
        manager_instance.should_replace.return_value = True

        results = run_optimizer(search_config_tmp, run_id="run_test")

        assert len(results) == 2
        manager_instance.write_champion.assert_called_once()
        call_kwargs = manager_instance.write_champion.call_args.kwargs
        assert call_kwargs["run_id"] == "run_test"
        assert call_kwargs["candidate"].score == pytest.approx(120.0)
        assert call_kwargs["snapshot_id"] == run_meta_payload["snapshot_id"]


def test_run_optimizer_validation_stage_promotes_validation_best(tmp_path: Path) -> None:
    config = {
        "meta": {
            "symbol": "tTEST",
            "timeframe": "1h",
            "snapshot_id": "tTEST_1h_20240101_20240201_v1",
            "warmup_bars": 50,
            "runs": {
                "max_trials": 2,
                "resume": False,
                "validation": {
                    "top_n": 2,
                    "use_sample_range": True,
                    "sample_start": "2024-01-01",
                    "sample_end": "2024-03-01",
                    "constraints": {"min_trades": 1, "min_profit_factor": 1.0},
                },
            },
        },
        "parameters": {
            "thresholds": {
                "entry_conf_overall": {
                    "type": "grid",
                    "values": [0.4, 0.5],
                }
            }
        },
    }
    config_path = tmp_path / "search_with_validation.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    results_root = tmp_path / "results" / "hparam_search"
    run_meta_payload = {
        "git_commit": "abc123",
        "snapshot_id": "tTEST_1h_20240101_20240201_v1",
    }

    def fake_run_trial(*args: Any, **kwargs: Any) -> dict[str, Any]:
        trial_cfg = args[0]
        run_dir = kwargs.get("run_dir")
        params = getattr(trial_cfg, "parameters", {}) or {}
        entry_conf = params.get("thresholds", {}).get("entry_conf_overall")

        # Explore stage (main run_dir)
        if run_dir is None or "validation" not in str(run_dir):
            if entry_conf == 0.4:
                return {
                    "trial_id": "trial_001",
                    "parameters": params,
                    "score": {"score": 120.0, "metrics": {"num_trades": 10}, "hard_failures": []},
                    "constraints": {"ok": True, "reasons": []},
                    "results_path": "explore_good.json",
                }
            return {
                "trial_id": "trial_002",
                "parameters": params,
                "score": {
                    "score": 80.0,
                    "metrics": {"num_trades": 0},
                    "hard_failures": ["pf<1.0"],
                },
                "constraints": {"ok": False, "reasons": ["min_profit_factor"]},
                "results_path": "explore_bad.json",
            }

        # Validation stage (run_dir/validation)
        if entry_conf == 0.4:
            return {
                "trial_id": "trial_001",
                "parameters": params,
                "score": {"score": 90.0, "metrics": {"num_trades": 15}, "hard_failures": []},
                "constraints": {"ok": True, "reasons": []},
                "results_path": "val_ok_04.json",
            }
        return {
            "trial_id": "trial_002",
            "parameters": params,
            "score": {"score": 130.0, "metrics": {"num_trades": 20}, "hard_failures": []},
            "constraints": {"ok": True, "reasons": []},
            "results_path": "val_best_05.json",
        }

    def fake_ensure(run_dir: Path, *_args: Any, **_kwargs: Any) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_meta.json").write_text(json.dumps(run_meta_payload), encoding="utf-8")

    with (
        patch.dict(os.environ, {"GENESIS_MAX_CONCURRENT": "1"}),
        patch("core.optimizer.runner.RESULTS_DIR", results_root),
        patch(
            "core.optimizer.runner.expand_parameters",
            return_value=[
                {"thresholds": {"entry_conf_overall": 0.4}},
                {"thresholds": {"entry_conf_overall": 0.5}},
            ],
        ),
        patch("core.optimizer.runner.run_trial", side_effect=fake_run_trial),
        patch("core.optimizer.runner._ensure_run_metadata", side_effect=fake_ensure),
        patch("core.optimizer.runner.ChampionManager") as manager_cls,
        patch("core.strategy.champion_loader.CHAMPIONS_DIR", tmp_path / "champions"),
    ):
        manager_instance = manager_cls.return_value
        manager_instance.load_current.return_value = None
        manager_instance.should_replace.return_value = True

        results = run_optimizer(config_path, run_id="run_test")

        # 2 explore + 2 validation
        assert len(results) == 4
        manager_instance.write_champion.assert_called_once()
        call_kwargs = manager_instance.write_champion.call_args.kwargs
        assert call_kwargs["candidate"].score == pytest.approx(130.0)


def test_trial_requests_htf_exits_detects_htf_exit_config() -> None:
    assert runner._trial_requests_htf_exits({"htf_exit_config": {"partial_1_pct": 0.5}}) is True
    assert runner._trial_requests_htf_exits({"htf_exit_config": {}}) is False
    assert runner._trial_requests_htf_exits({"htf_exit_config": None}) is False
    assert runner._trial_requests_htf_exits({}) is False


def test_build_backtest_cmd_uses_sys_executable_and_module_invocation(tmp_path: Path) -> None:
    trial = runner.TrialConfig(
        snapshot_id="tTEST_1h_20240101_20240201_v1",
        symbol="tTEST",
        timeframe="1h",
        warmup_bars=50,
        parameters={},
        start_date="2024-01-01",
        end_date="2024-01-02",
    )

    cmd = runner._build_backtest_cmd(
        trial,
        start_date="2024-01-01",
        end_date="2024-01-02",
        capital_default=10_000.0,
        commission_default=0.002,
        slippage_default=0.0,
        config_file=tmp_path / "trial_config.json",
        optuna_context={
            "storage": "sqlite:///dummy.db",
            "study_name": "s",
            "trial_id": 123,
            "pruner": {"type": "none"},
        },
    )

    assert cmd[0] == sys.executable
    assert cmd[1:3] == ["-m", "scripts.run_backtest"]
    assert "--fast-window" in cmd
    assert "--precompute-features" in cmd
    assert "--config-file" in cmd
    assert "--optuna-trial-id" in cmd
    assert "--optuna-pruner" in cmd
    pruner_idx = cmd.index("--optuna-pruner")
    assert cmd[pruner_idx + 1] == "none"


def test_run_optimizer_promotion_disabled_does_not_write_champion(
    tmp_path: Path, search_config_tmp: Path
) -> None:
    results_root = tmp_path / "results" / "hparam_search"
    run_meta_payload = {
        "git_commit": "abc123",
        "snapshot_id": "tTEST_1h_20240101_20240201_v1",
    }

    def fake_run_trial(*_args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "trial_id": f"trial_{kwargs.get('index', 1):03d}",
            "parameters": {"thresholds": {"entry_conf_overall": 0.4}},
            "score": {"score": 120.0, "metrics": {"num_trades": 10}, "hard_failures": []},
            "constraints": {"ok": True, "reasons": []},
            "results_path": "explore_good.json",
        }

    def fake_ensure(run_dir: Path, *_args: Any, **_kwargs: Any) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_meta.json").write_text(json.dumps(run_meta_payload), encoding="utf-8")

    # Patch the config file to disable promotion.
    cfg = yaml.safe_load(search_config_tmp.read_text(encoding="utf-8"))
    cfg["meta"]["runs"]["promotion"] = {"enabled": False}
    search_config_tmp.write_text(yaml.safe_dump(cfg), encoding="utf-8")

    with (
        patch.dict(os.environ, {"GENESIS_MAX_CONCURRENT": "1"}),
        patch("core.optimizer.runner.RESULTS_DIR", results_root),
        patch(
            "core.optimizer.runner.expand_parameters",
            return_value=[{"thresholds": {"entry_conf_overall": 0.4}}],
        ),
        patch("core.optimizer.runner.run_trial", side_effect=fake_run_trial),
        patch("core.optimizer.runner._ensure_run_metadata", side_effect=fake_ensure),
        patch("core.optimizer.runner.ChampionManager") as manager_cls,
        patch("core.strategy.champion_loader.CHAMPIONS_DIR", tmp_path / "champions"),
    ):
        manager_instance = manager_cls.return_value
        manager_instance.load_current.return_value = None
        manager_instance.should_replace.return_value = True

        results = run_optimizer(search_config_tmp, run_id="run_test")

        assert len(results) == 1
        manager_instance.write_champion.assert_not_called()


def test_run_optimizer_promotion_min_improvement_blocks_small_gain(
    tmp_path: Path, search_config_tmp: Path
) -> None:
    results_root = tmp_path / "results" / "hparam_search"
    run_meta_payload = {
        "git_commit": "abc123",
        "snapshot_id": "tTEST_1h_20240101_20240201_v1",
    }

    def fake_run_trial(*_args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "trial_id": f"trial_{kwargs.get('index', 1):03d}",
            "parameters": {"thresholds": {"entry_conf_overall": 0.4}},
            "score": {"score": 102.0, "metrics": {"num_trades": 10}, "hard_failures": []},
            "constraints": {"ok": True, "reasons": []},
            "results_path": "explore_ok.json",
        }

    def fake_ensure(run_dir: Path, *_args: Any, **_kwargs: Any) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_meta.json").write_text(json.dumps(run_meta_payload), encoding="utf-8")

    cfg = yaml.safe_load(search_config_tmp.read_text(encoding="utf-8"))
    cfg["meta"]["runs"]["promotion"] = {"enabled": True, "min_improvement": 5.0}
    search_config_tmp.write_text(yaml.safe_dump(cfg), encoding="utf-8")

    with (
        patch.dict(os.environ, {"GENESIS_MAX_CONCURRENT": "1"}),
        patch("core.optimizer.runner.RESULTS_DIR", results_root),
        patch(
            "core.optimizer.runner.expand_parameters",
            return_value=[{"thresholds": {"entry_conf_overall": 0.4}}],
        ),
        patch("core.optimizer.runner.run_trial", side_effect=fake_run_trial),
        patch("core.optimizer.runner._ensure_run_metadata", side_effect=fake_ensure),
        patch("core.optimizer.runner.ChampionManager") as manager_cls,
        patch("core.strategy.champion_loader.CHAMPIONS_DIR", tmp_path / "champions"),
    ):
        manager_instance = manager_cls.return_value
        manager_instance.load_current.return_value = MagicMock(score=100.0)
        manager_instance.should_replace.return_value = True

        results = run_optimizer(search_config_tmp, run_id="run_test")

        assert len(results) == 1
        manager_instance.write_champion.assert_not_called()


def test_run_trial_uses_scoring_thresholds_from_constraints(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GENESIS_SCORE_VERSION", "v2")
    monkeypatch.delenv("GENESIS_FORCE_SHELL", raising=False)

    trial = runner.TrialConfig(
        snapshot_id="tTEST_1h_20240101_20240201_v1",
        symbol="tTEST",
        timeframe="1h",
        warmup_bars=1,
        parameters={"thresholds": {"entry_conf_overall": 0.4}},
        start_date="2024-01-01",
        end_date="2024-01-02",
    )

    seen: dict[str, Any] = {}

    def fake_score_backtest(
        _results: dict[str, Any], *, thresholds: Any | None = None, score_version: str | None = None
    ) -> dict[str, Any]:
        seen["thresholds"] = thresholds
        seen["score_version"] = score_version
        return {
            "score": 0.0,
            "metrics": {
                "num_trades": 10,
                "total_return": 0.0,
                "profit_factor": 1.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "win_rate": 0.5,
            },
            "hard_failures": [],
            "baseline": {"score_version": score_version or "v1"},
        }

    def fake_run_backtest_direct(*_args: Any, **_kwargs: Any) -> tuple[int, str, dict[str, Any]]:
        return (
            0,
            "",
            {
                "summary": {"initial_capital": 10000.0},
                "trades": [],
                "equity_curve": [],
                "metrics": {"num_trades": 10},
                "merged_config": {},
                "runtime_version": 1,
            },
        )

    with (
        patch("core.optimizer.runner._get_default_config", return_value={}),
        patch("core.optimizer.runner._get_default_runtime_version", return_value=1),
        patch("core.optimizer.runner._check_abort_heuristic", return_value={"ok": True}),
        patch("core.optimizer.runner._run_backtest_direct", side_effect=fake_run_backtest_direct),
        patch("core.optimizer.runner.score_backtest", side_effect=fake_score_backtest),
    ):
        payload = runner.run_trial(
            trial,
            run_id="run_test",
            index=1,
            run_dir=tmp_path,
            allow_resume=False,
            existing_trials={},
            constraints_cfg={
                "scoring_thresholds": {
                    "min_trades": 1,
                    "min_profit_factor": 0.55,
                    "max_max_dd": 0.5,
                }
            },
        )

    assert payload.get("error") is None
    assert seen.get("score_version") == "v2"

    # Trial artifacts must be forensically bound to parameters + score_version.
    cfg = json.loads((tmp_path / "trial_001_config.json").read_text(encoding="utf-8"))
    assert cfg.get("run_id") == "run_test"
    assert cfg.get("trial_id") == "trial_001"
    assert cfg.get("parameters") == {"thresholds": {"entry_conf_overall": 0.4}}
    assert cfg.get("score_version") == "v2"
    assert cfg.get("trial_key") == runner._trial_key(trial.parameters)
    assert cfg.get("param_signature") == runner.param_signature(trial.parameters)

    thresholds = seen.get("thresholds")
    assert thresholds is not None
    assert thresholds.min_trades == 1
    assert thresholds.min_profit_factor == pytest.approx(0.55)
    assert thresholds.max_max_dd == pytest.approx(0.5)


def test_extract_results_path_from_log_parses_run_backtest_format(tmp_path: Path) -> None:
    out_json = tmp_path / "out.json"
    out_json.write_text("{}\n", encoding="utf-8")

    log_content = f"[OK] Results saved:\njson: {out_json}\ntrades_csv: whatever.csv\n"
    parsed = runner._extract_results_path_from_log(log_content)
    assert parsed == out_json


def test_run_trial_abort_payload_is_strict_json_and_includes_score_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GENESIS_SCORE_VERSION", "v1")
    monkeypatch.delenv("GENESIS_FORCE_SHELL", raising=False)

    trial = runner.TrialConfig(
        snapshot_id="tTEST_1h_20240101_20240201_v1",
        symbol="tTEST",
        timeframe="1h",
        warmup_bars=1,
        parameters={"thresholds": {"entry_conf_overall": 0.35}},
        start_date="2024-01-01",
        end_date="2024-01-02",
    )

    def fake_run_backtest_direct(*_args: Any, **_kwargs: Any) -> tuple[int, str, dict[str, Any]]:
        return (
            0,
            "",
            {
                "summary": {"initial_capital": 10000.0},
                "trades": [],
                "equity_curve": [],
                "metrics": {"num_trades": 0, "profit_factor": float("inf")},
                "merged_config": {},
                "runtime_version": 1,
            },
        )

    with (
        patch("core.optimizer.runner._get_default_config", return_value={}),
        patch("core.optimizer.runner._get_default_runtime_version", return_value=1),
        patch("core.optimizer.runner._run_backtest_direct", side_effect=fake_run_backtest_direct),
    ):
        payload = runner.run_trial(
            trial,
            run_id="run_test",
            index=1,
            run_dir=tmp_path,
            allow_resume=False,
            existing_trials={},
        )

    assert payload.get("abort_reason") == "zero_trades_high_thresholds"
    assert payload.get("score", {}).get("score_version") == "v1"

    trial_json_path = tmp_path / "trial_001.json"
    raw = trial_json_path.read_text(encoding="utf-8")
    assert "Infinity" not in raw

    parsed = runner._json_loads(raw)
    score_block = parsed.get("score")
    assert isinstance(score_block, dict)
    assert score_block.get("score_version") == "v1"

    metrics = score_block.get("metrics")
    assert isinstance(metrics, dict)
    assert metrics.get("profit_factor") is None


def test_ensure_run_metadata_mismatch_is_fail_fast(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GENESIS_SCORE_VERSION", "v1")
    monkeypatch.delenv("GENESIS_ALLOW_RUN_META_MISMATCH", raising=False)

    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "cfg.yaml"
    config_path.write_text("meta: {}\n", encoding="utf-8")

    meta = {
        "snapshot_id": "snap_A",
        "symbol": "tTEST",
        "timeframe": "1h",
    }
    run_id = "run_test"

    # Match everything except snapshot_id (guard should fail-fast).
    (run_dir / "run_meta.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "config_path": str(config_path),
                "snapshot_id": "snap_B",
                "symbol": "tTEST",
                "timeframe": "1h",
                "score_version": "v1",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"run_meta\.json mismatch"):
        runner._ensure_run_metadata(run_dir, config_path, meta, run_id)


def test_ensure_run_metadata_backfills_missing_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GENESIS_SCORE_VERSION", "v2")
    monkeypatch.delenv("GENESIS_ALLOW_RUN_META_MISMATCH", raising=False)

    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "cfg.yaml"
    config_path.write_text("meta: {}\n", encoding="utf-8")

    meta = {
        "snapshot_id": "snap_A",
        "symbol": "tTEST",
        "timeframe": "1h",
    }
    run_id = "run_test"

    # Older/partial run_meta.json missing key fields should be backfilled.
    (run_dir / "run_meta.json").write_text(
        json.dumps({"run_id": run_id, "snapshot_id": "snap_A"}),
        encoding="utf-8",
    )

    runner._ensure_run_metadata(run_dir, config_path, meta, run_id)

    updated = json.loads((run_dir / "run_meta.json").read_text(encoding="utf-8"))
    assert updated.get("run_id") == run_id
    assert updated.get("config_path") == str(config_path)
    assert updated.get("symbol") == "tTEST"
    assert updated.get("timeframe") == "1h"
    assert updated.get("score_version") == "v2"
    assert updated.get("raw_meta") == meta
    assert updated.get("updated_at")


def test_verify_or_set_optuna_study_score_version(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyStudy:
        def __init__(self, existing: str | None = None) -> None:
            self.user_attrs: dict[str, Any] = {}
            if existing is not None:
                self.user_attrs["genesis_score_version"] = existing

        def set_user_attr(self, k: str, v: Any) -> None:
            self.user_attrs[k] = v

    monkeypatch.delenv("GENESIS_ALLOW_STUDY_RESUME_MISMATCH", raising=False)

    s = _DummyStudy()
    runner._verify_or_set_optuna_study_score_version(s, "v2")
    assert s.user_attrs.get("genesis_score_version") == "v2"

    s2 = _DummyStudy(existing="v1")
    with pytest.raises(RuntimeError, match=r"score_version mismatch"):
        runner._verify_or_set_optuna_study_score_version(s2, "v2")

    monkeypatch.setenv("GENESIS_ALLOW_STUDY_RESUME_MISMATCH", "1")
    s3 = _DummyStudy(existing="v1")
    runner._verify_or_set_optuna_study_score_version(s3, "v2")
    # Allow-mismatch should tolerate mismatch without overwriting existing.
    assert s3.user_attrs.get("genesis_score_version") == "v1"


@pytest.mark.skipif(not runner.OPTUNA_AVAILABLE, reason="Optuna ej installerat")
def test_run_optimizer_optuna_strategy(tmp_path: Path) -> None:
    config = {
        "meta": {
            "symbol": "tTEST",
            "timeframe": "1h",
            "snapshot_id": "tTEST_1h_20240101_20240201_v1",
            "runs": {
                "strategy": "optuna",
                "max_trials": 2,
                "max_concurrent": 1,
                "resume": False,
                "optuna": {"storage": None, "study_name": "test-study"},
            },
        },
        "parameters": {
            "thresholds": {
                "entry_conf_overall": {
                    "type": "grid",
                    "values": [0.4, 0.5],
                }
            }
        },
    }
    config_path = tmp_path / "optuna.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    run_meta_payload = {
        "git_commit": "abc123",
        "snapshot_id": "tTEST_1h_20240101_20240201_v1",
    }

    def fake_make_trial(idx: int, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "trial_id": f"trial_{idx:03d}",
            "parameters": params,
            "results_path": "dummy.json",
            "score": {"score": 1.0, "metrics": {}, "hard_failures": []},
            "constraints": {"ok": True, "reasons": []},
        }

    with (
        patch("core.optimizer.runner.RESULTS_DIR", tmp_path / "results"),
        patch("core.optimizer.runner._ensure_run_metadata") as ensure_meta,
        patch("core.optimizer.runner._create_optuna_study") as create_study,
        patch("core.optimizer.runner.run_trial") as mock_run_trial,
    ):
        mock_run_trial.return_value = fake_make_trial(
            1, {"thresholds": {"entry_conf_overall": 0.4}}
        )
        ensure_meta.side_effect = lambda run_dir, *_: (
            run_dir.mkdir(parents=True, exist_ok=True),
            (run_dir / "run_meta.json").write_text(json.dumps(run_meta_payload), encoding="utf-8"),
        )

        study_mock = MagicMock()
        trial_mock = MagicMock()
        trial_mock.number = 0
        trial_mock.suggest_categorical.return_value = 0.4  # Return a real value
        trial_mock.user_attrs = {}

        study_mock.best_trial = trial_mock
        study_mock.study_name = "test-study"
        study_mock.trials = [trial_mock]
        study_mock.best_value = 1.0

        def optuna_objective_side_effect(objective, **kwargs):
            # Simulate Optuna calling the objective with the mocked trial
            score = objective(trial_mock)
            # Manually update trial state as Optuna would
            trial_mock.user_attrs["result_payload"] = mock_run_trial.return_value
            trial_mock.state = optuna.trial.TrialState.COMPLETE
            trial_mock.value = score
            return score

        study_mock.optimize.side_effect = optuna_objective_side_effect
        create_study.return_value = study_mock

        results = runner.run_optimizer(config_path, run_id="run_optuna")

    assert len(results) == 1
    assert results[0]["constraints"]["ok"] is True
    create_study.assert_called_once()


@pytest.mark.skipif(not runner.OPTUNA_AVAILABLE, reason="Optuna ej installerat")
def test_run_optimizer_validation_fallback_reads_from_optuna_storage(tmp_path: Path) -> None:
    config = {
        "meta": {
            "symbol": "tTEST",
            "timeframe": "1h",
            "snapshot_id": "tTEST_1h_20240101_20240201_v1",
            "runs": {
                "strategy": "optuna",
                "max_trials": 0,
                "max_concurrent": 1,
                "resume": True,
                "optuna": {"storage": "sqlite:///dummy.db", "study_name": "test-study"},
                "validation": {"enabled": True, "top_n": 2, "use_sample_range": False},
            },
        },
        "parameters": {
            "thresholds": {
                "entry_conf_overall": {
                    "type": "grid",
                    "values": [0.4, 0.5],
                }
            }
        },
    }
    config_path = tmp_path / "optuna_validate_only.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    results_root = tmp_path / "results" / "hparam_search"
    run_meta_payload = {
        "git_commit": "abc123",
        "snapshot_id": "tTEST_1h_20240101_20240201_v1",
        "optuna": {
            "study_name": "test-study",
            "storage": "sqlite:///dummy.db",
            "direction": "maximize",
            "n_trials": 0,
            "best_value": None,
            "best_trial_number": None,
        },
    }

    created_run_dir: Path | None = None

    def fake_ensure(run_dir: Path, *_args: Any, **_kwargs: Any) -> None:
        nonlocal created_run_dir
        created_run_dir = run_dir
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run_meta.json").write_text(json.dumps(run_meta_payload), encoding="utf-8")

    # Two explore payloads living in Optuna storage
    from types import SimpleNamespace

    from optuna.trial import TrialState

    trial_a = SimpleNamespace(
        state=TrialState.COMPLETE,
        user_attrs={
            "result_payload": {
                "trial_id": "trial_a",
                "parameters": {"thresholds": {"entry_conf_overall": 0.4}},
                "score": {"score": 10.0, "metrics": {}, "hard_failures": []},
                "constraints": {"ok": True, "reasons": []},
            }
        },
    )
    trial_b = SimpleNamespace(
        state=TrialState.COMPLETE,
        user_attrs={
            "result_payload": {
                "trial_id": "trial_b",
                "parameters": {"thresholds": {"entry_conf_overall": 0.5}},
                "score": {"score": 7.0, "metrics": {}, "hard_failures": []},
                "constraints": {"ok": True, "reasons": []},
            }
        },
    )
    study_mock = SimpleNamespace(trials=[trial_a, trial_b])

    def fake_run_trial(*args: Any, **kwargs: Any) -> dict[str, Any]:
        trial_cfg = args[0]
        params = getattr(trial_cfg, "parameters", {}) or {}
        entry_conf = params.get("thresholds", {}).get("entry_conf_overall")
        # Return different validation scores just to ensure we ran it.
        return {
            "trial_id": f"val_{entry_conf}",
            "parameters": params,
            "score": {
                "score": 100.0 if entry_conf == 0.4 else 200.0,
                "metrics": {},
                "hard_failures": [],
            },
            "constraints": {"ok": True, "reasons": []},
            "results_path": "val.json",
        }

    with (
        patch("core.optimizer.runner.RESULTS_DIR", results_root),
        patch("core.optimizer.runner._ensure_run_metadata", side_effect=fake_ensure),
        patch("core.optimizer.runner._run_optuna", return_value=[]),
        patch("optuna.load_study", return_value=study_mock) as load_study,
        patch("core.optimizer.runner.run_trial", side_effect=fake_run_trial),
    ):
        selected = runner._select_top_n_from_optuna_storage(run_meta_payload, top_n=2)
        assert len(selected) == 2
        results = run_optimizer(config_path, run_id="run_validate_only")

    # Fallback-vägen ska ha läst kandidater från Optuna storage.
    assert load_study.call_count >= 1

    assert created_run_dir is not None
    assert created_run_dir.exists()
    assert (created_run_dir / "validation").exists()
    meta = json.loads((created_run_dir / "run_meta.json").read_text(encoding="utf-8"))
    assert meta.get("validation", {}).get("validated") == 2
    assert len(results) == 2
