from __future__ import annotations

import math
import re
from datetime import datetime

from core.research_ledger.enums import LedgerEntityType
from core.research_ledger.models import JsonValue, LedgerRecordT

_ENTITY_PREFIX = {
    LedgerEntityType.HYPOTHESIS: "HYP",
    LedgerEntityType.PROPOSAL: "PROP",
    LedgerEntityType.EXPERIMENT: "EXP",
    LedgerEntityType.ARTIFACT: "ART",
    LedgerEntityType.GOVERNANCE_DECISION: "GOV",
    LedgerEntityType.PROMOTION_RECORD: "PROMO",
    LedgerEntityType.CHAMPION_RECORD: "CHAMP",
}

_ID_PATTERNS = {
    entity_type: re.compile(rf"^{prefix}-\d{{4}}-\d{{4}}$")
    for entity_type, prefix in _ENTITY_PREFIX.items()
}


class LedgerValidationError(ValueError):
    """Raised when a ledger record violates the v1 schema."""


def validate_json_value(value: JsonValue, *, path: str = "value") -> None:
    if isinstance(value, str | bool) or value is None or isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise LedgerValidationError(f"{path} must contain finite floats only")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_json_value(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise LedgerValidationError(f"{path} keys must be strings")
            validate_json_value(item, path=f"{path}.{key}")
        return
    raise LedgerValidationError(f"{path} contains unsupported JSON value {type(value).__name__}")


def validate_timestamp(value: str | None, *, field_name: str) -> None:
    if value is None:
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LedgerValidationError(f"{field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise LedgerValidationError(f"{field_name} must include timezone information")


def validate_entity_id(entity_type: LedgerEntityType, entity_id: str) -> None:
    if not _ID_PATTERNS[entity_type].match(entity_id):
        prefix = _ENTITY_PREFIX[entity_type]
        raise LedgerValidationError(
            f"{entity_type} id must match {prefix}-YYYY-NNNN, got {entity_id!r}"
        )


def _require_non_empty(value: str | None, *, field_name: str) -> None:
    if value is None or not value.strip():
        raise LedgerValidationError(f"{field_name} must be non-empty")


def _validate_experiment_traceability(record: LedgerRecordT) -> None:
    _require_non_empty(record.command_packet_path, field_name="command_packet_path")
    if record.code_version is None:
        raise LedgerValidationError("code_version must be provided")
    _require_non_empty(record.code_version.commit_sha, field_name="code_version.commit_sha")
    if not record.config_paths:
        raise LedgerValidationError("config_paths must contain at least one entry")
    for index, config_path in enumerate(record.config_paths):
        _require_non_empty(config_path, field_name=f"config_paths[{index}]")
    if not record.dataset_refs:
        raise LedgerValidationError("dataset_refs must contain at least one entry")
    for index, link in enumerate(record.artifact_links):
        if link.artifact_id is not None:
            _require_non_empty(link.artifact_id, field_name=f"artifact_links[{index}].artifact_id")


def _validate_reference(entity_type: LedgerEntityType, entity_id: str, *, field_name: str) -> None:
    validate_entity_id(entity_type, entity_id)
    _require_non_empty(entity_id, field_name=field_name)


def _validate_metadata(record: LedgerRecordT) -> None:
    validate_json_value(record.metadata, path=f"{record.entity_id}.metadata")
    if hasattr(record, "metrics"):
        validate_json_value(
            getattr(record, "metrics"),  # noqa: B009 - preserve canonical ledger semantics
            path=f"{record.entity_id}.metrics",
        )
    if hasattr(record, "intelligence_refs"):
        for index, ref in enumerate(
            getattr(record, "intelligence_refs")  # noqa: B009 - preserve canonical ledger semantics
        ):
            _require_non_empty(ref.module, field_name=f"intelligence_refs[{index}].module")
            _require_non_empty(ref.ref_kind, field_name=f"intelligence_refs[{index}].ref_kind")
            validate_json_value(
                ref.metadata,
                path=f"{record.entity_id}.intelligence_refs[{index}].metadata",
            )
    if hasattr(record, "artifact_links"):
        for index, link in enumerate(
            getattr(record, "artifact_links")  # noqa: B009 - preserve canonical ledger semantics
        ):
            if link.artifact_id is None and link.path is None:
                raise LedgerValidationError(
                    f"artifact_links[{index}] must have artifact_id or path"
                )
            validate_json_value(
                link.metadata,
                path=f"{record.entity_id}.artifact_links[{index}].metadata",
            )
    if hasattr(record, "dataset_refs"):
        for index, dataset in enumerate(
            getattr(record, "dataset_refs")  # noqa: B009 - preserve canonical ledger semantics
        ):
            _require_non_empty(dataset.dataset_id, field_name=f"dataset_refs[{index}].dataset_id")
            _require_non_empty(dataset.version, field_name=f"dataset_refs[{index}].version")


def validate_record(record: LedgerRecordT) -> None:
    validate_entity_id(record.entity_type, record.entity_id)
    validate_timestamp(record.created_at, field_name="created_at")
    _validate_metadata(record)

    match record.entity_type:
        case LedgerEntityType.HYPOTHESIS:
            _require_non_empty(record.title, field_name="title")
            _require_non_empty(record.hypothesis, field_name="hypothesis")
        case LedgerEntityType.PROPOSAL:
            _validate_reference(
                LedgerEntityType.HYPOTHESIS,
                record.hypothesis_id,
                field_name="hypothesis_id",
            )
            _require_non_empty(record.title, field_name="title")
            _require_non_empty(record.summary, field_name="summary")
        case LedgerEntityType.EXPERIMENT:
            _validate_reference(
                LedgerEntityType.HYPOTHESIS,
                record.hypothesis_id,
                field_name="hypothesis_id",
            )
            _validate_reference(
                LedgerEntityType.PROPOSAL,
                record.proposal_id,
                field_name="proposal_id",
            )
            _require_non_empty(record.title, field_name="title")
            _require_non_empty(record.objective, field_name="objective")
            _validate_experiment_traceability(record)
            validate_timestamp(record.started_at, field_name="started_at")
            validate_timestamp(record.completed_at, field_name="completed_at")
            if record.code_version is not None:
                _require_non_empty(
                    record.code_version.commit_sha, field_name="code_version.commit_sha"
                )
        case LedgerEntityType.ARTIFACT:
            _require_non_empty(record.path, field_name="path")
            if record.experiment_id is not None:
                _validate_reference(
                    LedgerEntityType.EXPERIMENT,
                    record.experiment_id,
                    field_name="experiment_id",
                )
        case LedgerEntityType.GOVERNANCE_DECISION:
            _validate_reference(record.subject_type, record.subject_id, field_name="subject_id")
            _require_non_empty(record.rationale, field_name="rationale")
        case LedgerEntityType.PROMOTION_RECORD:
            _validate_reference(
                LedgerEntityType.EXPERIMENT,
                record.subject_experiment_id,
                field_name="subject_experiment_id",
            )
            _validate_reference(
                LedgerEntityType.GOVERNANCE_DECISION,
                record.governance_decision_id,
                field_name="governance_decision_id",
            )
            _require_non_empty(record.target_ref, field_name="target_ref")
        case LedgerEntityType.CHAMPION_RECORD:
            _require_non_empty(record.symbol, field_name="symbol")
            _require_non_empty(record.timeframe, field_name="timeframe")
            _validate_reference(
                LedgerEntityType.PROMOTION_RECORD,
                record.promotion_record_id,
                field_name="promotion_record_id",
            )
            if record.governance_decision_id is not None:
                _validate_reference(
                    LedgerEntityType.GOVERNANCE_DECISION,
                    record.governance_decision_id,
                    field_name="governance_decision_id",
                )
            if record.experiment_id is not None:
                _validate_reference(
                    LedgerEntityType.EXPERIMENT,
                    record.experiment_id,
                    field_name="experiment_id",
                )
            if record.artifact_id is not None:
                _validate_reference(
                    LedgerEntityType.ARTIFACT,
                    record.artifact_id,
                    field_name="artifact_id",
                )
            if record.predecessor_champion_id is not None:
                _validate_reference(
                    LedgerEntityType.CHAMPION_RECORD,
                    record.predecessor_champion_id,
                    field_name="predecessor_champion_id",
                )
        case _:
            raise LedgerValidationError(f"Unsupported entity type: {record.entity_type}")
