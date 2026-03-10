from __future__ import annotations

from pathlib import Path

from core.governance.registry import validate_registry


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


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


def _write_compact(
    dst_root: Path,
    *,
    compact_id: str,
    version: str = "1.0.0",
    status: str = "dev",
    priority: str | None = None,
    conflict_group: str | None = None,
    includes_compacts: list[dict[str, str]] | None = None,
) -> None:
    compacts_dir = dst_root / "registry" / "compacts"
    compacts_dir.mkdir(parents=True, exist_ok=True)

    compact: dict[str, object] = {
        "id": compact_id,
        "version": version,
        "title": f"Compact {compact_id}",
        "description": "Compact description long enough for schema validation.",
        "status": status,
        "owners": ["qa"],
        "scopes": ["registry"],
        "rules": [{"id": "rule_a", "text": "Rule text that satisfies schema."}],
    }
    if priority is not None:
        compact["priority"] = priority
    if conflict_group is not None:
        compact["conflict_group"] = conflict_group
    if includes_compacts is not None:
        compact["includes_compacts"] = includes_compacts

    import json

    (compacts_dir / f"{compact_id}.json").write_text(
        json.dumps(compact, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_manifest_with_compacts(
    dst_root: Path, *, stage: str, compact_refs: list[dict[str, str]]
) -> None:
    manifests = dst_root / "registry" / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)

    import json

    payload = {
        "registry_version": 1,
        "skills": [],
        "compacts": compact_refs,
    }
    (manifests / f"{stage}.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )


def test_registry_validates_repo_registry() -> None:
    result = validate_registry(_repo_root())
    assert result.ok, "\n".join(result.errors)


def test_registry_detects_id_filename_mismatch(tmp_path: Path) -> None:
    repo_root = _repo_root()
    _copy_schemas(repo_root, tmp_path)

    skills = tmp_path / ".github" / "skills"
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

    skills = tmp_path / ".github" / "skills"
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


def test_registry_dedupes_direct_plus_included_compact_before_conflict_check(
    tmp_path: Path,
) -> None:
    repo_root = _repo_root()
    _copy_schemas(repo_root, tmp_path)

    # Minimal dirs expected by validator.
    (tmp_path / ".github" / "skills").mkdir(parents=True, exist_ok=True)

    _write_compact(
        tmp_path,
        compact_id="base_compact",
        conflict_group="core_group",
        priority="P1",
    )
    _write_compact(
        tmp_path,
        compact_id="pack_compact",
        includes_compacts=[{"id": "base_compact", "version": "1.0.0"}],
    )

    # base_compact is activated directly and again via pack_compact includes.
    _write_manifest_with_compacts(
        tmp_path,
        stage="dev",
        compact_refs=[
            {"id": "base_compact", "version": "1.0.0"},
            {"id": "pack_compact", "version": "1.0.0"},
        ],
    )
    _write_manifest_with_compacts(tmp_path, stage="stable", compact_refs=[])

    result = validate_registry(tmp_path)
    assert result.ok, "\n".join(result.errors)


def test_registry_still_flags_real_conflict_between_distinct_compacts(tmp_path: Path) -> None:
    repo_root = _repo_root()
    _copy_schemas(repo_root, tmp_path)

    (tmp_path / ".github" / "skills").mkdir(parents=True, exist_ok=True)

    _write_compact(
        tmp_path,
        compact_id="conflict_a",
        conflict_group="shared_group",
        priority="P1",
    )
    _write_compact(
        tmp_path,
        compact_id="conflict_b",
        conflict_group="shared_group",
        priority="P2",
    )

    _write_manifest_with_compacts(
        tmp_path,
        stage="dev",
        compact_refs=[
            {"id": "conflict_a", "version": "1.0.0"},
            {"id": "conflict_b", "version": "1.0.0"},
        ],
    )
    _write_manifest_with_compacts(tmp_path, stage="stable", compact_refs=[])

    result = validate_registry(tmp_path)
    assert not result.ok
    assert any("compact conflict in group 'shared_group'" in e for e in result.errors)
