from __future__ import annotations

from pathlib import Path

import core.optimizer.runner as runner


def _install_counting_loader(monkeypatch) -> dict[str, int]:
    calls = {"n": 0}

    def _fake_load_json_with_retries(_path: Path, retries: int = 3, delay: float = 0.1):
        calls["n"] += 1
        return {"ok": True}

    monkeypatch.setattr(runner, "_load_json_with_retries", _fake_load_json_with_retries)
    return calls


def test_optimizer_json_cache_disabled_by_default(monkeypatch, tmp_path: Path) -> None:
    runner._JSON_CACHE.clear()
    calls = _install_counting_loader(monkeypatch)

    monkeypatch.delenv("GENESIS_OPTIMIZER_JSON_CACHE", raising=False)

    p = tmp_path / "payload.json"
    p.write_text("{\"x\": 1}", encoding="utf-8")

    runner._read_json_cached(p)
    runner._read_json_cached(p)

    assert calls["n"] == 2


def test_optimizer_json_cache_enabled_is_case_insensitive(monkeypatch, tmp_path: Path) -> None:
    runner._JSON_CACHE.clear()
    calls = _install_counting_loader(monkeypatch)

    monkeypatch.setenv("GENESIS_OPTIMIZER_JSON_CACHE", "TRUE")

    p = tmp_path / "payload.json"
    p.write_text("{\"x\": 1}", encoding="utf-8")

    runner._read_json_cached(p)
    runner._read_json_cached(p)

    assert calls["n"] == 1


def test_optimizer_json_cache_disabled_for_empty_or_zero(monkeypatch, tmp_path: Path) -> None:
    p = tmp_path / "payload.json"
    p.write_text("{\"x\": 1}", encoding="utf-8")

    runner._JSON_CACHE.clear()
    calls = _install_counting_loader(monkeypatch)

    monkeypatch.setenv("GENESIS_OPTIMIZER_JSON_CACHE", "")
    runner._read_json_cached(p)
    runner._read_json_cached(p)
    assert calls["n"] == 2

    runner._JSON_CACHE.clear()
    calls = _install_counting_loader(monkeypatch)

    monkeypatch.setenv("GENESIS_OPTIMIZER_JSON_CACHE", "0")
    runner._read_json_cached(p)
    runner._read_json_cached(p)
    assert calls["n"] == 2
