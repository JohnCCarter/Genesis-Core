from __future__ import annotations

import json
import os
import re
from pathlib import Path

from core.research_ledger.enums import LedgerEntityType
from core.research_ledger.models import JsonObject, LedgerRecordT, record_from_dict, record_to_dict

_ENTITY_DIRS = {
    LedgerEntityType.HYPOTHESIS: "hypotheses",
    LedgerEntityType.PROPOSAL: "proposals",
    LedgerEntityType.EXPERIMENT: "experiments",
    LedgerEntityType.ARTIFACT: "artifacts",
    LedgerEntityType.GOVERNANCE_DECISION: "governance",
    LedgerEntityType.PROMOTION_RECORD: "promotions",
    LedgerEntityType.CHAMPION_RECORD: "champions",
}

_INDEX_FILES = {
    "hypothesis": "hypothesis_index.json",
    "experiment": "experiment_index.json",
    "champion": "champion_index.json",
}


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def json_dumps_stable(data: JsonObject) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)
    try:
        dir_fd = os.open(path.parent, os.O_DIRECTORY)
        os.fsync(dir_fd)
        os.close(dir_fd)
    except Exception:  # nosec B110 - best effort on platforms without O_DIRECTORY
        pass


class LedgerPaths:
    def __init__(self, root: Path | None = None) -> None:
        repo_root = _resolve_repo_root()
        self.root = root or (repo_root / "artifacts" / "research_ledger")
        self.indexes_dir = self.root / "indexes"

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        for directory in _ENTITY_DIRS.values():
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        self.indexes_dir.mkdir(parents=True, exist_ok=True)

    def entity_dir(self, entity_type: LedgerEntityType) -> Path:
        return self.root / _ENTITY_DIRS[entity_type]

    def record_path(self, entity_type: LedgerEntityType, entity_id: str) -> Path:
        return self.entity_dir(entity_type) / f"{entity_id}.json"

    def index_path(self, index_name: str) -> Path:
        return self.indexes_dir / _INDEX_FILES[index_name]


class LedgerStorage:
    def __init__(self, root: Path | None = None) -> None:
        self.paths = LedgerPaths(root=root)
        self.paths.ensure()

    def exists(self, entity_type: LedgerEntityType, entity_id: str) -> bool:
        return self.paths.record_path(entity_type, entity_id).exists()

    def write_record(self, record: LedgerRecordT) -> Path:
        path = self.paths.record_path(record.entity_type, record.entity_id)
        payload = record_to_dict(record)
        atomic_write_text(path, json_dumps_stable(payload))
        return path

    def read_record(self, entity_type: LedgerEntityType, entity_id: str) -> LedgerRecordT:
        path = self.paths.record_path(entity_type, entity_id)
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Ledger record must be a JSON object: {path}")
        return record_from_dict(data)

    def list_records(self, entity_type: LedgerEntityType) -> list[LedgerRecordT]:
        records: list[LedgerRecordT] = []
        for path in sorted(self.paths.entity_dir(entity_type).glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError(f"Ledger record must be a JSON object: {path}")
            records.append(record_from_dict(data))
        records.sort(key=lambda record: record.entity_id)
        return records

    def write_index(self, index_name: str, payload: JsonObject) -> Path:
        path = self.paths.index_path(index_name)
        atomic_write_text(path, json_dumps_stable(payload))
        return path

    def read_index(self, index_name: str) -> JsonObject:
        path = self.paths.index_path(index_name)
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Ledger index must be a JSON object: {path}")
        return data

    def next_entity_id(self, entity_type: LedgerEntityType, year: int) -> str:
        prefix = {
            LedgerEntityType.HYPOTHESIS: "HYP",
            LedgerEntityType.PROPOSAL: "PROP",
            LedgerEntityType.EXPERIMENT: "EXP",
            LedgerEntityType.ARTIFACT: "ART",
            LedgerEntityType.GOVERNANCE_DECISION: "GOV",
            LedgerEntityType.PROMOTION_RECORD: "PROMO",
            LedgerEntityType.CHAMPION_RECORD: "CHAMP",
        }[entity_type]
        pattern = re.compile(rf"^{prefix}-{year}-(\d{{4}})\.json$")
        max_value = 0
        for path in sorted(self.paths.entity_dir(entity_type).glob(f"{prefix}-{year}-*.json")):
            match = pattern.match(path.name)
            if match is None:
                continue
            max_value = max(max_value, int(match.group(1)))
        return f"{prefix}-{year}-{max_value + 1:04d}"
