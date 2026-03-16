from __future__ import annotations

from enum import StrEnum


class LedgerEntityType(StrEnum):
    HYPOTHESIS = "hypothesis"
    PROPOSAL = "proposal"
    EXPERIMENT = "experiment"
    ARTIFACT = "artifact"
    GOVERNANCE_DECISION = "governance_decision"
    PROMOTION_RECORD = "promotion_record"
    CHAMPION_RECORD = "champion_record"


class HypothesisStatus(StrEnum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ProposalStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    ARCHIVED = "archived"


class ExperimentStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    VALIDATED = "validated"


class ArtifactKind(StrEnum):
    COMMAND_PACKET = "command_packet"
    CONFIG_SNAPSHOT = "config_snapshot"
    DATASET_SNAPSHOT = "dataset_snapshot"
    RESULT_SUMMARY = "result_summary"
    RUN_LOG = "run_log"
    EVIDENCE_BUNDLE = "evidence_bundle"
    INTELLIGENCE_OUTPUT = "intelligence_output"
    OTHER = "other"


class GovernanceDecisionKind(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    DEFERRED = "deferred"
    ACCEPTED = "accepted"


class PromotionTargetKind(StrEnum):
    PAPER = "paper"
    CHAMPION = "champion"
    LIVE = "live"
    ARCHIVE = "archive"


class ChampionStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    RETIRED = "retired"
