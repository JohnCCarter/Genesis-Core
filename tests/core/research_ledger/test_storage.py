from __future__ import annotations

import json
from pathlib import Path

from core.research_ledger.enums import LedgerEntityType
from core.research_ledger.models import HypothesisRecord
from core.research_ledger.storage import LedgerStorage


def test_storage_writes_stable_json_payload(tmp_path: Path) -> None:
    storage = LedgerStorage(root=tmp_path / "artifacts" / "research_ledger")
    record = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Stable json",
        hypothesis="Stable output is required.",
        tags=("ledger", "research"),
    )

    path = storage.write_record(record)
    payload = path.read_text(encoding="utf-8")

    assert payload.endswith("\n")
    assert '  "entity_id": "HYP-2026-0001"' in payload
    assert payload.index('"created_at"') < payload.index('"entity_id"')

    loaded = storage.read_record(LedgerEntityType.HYPOTHESIS, "HYP-2026-0001")
    assert loaded == record


def test_next_entity_id_is_deterministic(tmp_path: Path) -> None:
    storage = LedgerStorage(root=tmp_path / "artifacts" / "research_ledger")

    storage.write_record(
        HypothesisRecord(
            entity_id="HYP-2026-0001",
            entity_type=LedgerEntityType.HYPOTHESIS,
            created_at="2026-03-16T12:00:00+00:00",
            title="One",
            hypothesis="One",
        )
    )
    storage.write_record(
        HypothesisRecord(
            entity_id="HYP-2026-0002",
            entity_type=LedgerEntityType.HYPOTHESIS,
            created_at="2026-03-16T12:01:00+00:00",
            title="Two",
            hypothesis="Two",
        )
    )

    assert storage.next_entity_id(LedgerEntityType.HYPOTHESIS, 2026) == "HYP-2026-0003"


def test_write_index_round_trip(tmp_path: Path) -> None:
    storage = LedgerStorage(root=tmp_path / "artifacts" / "research_ledger")
    payload = {"schema_version": "research_ledger.v1", "items": [{"entity_id": "HYP-2026-0001"}]}

    storage.write_index("hypothesis", payload)
    loaded = storage.read_index("hypothesis")

    assert loaded == payload
    raw = json.loads(
        (
            tmp_path / "artifacts" / "research_ledger" / "indexes" / "hypothesis_index.json"
        ).read_text(encoding="utf-8")
    )
    assert raw == payload
