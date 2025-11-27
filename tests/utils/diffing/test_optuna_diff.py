from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.optimizer.runner import TrialConfig, run_trial
from core.utils.diffing.canonical import canonicalize_config, fingerprint_config
from core.utils.diffing.optuna_guard import estimate_zero_trade
from core.utils.diffing.trial_cache import TrialResultCache


def test_canonicalize_config_stable():
    params_a = {
        "risk": {"risk_map": [[0.6, 0.010000001], [0.7, 0.02]]},
        "thresholds": {"entry_conf_overall": 0.45},
    }
    params_b = {
        "thresholds": {"entry_conf_overall": 0.4500000001},
        "risk": {"risk_map": [[0.6, 0.01], [0.7, 0.02]]},
    }

    canon_a = canonicalize_config(params_a, precision=6)
    canon_b = canonicalize_config(params_b, precision=6)

    assert canon_a == canon_b
    assert fingerprint_config(params_a) == fingerprint_config(params_b)


def test_trial_result_cache_roundtrip(tmp_path: Path):
    cache = TrialResultCache(tmp_path)
    payload = {"score": {"score": 1.23}}
    cache.store("abc123", payload)
    loaded = cache.lookup("abc123")
    assert loaded == payload


def test_estimate_zero_trade_flags_high_threshold():
    result = estimate_zero_trade(
        {
            "thresholds": {"entry_conf_overall": 0.99},
            "risk": {"risk_map": [[0.6, 0.01]]},
        }
    )
    assert not result.ok
    assert "0.99" in (result.reason or "")


def test_estimate_zero_trade_allows_champion():
    champion_path = (
        Path(__file__).resolve().parents[4]
        / "config"
        / "strategy"
        / "champions"
        / "tBTCUSD_1h.json"
    )
    if not champion_path.exists():
        pytest.skip("Champion config missing")
    champion_payload = json.loads(champion_path.read_text(encoding="utf-8"))
    champion_params = champion_payload.get("cfg", {}).get("parameters", {})
    assert champion_params, "Champion parameters missing"
    result = estimate_zero_trade(champion_params)
    assert result.ok


def test_run_trial_uses_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    results_root = Path(__file__).resolve().parents[3] / "results" / "backtests"
    results_root.mkdir(parents=True, exist_ok=True)

    created_files: list[Path] = []
    call_count = {"runs": 0}

    # Force runner to use the subprocess path so our fake _exec_backtest is invoked
    monkeypatch.setenv("GENESIS_FORCE_SHELL", "1")

    def fake_exec_backtest(cmd, cwd, env, log_path):
        call_count["runs"] += 1
        symbol = cmd[cmd.index("--symbol") + 1]
        timeframe = cmd[cmd.index("--timeframe") + 1]
        result_path = results_root / f"{symbol}_{timeframe}_diffcache_{call_count['runs']}.json"
        payload = {
            "metrics": {
                "initial_capital": 10000,
                "total_return": 1.0,
                "num_trades": 5,
                "profit_factor": 1.2,
                "max_drawdown": 0.1,
                "sharpe_ratio": 0.5,
                "win_rate": 0.5,
            },
            "summary": {
                "initial_capital": 10000,
                "total_return": 1.0,
                "num_trades": 5,
                "profit_factor": 1.2,
            },
            "trades": [{"pnl": 50.0}],
            "equity_curve": [{"total_equity": 10000}, {"total_equity": 10050}],
        }
        result_path.write_text(json.dumps(payload), encoding="utf-8")
        created_files.append(result_path)
        log_path.write_text(f"  results: {result_path}\n", encoding="utf-8")
        return 0, "ok"

    # Import runner module to patch it correctly
    from core.optimizer import runner as runner_module

    monkeypatch.setattr(runner_module, "_exec_backtest", fake_exec_backtest)

    trial = TrialConfig(
        snapshot_id="tBTCUSD_1h_20240101_20240201_v1",
        symbol="tBTCUSD",
        timeframe="1h",
        warmup_bars=10,
        parameters={
            "thresholds": {"entry_conf_overall": 0.45},
            "risk": {"risk_map": [[0.6, 0.01], [0.7, 0.02]]},
        },
        start_date="2024-01-01",
        end_date="2024-02-01",
    )

    run_dir = tmp_path / "run"
    first = run_trial(
        trial,
        run_id="diff",
        index=1,
        run_dir=run_dir,
        allow_resume=False,
        existing_trials={},
        max_attempts=1,
        constraints_cfg=None,
        cache_enabled=True,
    )

    assert call_count["runs"] == 1
    assert not first.get("skipped")
    assert first.get("score", {}).get("score") is not None

    second = run_trial(
        trial,
        run_id="diff",
        index=2,
        run_dir=run_dir,
        allow_resume=False,
        existing_trials={},
        max_attempts=1,
        constraints_cfg=None,
        cache_enabled=True,
    )

    assert call_count["runs"] == 1, "Second run should hit cache"
    assert second.get("from_cache") is True

    for path in created_files:
        path.unlink(missing_ok=True)


def test_run_trial_zero_trade_skip(tmp_path: Path):
    trial = TrialConfig(
        snapshot_id="tBTCUSD_1h_20240101_20240201_v1",
        symbol="tBTCUSD",
        timeframe="1h",
        warmup_bars=10,
        parameters={
            "thresholds": {"entry_conf_overall": 0.99},
            "risk": {"risk_map": [[0.6, 0.0]]},
        },
        start_date="2024-01-01",
        end_date="2024-02-01",
    )

    run_dir = tmp_path / "run"
    result = run_trial(
        trial,
        run_id="diff",
        index=1,
        run_dir=run_dir,
        allow_resume=False,
        existing_trials={},
        max_attempts=1,
        constraints_cfg=None,
        cache_enabled=True,
    )

    assert result.get("skipped") is True
    assert result.get("reason") == "zero_trade_preflight"
    assert result.get("score", {}).get("score") == -1e5
