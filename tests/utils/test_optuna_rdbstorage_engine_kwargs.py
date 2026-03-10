from __future__ import annotations

from typing import Any

import pytest

import core.optimizer.runner as runner


def _patch_study_capture(monkeypatch):
    calls: dict[str, Any] = {}

    class FakeRDBStorage:
        def __init__(
            self,
            url: str,
            engine_kwargs: dict[str, Any] | None = None,
            skip_compatibility_check: bool = False,
            *,
            heartbeat_interval: int | None = None,
            grace_period: int | None = None,
            failed_trial_callback=None,
            skip_table_creation: bool = False,
        ) -> None:
            _ = (skip_compatibility_check, failed_trial_callback, skip_table_creation)
            calls["url"] = url
            calls["engine_kwargs"] = engine_kwargs
            calls["heartbeat_interval"] = heartbeat_interval
            calls["grace_period"] = grace_period

    monkeypatch.setattr(runner, "RDBStorage", FakeRDBStorage)

    def fake_create_study(**kwargs):
        calls["create_study_storage"] = kwargs.get("storage")
        return object()

    monkeypatch.setattr(runner.optuna, "create_study", fake_create_study)

    return calls, FakeRDBStorage


@pytest.mark.parametrize(
    ("heartbeat_interval", "heartbeat_grace_period"),
    [
        pytest.param(60, 120, id="with-heartbeat"),
        pytest.param(None, None, id="without-heartbeat"),
    ],
)
def test_create_optuna_study_injects_sqlite_timeout_engine_kwargs(
    monkeypatch, heartbeat_interval, heartbeat_grace_period
) -> None:
    calls, fake_storage_cls = _patch_study_capture(monkeypatch)

    runner._create_optuna_study(
        run_id="run_x",
        storage="sqlite:///test.db",
        study_name="study_x",
        sampler_cfg={"name": "random", "kwargs": {"seed": 42}},
        pruner_cfg={"name": "none", "kwargs": {}},
        direction="maximize",
        allow_resume=False,
        concurrency=1,
        heartbeat_interval=heartbeat_interval,
        heartbeat_grace_period=heartbeat_grace_period,
    )

    assert calls["url"].startswith("sqlite")
    assert calls["engine_kwargs"] == {"connect_args": {"timeout": 10}}
    assert calls["heartbeat_interval"] == heartbeat_interval
    assert calls["grace_period"] == heartbeat_grace_period
    assert isinstance(calls["create_study_storage"], fake_storage_cls)


def test_create_optuna_study_does_not_inject_timeout_for_non_sqlite(monkeypatch) -> None:
    calls, _ = _patch_study_capture(monkeypatch)

    runner._create_optuna_study(
        run_id="run_x",
        storage="postgresql://user@localhost:5432/db",
        study_name="study_x",
        sampler_cfg={"name": "random", "kwargs": {"seed": 42}},
        pruner_cfg={"name": "none", "kwargs": {}},
        direction="maximize",
        allow_resume=False,
        concurrency=1,
        heartbeat_interval=60,
        heartbeat_grace_period=120,
    )

    assert calls["url"].startswith("postgresql")
    assert calls["engine_kwargs"] is None


def test_create_optuna_study_rejects_non_positive_heartbeat_interval() -> None:
    try:
        runner._create_optuna_study(
            run_id="run_x",
            storage="sqlite:///test.db",
            study_name="study_x",
            sampler_cfg={"name": "random", "kwargs": {"seed": 42}},
            pruner_cfg={"name": "none", "kwargs": {}},
            direction="maximize",
            allow_resume=False,
            concurrency=1,
            heartbeat_interval=0,
            heartbeat_grace_period=120,
        )
    except ValueError as exc:
        assert "heartbeat_interval" in str(exc)
    else:
        raise AssertionError("Expected ValueError for heartbeat_interval=0")
