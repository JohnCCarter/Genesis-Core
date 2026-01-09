from __future__ import annotations

from pathlib import Path

from core.governance.registry import validate_registry


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _copy_schemas(repo_root: Path, dst_root: Path) -> None:
    dst = dst_root / "registry" / "schemas"
    dst.mkdir(parents=True, exist_ok=True)

    for name in [
        "skill.schema.json",
        "compact.schema.json",
        "manifest.schema.json",
        "audit_entry.schema.json",
    ]:
        (dst / name).write_text(
            (repo_root / "registry" / "schemas" / name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )


def _write_minimal_manifests(dst_root: Path, *, stable_skill_ref: bool) -> None:
    manifests = dst_root / "registry" / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)
    (manifests / "dev.json").write_text(
        '{"registry_version":1,"skills":[{"id":"s1","version":"1.0.0"}],"compacts":[]}',
        encoding="utf-8",
    )

    stable_skills = '[{"id":"s1","version":"1.0.0"}]' if stable_skill_ref else "[]"
    (manifests / "stable.json").write_text(
        f'{{"registry_version":1,"skills":{stable_skills},"compacts":[]}}',
        encoding="utf-8",
    )


def test_registry_validates_repo_registry() -> None:
    result = validate_registry(_repo_root())
    assert result.ok, "\n".join(result.errors)


def test_registry_detects_id_filename_mismatch(tmp_path: Path) -> None:
    repo_root = _repo_root()
    _copy_schemas(repo_root, tmp_path)

    skills = tmp_path / "registry" / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    skills.joinpath("s1.json").write_text(
        '{"id":"different","version":"1.0.0","title":"Some title","description":"Long enough desc"'
        ',"status":"dev","owners":["me"]}',
        encoding="utf-8",
    )

    compacts = tmp_path / "registry" / "compacts"
    compacts.mkdir(parents=True, exist_ok=True)

    _write_minimal_manifests(tmp_path, stable_skill_ref=False)

    result = validate_registry(tmp_path)
    assert not result.ok
    assert any("must match filename stem" in e for e in result.errors)


def test_stable_manifest_requires_stable_status(tmp_path: Path) -> None:
    repo_root = _repo_root()
    _copy_schemas(repo_root, tmp_path)

    skills = tmp_path / "registry" / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    skills.joinpath("s1.json").write_text(
        '{"id":"s1","version":"1.0.0","title":"Some title","description":"Long enough desc"'
        ',"status":"dev","owners":["me"]}',
        encoding="utf-8",
    )

    compacts = tmp_path / "registry" / "compacts"
    compacts.mkdir(parents=True, exist_ok=True)

    _write_minimal_manifests(tmp_path, stable_skill_ref=True)

    result = validate_registry(tmp_path)
    assert not result.ok
    assert any("must be status=stable" in e for e in result.errors)
