from __future__ import annotations

import pytest

from core.research_ledger.enums import LedgerEntityType
from core.research_ledger.models import HypothesisRecord
from core.research_ledger.validators import LedgerValidationError, validate_record


def test_validate_record_accepts_valid_hypothesis() -> None:
    record = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Risk-state improves 3h exits",
        hypothesis="Risk-state gating improves OOS drawdown on 3h.",
        rationale="Observed repeated drawdown clustering in balanced/bear transitions.",
    )

    validate_record(record)


def test_validate_record_rejects_bad_id_prefix() -> None:
    record = HypothesisRecord(
        entity_id="EXP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Bad id",
        hypothesis="This should fail.",
    )

    with pytest.raises(LedgerValidationError, match="HYP-YYYY-NNNN"):
        validate_record(record)


def test_validate_record_rejects_non_json_metadata() -> None:
    record = HypothesisRecord(
        entity_id="HYP-2026-0002",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Bad metadata",
        hypothesis="This should fail.",
        metadata={"oops": {1, 2, 3}},  # type: ignore[arg-type]
    )

    with pytest.raises(LedgerValidationError, match="unsupported JSON value"):
        validate_record(record)


def test_validate_record_requires_timezone() -> None:
    record = HypothesisRecord(
        entity_id="HYP-2026-0003",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00",
        title="Naive timestamp",
        hypothesis="This should fail.",
    )

    with pytest.raises(LedgerValidationError, match="timezone"):
        validate_record(record)
