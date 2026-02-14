from __future__ import annotations

from typing import Any

import core.optimizer.runner as runner


def test_create_optuna_study_injects_sqlite_timeout_engine_kwargs(monkeypatch) -> None:
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
            calls["url"] = url
            calls["engine_kwargs"] = engine_kwargs
            calls["heartbeat_interval"] = heartbeat_interval
            calls["grace_period"] = grace_period

    monkeypatch.setattr(runner, "RDBStorage", FakeRDBStorage)

    def fake_create_study(**kwargs):
        calls["create_study_storage"] = kwargs.get("storage")
        return object()

    monkeypatch.setattr(runner.optuna, "create_study", fake_create_study)

    runner._create_optuna_study(
        run_id="run_x",
        storage="sqlite:///test.db",
        study_name="study_x",
        sampler_cfg={"name": "random", "kwargs": {"seed": 42}},
        pruner_cfg={"name": "none", "kwargs": {}},
        direction="maximize",
        allow_resume=False,
        concurrency=1,
        heartbeat_interval=60,
        heartbeat_grace_period=120,
    )

    assert calls["url"].startswith("sqlite")
    assert calls["engine_kwargs"] == {"connect_args": {"timeout": 10}}
    assert calls["heartbeat_interval"] == 60
    assert calls["grace_period"] == 120
    assert isinstance(calls["create_study_storage"], FakeRDBStorage)


def test_create_optuna_study_injects_sqlite_timeout_without_heartbeat(monkeypatch) -> None:
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
            calls["url"] = url
            calls["engine_kwargs"] = engine_kwargs
            calls["heartbeat_interval"] = heartbeat_interval
            calls["grace_period"] = grace_period

    monkeypatch.setattr(runner, "RDBStorage", FakeRDBStorage)

    def fake_create_study(**kwargs):
        calls["create_study_storage"] = kwargs.get("storage")
        return object()

    monkeypatch.setattr(runner.optuna, "create_study", fake_create_study)

    runner._create_optuna_study(
        run_id="run_x",
        storage="sqlite:///test.db",
        study_name="study_x",
        sampler_cfg={"name": "random", "kwargs": {"seed": 42}},
        pruner_cfg={"name": "none", "kwargs": {}},
        direction="maximize",
        allow_resume=False,
        concurrency=1,
        heartbeat_interval=None,
        heartbeat_grace_period=None,
    )

    assert calls["url"].startswith("sqlite")
    assert calls["engine_kwargs"] == {"connect_args": {"timeout": 10}}
    assert calls["heartbeat_interval"] is None
    assert calls["grace_period"] is None
    assert isinstance(calls["create_study_storage"], FakeRDBStorage)


def test_create_optuna_study_does_not_inject_timeout_for_non_sqlite(monkeypatch) -> None:
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
            calls["url"] = url
            calls["engine_kwargs"] = engine_kwargs

    monkeypatch.setattr(runner, "RDBStorage", FakeRDBStorage)

    def fake_create_study(**kwargs):
        return object()

    monkeypatch.setattr(runner.optuna, "create_study", fake_create_study)

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
