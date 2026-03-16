from __future__ import annotations

from dataclasses import replace

import pytest

from core.research_ledger.enums import LedgerEntityType
from core.research_ledger.models import (
    ArtifactLink,
    CodeVersionRef,
    DatasetRef,
    ExperimentRecord,
    HypothesisRecord,
)
from core.research_ledger.validators import LedgerValidationError, validate_record


def _valid_experiment() -> ExperimentRecord:
    return ExperimentRecord(
        entity_id="EXP-2026-0001",
        entity_type=LedgerEntityType.EXPERIMENT,
        created_at="2026-03-16T12:10:00+00:00",
        hypothesis_id="HYP-2026-0001",
        proposal_id="PROP-2026-0001",
        title="1h RI vs OFF",
        objective="Validate canonical Phase B on 1h.",
        command_packet_path="docs/governance/templates/command_packet.md",
        code_version=CodeVersionRef(commit_sha="abc123def456"),
        config_paths=("config/optimizer/1h/tBTCUSD_1h_risk_optuna_smoke.yaml",),
        dataset_refs=(DatasetRef(dataset_id="curated.tBTCUSD.1h", version="2026-03-16"),),
    )


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


@pytest.mark.parametrize(
    ("record", "message"),
    [
        (
            replace(_valid_experiment(), command_packet_path=None),
            "command_packet_path must be non-empty",
        ),
        (replace(_valid_experiment(), code_version=None), "code_version must be provided"),
        (
            replace(_valid_experiment(), config_paths=()),
            "config_paths must contain at least one entry",
        ),
        (
            replace(_valid_experiment(), dataset_refs=()),
            "dataset_refs must contain at least one entry",
        ),
    ],
)
def test_validate_record_rejects_experiment_missing_traceability_fields(
    record: ExperimentRecord,
    message: str,
) -> None:
    with pytest.raises(LedgerValidationError, match=message):
        validate_record(record)


def test_validate_record_accepts_traceable_experiment() -> None:
    validate_record(_valid_experiment())


@pytest.mark.parametrize(
    ("record", "message"),
    [
        (
            replace(
                _valid_experiment(),
                code_version=CodeVersionRef(commit_sha="   "),
            ),
            "code_version.commit_sha must be non-empty",
        ),
        (
            replace(_valid_experiment(), config_paths=("",)),
            r"config_paths\[0\] must be non-empty",
        ),
        (
            replace(
                _valid_experiment(),
                artifact_links=(ArtifactLink(artifact_id=""),),
            ),
            r"artifact_links\[0\]\.artifact_id must be non-empty",
        ),
    ],
)
def test_validate_record_rejects_blank_traceability_values(
    record: ExperimentRecord,
    message: str,
) -> None:
    with pytest.raises(LedgerValidationError, match=message):
        validate_record(record)
