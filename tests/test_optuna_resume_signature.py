from __future__ import annotations

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
