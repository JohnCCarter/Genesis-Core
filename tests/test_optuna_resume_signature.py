from __future__ import annotations

from pathlib import Path

import pytest


def _dummy_objective(trial):  # pragma: no cover
    # Keep it deterministic and fast.
    _ = trial.suggest_float("x", 0.0, 1.0)
    return 0.0


def test_resume_signature_mismatch_raises_when_existing_signature_present(monkeypatch):
    optuna = pytest.importorskip("optuna")

    from core.optimizer.runner import _verify_or_set_optuna_study_signature

    study = optuna.create_study(direction="maximize")
    study.optimize(_dummy_objective, n_trials=1, show_progress_bar=False)

    # Simulate a study that already has a stored signature.
    study.set_user_attr(
        "genesis_resume_signature",
        {"version": 1, "fingerprint": "abc", "git_commit": "x", "runtime_version": 1},
    )

    with pytest.raises(RuntimeError, match=r"signature mismatch"):
        _verify_or_set_optuna_study_signature(
            study,
            {"version": 1, "fingerprint": "def", "git_commit": "x", "runtime_version": 1},
        )


def test_resume_signature_mismatch_can_be_overridden(monkeypatch):
    optuna = pytest.importorskip("optuna")

    from core.optimizer.runner import _verify_or_set_optuna_study_signature

    monkeypatch.setenv("GENESIS_ALLOW_STUDY_RESUME_MISMATCH", "1")

    study = optuna.create_study(direction="maximize")
    study.optimize(_dummy_objective, n_trials=1, show_progress_bar=False)
    study.set_user_attr(
        "genesis_resume_signature",
        {"version": 1, "fingerprint": "abc", "git_commit": "x", "runtime_version": 1},
    )

    # Should not raise due to override.
    _verify_or_set_optuna_study_signature(
        study,
        {"version": 1, "fingerprint": "def", "git_commit": "x", "runtime_version": 1},
    )


def test_missing_signature_on_existing_study_does_not_backfill_by_default(capfd):
    optuna = pytest.importorskip("optuna")

    from core.optimizer.runner import _verify_or_set_optuna_study_signature

    study = optuna.create_study(direction="maximize")
    study.optimize(_dummy_objective, n_trials=1, show_progress_bar=False)

    _verify_or_set_optuna_study_signature(
        study,
        {"version": 1, "fingerprint": "abc", "git_commit": "x", "runtime_version": 1},
    )

    captured = capfd.readouterr().out
    assert "cannot verify resume safety" in captured

    # Ensure we did not silently attach a signature.
    assert "genesis_resume_signature" not in study.user_attrs


def test_missing_signature_can_be_backfilled(monkeypatch):
    optuna = pytest.importorskip("optuna")

    from core.optimizer.runner import _verify_or_set_optuna_study_signature

    monkeypatch.setenv("GENESIS_BACKFILL_STUDY_SIGNATURE", "1")

    study = optuna.create_study(direction="maximize")
    study.optimize(_dummy_objective, n_trials=1, show_progress_bar=False)

    _verify_or_set_optuna_study_signature(
        study,
        {"version": 1, "fingerprint": "abc", "git_commit": "x", "runtime_version": 1},
    )

    assert study.user_attrs.get("genesis_resume_signature", {}).get("fingerprint") == "abc"


def test_compute_resume_signature_hashes_repo_relative_path(monkeypatch, tmp_path):
    """Fingerprint should be stable across machines if the repo-relative config path is the same."""

    from core.optimizer import runner

    config = {
        "meta": {
            "symbol": "tBTCUSD",
            "timeframe": "1h",
            "snapshot_id": "snap",
            "warmup_bars": 150,
            "runs": {
                "use_sample_range": True,
                "sample_start": "2024-01-01",
                "sample_end": "2024-12-31",
                "optuna": {"timeout_seconds": 123, "end_at": "2026-01-01"},
            },
        },
        "constraints": {},
        "parameters": {},
    }

    # Simulate two different machine checkouts with the same relative config path.
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"

    cfg_rel = Path("config/optimizer/test.yaml")
    cfg_a = repo_a / cfg_rel
    cfg_b = repo_b / cfg_rel

    cfg_a.parent.mkdir(parents=True, exist_ok=True)
    cfg_b.parent.mkdir(parents=True, exist_ok=True)
    cfg_a.write_text("# test", encoding="utf-8")
    cfg_b.write_text("# test", encoding="utf-8")

    monkeypatch.setattr(runner, "PROJECT_ROOT", repo_a)
    sig_a = runner._compute_optuna_resume_signature(
        config=config, config_path=cfg_a, git_commit="abc", runtime_version=123
    )

    monkeypatch.setattr(runner, "PROJECT_ROOT", repo_b)
    sig_b = runner._compute_optuna_resume_signature(
        config=config, config_path=cfg_b, git_commit="abc", runtime_version=123
    )

    assert sig_a["config_path_rel_posix"] == "config/optimizer/test.yaml"
    assert sig_b["config_path_rel_posix"] == "config/optimizer/test.yaml"
    assert sig_a["fingerprint"] == sig_b["fingerprint"]
    assert sig_a["config_path_abs"] != sig_b["config_path_abs"]


def test_compute_resume_signature_external_config_is_strict(monkeypatch, tmp_path):
    """If config_path is outside the repo, the abs path should be part of the fingerprint."""

    from core.optimizer import runner

    config = {
        "meta": {
            "symbol": "tBTCUSD",
            "timeframe": "1h",
            "snapshot_id": "snap",
            "warmup_bars": 150,
            "runs": {
                "use_sample_range": True,
                "sample_start": "2024-01-01",
                "sample_end": "2024-12-31",
                "optuna": {},
            },
        },
        "constraints": {},
        "parameters": {},
    }

    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(runner, "PROJECT_ROOT", repo_root)

    external_a = tmp_path / "external_a.yaml"
    external_b = tmp_path / "external_b.yaml"
    external_a.write_text("# ext a", encoding="utf-8")
    external_b.write_text("# ext b", encoding="utf-8")

    sig_a = runner._compute_optuna_resume_signature(
        config=config, config_path=external_a, git_commit="abc", runtime_version=123
    )
    sig_b = runner._compute_optuna_resume_signature(
        config=config, config_path=external_b, git_commit="abc", runtime_version=123
    )

    assert sig_a["config_path_external"] is True
    assert sig_b["config_path_external"] is True
    assert sig_a["fingerprint"] != sig_b["fingerprint"]
