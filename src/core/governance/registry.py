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


def _priority_rank(compact: dict) -> int:
    """Map P0..P4 to numeric rank (lower is higher priority)."""

    val = compact.get("priority")
    if not isinstance(val, str):
        return 99
    mapping = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    return mapping.get(val, 99)


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

    # Validate compact packs (includes_compacts) references.
    for (cid, _ver), compact in compacts.items():
        includes = compact.get("includes_compacts")
        if includes is None:
            continue
        if not isinstance(includes, list):
            errors.append(
                f"registry/compacts/{cid}.json: includes_compacts must be a list, got {type(includes).__name__}"
            )
            continue
        for ref in includes:
            if not isinstance(ref, dict):
                errors.append(
                    f"registry/compacts/{cid}.json: includes_compacts entry must be object, got {type(ref).__name__}"
                )
                continue
            rid = str(ref.get("id", ""))
            rver = str(ref.get("version", ""))
            if (rid, rver) not in compacts:
                errors.append(
                    f"registry/compacts/{cid}.json: includes missing compact {rid}@{rver}"
                )

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
            if stage == "stable" and skills[key].get("locked") is not True:
                errors.append(f"{manifest_path}: skill {rid}@{ver} must be locked=true for stable")

        active_compacts: list[tuple[tuple[str, str], dict]] = []
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

            active_compacts.append((key, compacts[key]))

            # Expand compact packs (one level) into active compacts.
            includes = compacts[key].get("includes_compacts")
            if isinstance(includes, list):
                for inc in includes:
                    if not isinstance(inc, dict):
                        continue
                    iid = str(inc.get("id", ""))
                    iver = str(inc.get("version", ""))
                    ikey = (iid, iver)
                    if ikey in compacts:
                        active_compacts.append((ikey, compacts[ikey]))

        # Enforce compact conflicts per conflict_group with priority P0..P4.
        groups: dict[str, list[tuple[int, str]]] = {}
        for (rid, rver), compact in active_compacts:
            cg = compact.get("conflict_group")
            if not isinstance(cg, str) or not cg.strip():
                continue
            label = f"{rid}@{rver}"
            groups.setdefault(cg, []).append((_priority_rank(compact), label))

        for cg, items in groups.items():
            if len(items) <= 1:
                continue
            items_sorted = sorted(items, key=lambda x: (x[0], x[1]))
            keep = items_sorted[0][1]
            drop = ", ".join([lbl for _, lbl in items_sorted[1:]])
            all_list = ", ".join([f"{lbl}(P{rank})" for rank, lbl in items_sorted])
            errors.append(
                f"{manifest_path}: compact conflict in group {cg!r}: {all_list}. "
                f"Alternative A: keep {keep} and remove {drop}. "
                f"Alternative B: remove {keep} and keep one of [{drop}]."
            )

    _validate_manifest("dev")
    _validate_manifest("stable")

    return RegistryValidationResult(errors=errors)
