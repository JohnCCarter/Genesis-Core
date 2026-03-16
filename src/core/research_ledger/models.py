from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, TypeAlias

from core.research_ledger.enums import (
    ArtifactKind,
    ChampionStatus,
    ExperimentStatus,
    GovernanceDecisionKind,
    HypothesisStatus,
    LedgerEntityType,
    PromotionTargetKind,
    ProposalStatus,
)

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

SCHEMA_VERSION = "research_ledger.v1"


@dataclass(frozen=True, slots=True)
class CodeVersionRef:
    commit_sha: str
    branch: str | None = None
    tree_state: str | None = None


@dataclass(frozen=True, slots=True)
class DatasetRef:
    dataset_id: str
    version: str
    path: str | None = None
    content_hash: str | None = None


@dataclass(frozen=True, slots=True)
class ArtifactLink:
    artifact_id: str | None = None
    path: str | None = None
    role: str = "related"
    metadata: JsonObject = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class IntelligenceRef:
    module: str
    ref_kind: str
    artifact_id: str | None = None
    path: str | None = None
    label: str | None = None
    metadata: JsonObject = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class LedgerRecord:
    entity_id: str
    entity_type: LedgerEntityType
    created_at: str
    schema_version: str = SCHEMA_VERSION
    metadata: JsonObject = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class HypothesisRecord(LedgerRecord):
    title: str = ""
    hypothesis: str = ""
    rationale: str = ""
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    tags: tuple[str, ...] = ()
    intelligence_refs: tuple[IntelligenceRef, ...] = ()


@dataclass(frozen=True, slots=True)
class ProposalRecord(LedgerRecord):
    hypothesis_id: str = ""
    title: str = ""
    summary: str = ""
    proposer: str | None = None
    command_packet_path: str | None = None
    status: ProposalStatus = ProposalStatus.DRAFT
    config_paths: tuple[str, ...] = ()
    dataset_refs: tuple[DatasetRef, ...] = ()
    artifact_links: tuple[ArtifactLink, ...] = ()
    intelligence_refs: tuple[IntelligenceRef, ...] = ()


@dataclass(frozen=True, slots=True)
class ExperimentRecord(LedgerRecord):
    hypothesis_id: str = ""
    proposal_id: str = ""
    title: str = ""
    objective: str = ""
    status: ExperimentStatus = ExperimentStatus.PLANNED
    command_packet_path: str | None = None
    run_command: str | None = None
    code_version: CodeVersionRef | None = None
    config_paths: tuple[str, ...] = ()
    dataset_refs: tuple[DatasetRef, ...] = ()
    artifact_links: tuple[ArtifactLink, ...] = ()
    intelligence_refs: tuple[IntelligenceRef, ...] = ()
    started_at: str | None = None
    completed_at: str | None = None
    metrics: JsonObject = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ArtifactRecord(LedgerRecord):
    experiment_id: str | None = None
    artifact_kind: ArtifactKind = ArtifactKind.OTHER
    path: str = ""
    role: str = "evidence"
    format: str | None = None
    checksum_sha256: str | None = None
    size_bytes: int | None = None
    intelligence_refs: tuple[IntelligenceRef, ...] = ()


@dataclass(frozen=True, slots=True)
class GovernanceDecisionRecord(LedgerRecord):
    subject_type: LedgerEntityType = LedgerEntityType.EXPERIMENT
    subject_id: str = ""
    decision: GovernanceDecisionKind = GovernanceDecisionKind.DEFERRED
    rationale: str = ""
    decided_by: str | None = None
    gate_names: tuple[str, ...] = ()
    artifact_links: tuple[ArtifactLink, ...] = ()
    intelligence_refs: tuple[IntelligenceRef, ...] = ()


@dataclass(frozen=True, slots=True)
class PromotionRecord(LedgerRecord):
    subject_experiment_id: str = ""
    governance_decision_id: str = ""
    target_kind: PromotionTargetKind = PromotionTargetKind.CHAMPION
    target_ref: str = ""
    source_artifact_id: str | None = None
    previous_target_ref: str | None = None
    rationale: str = ""
    intelligence_refs: tuple[IntelligenceRef, ...] = ()


@dataclass(frozen=True, slots=True)
class ChampionRecord(LedgerRecord):
    symbol: str = ""
    timeframe: str = ""
    promotion_record_id: str = ""
    governance_decision_id: str | None = None
    experiment_id: str | None = None
    artifact_id: str | None = None
    config_path: str | None = None
    predecessor_champion_id: str | None = None
    status: ChampionStatus = ChampionStatus.ACTIVE
    intelligence_refs: tuple[IntelligenceRef, ...] = ()


LedgerRecordT: TypeAlias = (
    HypothesisRecord
    | ProposalRecord
    | ExperimentRecord
    | ArtifactRecord
    | GovernanceDecisionRecord
    | PromotionRecord
    | ChampionRecord
)


def record_to_dict(record: LedgerRecordT) -> JsonObject:
    payload = asdict(record)
    payload["entity_type"] = str(record.entity_type)
    return payload


def _build_dataset_refs(items: list[dict[str, Any]] | None) -> tuple[DatasetRef, ...]:
    return tuple(DatasetRef(**item) for item in (items or []))


def _build_artifact_links(items: list[dict[str, Any]] | None) -> tuple[ArtifactLink, ...]:
    return tuple(ArtifactLink(**item) for item in (items or []))


def _build_intelligence_refs(
    items: list[dict[str, Any]] | None,
) -> tuple[IntelligenceRef, ...]:
    return tuple(IntelligenceRef(**item) for item in (items or []))


def _load_base_kwargs(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "entity_id": str(data["entity_id"]),
        "entity_type": LedgerEntityType(str(data["entity_type"])),
        "created_at": str(data["created_at"]),
        "schema_version": str(data.get("schema_version", SCHEMA_VERSION)),
        "metadata": dict(data.get("metadata") or {}),
    }


def record_from_dict(data: dict[str, Any]) -> LedgerRecordT:
    entity_type = LedgerEntityType(str(data["entity_type"]))
    base_kwargs = _load_base_kwargs(data)
    match entity_type:
        case LedgerEntityType.HYPOTHESIS:
            return HypothesisRecord(
                **base_kwargs,
                title=str(data.get("title", "")),
                hypothesis=str(data.get("hypothesis", "")),
                rationale=str(data.get("rationale", "")),
                status=HypothesisStatus(str(data.get("status", HypothesisStatus.PROPOSED))),
                tags=tuple(str(tag) for tag in data.get("tags") or []),
                intelligence_refs=_build_intelligence_refs(data.get("intelligence_refs")),
            )
        case LedgerEntityType.PROPOSAL:
            return ProposalRecord(
                **base_kwargs,
                hypothesis_id=str(data.get("hypothesis_id", "")),
                title=str(data.get("title", "")),
                summary=str(data.get("summary", "")),
                proposer=(str(data["proposer"]) if data.get("proposer") is not None else None),
                command_packet_path=(
                    str(data["command_packet_path"])
                    if data.get("command_packet_path") is not None
                    else None
                ),
                status=ProposalStatus(str(data.get("status", ProposalStatus.DRAFT))),
                config_paths=tuple(str(path) for path in data.get("config_paths") or []),
                dataset_refs=_build_dataset_refs(data.get("dataset_refs")),
                artifact_links=_build_artifact_links(data.get("artifact_links")),
                intelligence_refs=_build_intelligence_refs(data.get("intelligence_refs")),
            )
        case LedgerEntityType.EXPERIMENT:
            code_version_raw = data.get("code_version")
            code_version = (
                CodeVersionRef(**code_version_raw) if isinstance(code_version_raw, dict) else None
            )
            return ExperimentRecord(
                **base_kwargs,
                hypothesis_id=str(data.get("hypothesis_id", "")),
                proposal_id=str(data.get("proposal_id", "")),
                title=str(data.get("title", "")),
                objective=str(data.get("objective", "")),
                status=ExperimentStatus(str(data.get("status", ExperimentStatus.PLANNED))),
                command_packet_path=(
                    str(data["command_packet_path"])
                    if data.get("command_packet_path") is not None
                    else None
                ),
                run_command=(str(data["run_command"]) if data.get("run_command") else None),
                code_version=code_version,
                config_paths=tuple(str(path) for path in data.get("config_paths") or []),
                dataset_refs=_build_dataset_refs(data.get("dataset_refs")),
                artifact_links=_build_artifact_links(data.get("artifact_links")),
                intelligence_refs=_build_intelligence_refs(data.get("intelligence_refs")),
                started_at=(str(data["started_at"]) if data.get("started_at") else None),
                completed_at=(str(data["completed_at"]) if data.get("completed_at") else None),
                metrics=dict(data.get("metrics") or {}),
            )
        case LedgerEntityType.ARTIFACT:
            size_raw = data.get("size_bytes")
            return ArtifactRecord(
                **base_kwargs,
                experiment_id=(str(data["experiment_id"]) if data.get("experiment_id") else None),
                artifact_kind=ArtifactKind(str(data.get("artifact_kind", ArtifactKind.OTHER))),
                path=str(data.get("path", "")),
                role=str(data.get("role", "evidence")),
                format=(str(data["format"]) if data.get("format") else None),
                checksum_sha256=(
                    str(data["checksum_sha256"]) if data.get("checksum_sha256") else None
                ),
                size_bytes=int(size_raw) if size_raw is not None else None,
                intelligence_refs=_build_intelligence_refs(data.get("intelligence_refs")),
            )
        case LedgerEntityType.GOVERNANCE_DECISION:
            return GovernanceDecisionRecord(
                **base_kwargs,
                subject_type=LedgerEntityType(str(data.get("subject_type"))),
                subject_id=str(data.get("subject_id", "")),
                decision=GovernanceDecisionKind(
                    str(data.get("decision", GovernanceDecisionKind.DEFERRED))
                ),
                rationale=str(data.get("rationale", "")),
                decided_by=(str(data["decided_by"]) if data.get("decided_by") else None),
                gate_names=tuple(str(name) for name in data.get("gate_names") or []),
                artifact_links=_build_artifact_links(data.get("artifact_links")),
                intelligence_refs=_build_intelligence_refs(data.get("intelligence_refs")),
            )
        case LedgerEntityType.PROMOTION_RECORD:
            return PromotionRecord(
                **base_kwargs,
                subject_experiment_id=str(data.get("subject_experiment_id", "")),
                governance_decision_id=str(data.get("governance_decision_id", "")),
                target_kind=PromotionTargetKind(
                    str(data.get("target_kind", PromotionTargetKind.CHAMPION))
                ),
                target_ref=str(data.get("target_ref", "")),
                source_artifact_id=(
                    str(data["source_artifact_id"]) if data.get("source_artifact_id") else None
                ),
                previous_target_ref=(
                    str(data["previous_target_ref"]) if data.get("previous_target_ref") else None
                ),
                rationale=str(data.get("rationale", "")),
                intelligence_refs=_build_intelligence_refs(data.get("intelligence_refs")),
            )
        case LedgerEntityType.CHAMPION_RECORD:
            return ChampionRecord(
                **base_kwargs,
                symbol=str(data.get("symbol", "")),
                timeframe=str(data.get("timeframe", "")),
                promotion_record_id=str(data.get("promotion_record_id", "")),
                governance_decision_id=(
                    str(data["governance_decision_id"])
                    if data.get("governance_decision_id")
                    else None
                ),
                experiment_id=(str(data["experiment_id"]) if data.get("experiment_id") else None),
                artifact_id=(str(data["artifact_id"]) if data.get("artifact_id") else None),
                config_path=(str(data["config_path"]) if data.get("config_path") else None),
                predecessor_champion_id=(
                    str(data["predecessor_champion_id"])
                    if data.get("predecessor_champion_id")
                    else None
                ),
                status=ChampionStatus(str(data.get("status", ChampionStatus.ACTIVE))),
                intelligence_refs=_build_intelligence_refs(data.get("intelligence_refs")),
            )
    raise ValueError(f"Unsupported entity_type: {entity_type}")
