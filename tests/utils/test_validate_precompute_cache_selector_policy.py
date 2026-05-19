from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import pytest

import scripts.validate.validate_precompute_cache_selector_policy as selector_policy


def _git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _engine_source(
    *,
    schema_version: str = "3",
    material_suffix: str = "v3",
    helper_note: str = "keep",
    prepare_call: str = "prepare_precomputed_features()",
) -> str:
    return (
        textwrap.dedent(
            f"""
            PRECOMPUTE_SCHEMA_VERSION = {schema_version}


            def _precompute_cache_key_material():
                digest = \"{material_suffix}\"
                return digest


            def _build_precompute_cache_metadata():
                return {{}}


            def _validate_metadata_bearing_precompute_cache():
                return True, None


            def helper_not_target():
                note = \"{helper_note}\"
                return note


            class BacktestEngine:
                def load_data(self):
                    {prepare_call}
                    helper_not_target()

                def _precompute_cache_key(self, df):
                    return \"key\"
            """
        ).strip()
        + "\n"
    )


def _bootstrap_repo(tmp_path: Path) -> tuple[Path, Path, str]:
    repo = tmp_path
    _git(repo, "init")
    _git(repo, "checkout", "-b", "master")
    _git(repo, "config", "user.email", "ci@example.test")
    _git(repo, "config", "user.name", "CI")

    (repo / "pyproject.toml").write_text(
        '[project]\nname = "selector-policy-test"\nversion = "0.0.0"\n',
        encoding="utf-8",
    )
    engine_path = repo / "src" / "core" / "backtest" / "engine.py"
    engine_path.parent.mkdir(parents=True, exist_ok=True)
    engine_path.write_text(_engine_source(), encoding="utf-8")

    _git(repo, "add", "pyproject.toml", "src/core/backtest/engine.py")
    _git(repo, "commit", "-m", "base")
    base_sha = _git(repo, "rev-parse", "HEAD")
    return repo, engine_path, base_sha


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git is required for selector-policy validation tests",
)
def test_validate_selector_policy_noops_when_engine_surface_is_untouched(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, _engine_path, _base_sha = _bootstrap_repo(tmp_path)
    calls: list[tuple[str, ...]] = []

    monkeypatch.setattr(selector_policy, "_repo_root", lambda: repo)

    exit_code = selector_policy.validate_selector_policy(
        run_pytest_fn=lambda selectors: calls.append(selectors) or 0,
    )

    assert exit_code == 0
    assert calls == []


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git is required for selector-policy validation tests",
)
def test_validate_selector_policy_noops_for_non_target_engine_edit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, engine_path, _base_sha = _bootstrap_repo(tmp_path)
    engine_path.write_text(_engine_source(helper_note="changed"), encoding="utf-8")
    calls: list[tuple[str, ...]] = []

    monkeypatch.setattr(selector_policy, "_repo_root", lambda: repo)

    exit_code = selector_policy.validate_selector_policy(
        run_pytest_fn=lambda selectors: calls.append(selectors) or 0,
    )

    assert exit_code == 0
    assert calls == []


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git is required for selector-policy validation tests",
)
def test_validate_selector_policy_runs_selectors_when_schema_version_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, engine_path, _base_sha = _bootstrap_repo(tmp_path)
    engine_path.write_text(_engine_source(schema_version="4"), encoding="utf-8")
    calls: list[tuple[str, ...]] = []

    monkeypatch.setattr(selector_policy, "_repo_root", lambda: repo)

    exit_code = selector_policy.validate_selector_policy(
        run_pytest_fn=lambda selectors: calls.append(selectors) or 0,
    )

    assert exit_code == 0
    assert calls == [selector_policy.TARGET_SELECTORS]


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git is required for selector-policy validation tests",
)
def test_validate_selector_policy_runs_selectors_for_prepare_precompute_callsite_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, engine_path, _base_sha = _bootstrap_repo(tmp_path)
    engine_path.write_text(
        _engine_source(prepare_call="prepare_precomputed_features(cache_path=None)"),
        encoding="utf-8",
    )
    calls: list[tuple[str, ...]] = []

    monkeypatch.setattr(selector_policy, "_repo_root", lambda: repo)

    exit_code = selector_policy.validate_selector_policy(
        run_pytest_fn=lambda selectors: calls.append(selectors) or 0,
    )

    assert exit_code == 0
    assert calls == [selector_policy.TARGET_SELECTORS]


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git is required for selector-policy validation tests",
)
def test_validate_selector_policy_propagates_failure_for_ci_diff_base(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, engine_path, base_sha = _bootstrap_repo(tmp_path)
    engine_path.write_text(_engine_source(material_suffix="v4"), encoding="utf-8")
    _git(repo, "add", "src/core/backtest/engine.py")
    _git(repo, "commit", "-m", "touch target function")
    calls: list[tuple[str, ...]] = []

    monkeypatch.setattr(selector_policy, "_repo_root", lambda: repo)

    exit_code = selector_policy.validate_selector_policy(
        base_ref=base_sha,
        run_pytest_fn=lambda selectors: calls.append(selectors) or 7,
    )

    assert exit_code == 7
    assert calls == [selector_policy.TARGET_SELECTORS]
