from __future__ import annotations

import importlib
from pathlib import Path

import core.config.authority as authority_mod


def test_runtime_path_does_not_depend_on_cwd(tmp_path: Path, monkeypatch) -> None:
    other_cwd = tmp_path / "other"
    other_cwd.mkdir()

    monkeypatch.chdir(tmp_path)
    importlib.reload(authority_mod)
    p1 = authority_mod.RUNTIME_PATH
    a1 = authority_mod.AUDIT_LOG
    s1 = authority_mod.SEED_PATH

    monkeypatch.chdir(other_cwd)
    importlib.reload(authority_mod)
    p2 = authority_mod.RUNTIME_PATH
    a2 = authority_mod.AUDIT_LOG
    s2 = authority_mod.SEED_PATH

    assert p1 == p2
    assert a1 == a2
    assert s1 == s2

    expected_repo_root = Path(authority_mod.__file__).resolve().parents[3]
    assert p1 == expected_repo_root / "config" / "runtime.json"
    assert a1 == expected_repo_root / "logs" / "config_audit.jsonl"
    assert s1 == expected_repo_root / "config" / "runtime.seed.json"


def test_default_config_authority_uses_runtime_path() -> None:
    auth = authority_mod.ConfigAuthority()
    assert auth.path == authority_mod.RUNTIME_PATH
