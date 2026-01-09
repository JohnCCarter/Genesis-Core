from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class RegistryValidationResult:
    """Result of registry validation.

    Attributes:
        errors: Human-readable validation errors. Empty means OK.
    """

    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e


def _load_schema(repo_root: Path, schema_name: str) -> dict:
    schema_path = repo_root / "registry" / "schemas" / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Missing schema file: {schema_path}")
    data = _load_json(schema_path)
    if not isinstance(data, dict):
        raise ValueError(f"Schema must be a JSON object: {schema_path}")
    return data


def _schema_validate(errors: list[str], *, data: object, schema: dict, source: Path) -> None:
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=str):
        loc = "".join([f"[{p!r}]" if isinstance(p, str) else f"[{p}]" for p in err.path])
        errors.append(f"{source}: {loc} {err.message}")


def validate_registry(repo_root: Path) -> RegistryValidationResult:
    """Validate the skills/compacts registry (schema + cross-references).

    This function is pure (no git calls) so it can be safely used in unit tests.
    """

    errors: list[str] = []

    skill_schema = _load_schema(repo_root, "skill.schema.json")
    compact_schema = _load_schema(repo_root, "compact.schema.json")
    manifest_schema = _load_schema(repo_root, "manifest.schema.json")

    skills_dir = repo_root / "registry" / "skills"
    compacts_dir = repo_root / "registry" / "compacts"
    manifests_dir = repo_root / "registry" / "manifests"

    skills: dict[tuple[str, str], dict] = {}
    compacts: dict[tuple[str, str], dict] = {}

    for path in sorted(skills_dir.glob("*.json")):
        try:
            data = _load_json(path)
        except Exception as e:  # noqa: BLE001 - convert to validation message
            errors.append(str(e))
            continue
        _schema_validate(errors, data=data, schema=skill_schema, source=path)
        if not isinstance(data, dict):
            errors.append(f"{path}: skill must be a JSON object")
            continue

        file_id = path.stem
        doc_id = str(data.get("id", ""))
        if doc_id and doc_id != file_id:
            errors.append(f"{path}: id={doc_id!r} must match filename stem {file_id!r}")

        version = str(data.get("version", ""))
        key = (doc_id, version)
        if doc_id and version:
            if key in skills:
                errors.append(f"Duplicate skill id+version: {doc_id}@{version}")
            else:
                skills[key] = data

    for path in sorted(compacts_dir.glob("*.json")):
        try:
            data = _load_json(path)
        except Exception as e:  # noqa: BLE001
            errors.append(str(e))
            continue
        _schema_validate(errors, data=data, schema=compact_schema, source=path)
        if not isinstance(data, dict):
            errors.append(f"{path}: compact must be a JSON object")
            continue

        file_id = path.stem
        doc_id = str(data.get("id", ""))
        if doc_id and doc_id != file_id:
            errors.append(f"{path}: id={doc_id!r} must match filename stem {file_id!r}")

        version = str(data.get("version", ""))
        key = (doc_id, version)
        if doc_id and version:
            if key in compacts:
                errors.append(f"Duplicate compact id+version: {doc_id}@{version}")
            else:
                compacts[key] = data

    def _validate_manifest(stage: str) -> None:
        manifest_path = manifests_dir / f"{stage}.json"
        if not manifest_path.exists():
            errors.append(f"Missing manifest: {manifest_path}")
            return

        try:
            manifest = _load_json(manifest_path)
        except Exception as e:  # noqa: BLE001
            errors.append(str(e))
            return

        _schema_validate(errors, data=manifest, schema=manifest_schema, source=manifest_path)
        if not isinstance(manifest, dict):
            errors.append(f"{manifest_path}: manifest must be a JSON object")
            return

        for ref in manifest.get("skills", []) if isinstance(manifest.get("skills"), list) else []:
            if not isinstance(ref, dict):
                errors.append(
                    f"{manifest_path}: skills entry must be object, got {type(ref).__name__}"
                )
                continue
            rid = str(ref.get("id", ""))
            ver = str(ref.get("version", ""))
            key = (rid, ver)
            if key not in skills:
                errors.append(f"{manifest_path}: missing skill {rid}@{ver}")
                continue
            if stage == "stable" and skills[key].get("status") != "stable":
                errors.append(f"{manifest_path}: skill {rid}@{ver} must be status=stable")

        for ref in (
            manifest.get("compacts", []) if isinstance(manifest.get("compacts"), list) else []
        ):
            if not isinstance(ref, dict):
                errors.append(
                    f"{manifest_path}: compacts entry must be object, got {type(ref).__name__}"
                )
                continue
            rid = str(ref.get("id", ""))
            ver = str(ref.get("version", ""))
            key = (rid, ver)
            if key not in compacts:
                errors.append(f"{manifest_path}: missing compact {rid}@{ver}")
                continue
            if stage == "stable" and compacts[key].get("status") != "stable":
                errors.append(f"{manifest_path}: compact {rid}@{ver} must be status=stable")

    _validate_manifest("dev")
    _validate_manifest("stable")

    return RegistryValidationResult(errors=errors)
