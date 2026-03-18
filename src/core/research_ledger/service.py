from __future__ import annotations

from dataclasses import replace

from core.research_ledger.enums import LedgerEntityType
from core.research_ledger.indexes import (
    build_champion_index,
    build_experiment_index,
    build_hypothesis_index,
)
from core.research_ledger.models import (
    ArtifactRecord,
    ChampionRecord,
    ExperimentRecord,
    GovernanceDecisionRecord,
    HypothesisRecord,
    LedgerRecordT,
    PromotionRecord,
    ProposalRecord,
)
from core.research_ledger.queries import LedgerQueries
from core.research_ledger.storage import LedgerStorage
from core.research_ledger.validators import LedgerValidationError, validate_record
from core.strategy.family_registry import (
    STRATEGY_FAMILY_SOURCE,
    resolve_strategy_family,
    validate_strategy_family_name,
)


class ResearchLedgerService:
    def __init__(self, storage: LedgerStorage | None = None) -> None:
        self.storage = storage or LedgerStorage()
        self.queries = LedgerQueries(self.storage)

    def allocate_id(self, entity_type: LedgerEntityType, *, year: int) -> str:
        return self.storage.next_entity_id(entity_type, year)

    def _validate_experiment_semantics(self, record: ExperimentRecord) -> None:
        if not self.storage.exists(LedgerEntityType.HYPOTHESIS, record.hypothesis_id):
            raise LedgerValidationError(
                f"Experiment {record.entity_id} references missing hypothesis {record.hypothesis_id}"
            )
        if not self.storage.exists(LedgerEntityType.PROPOSAL, record.proposal_id):
            raise LedgerValidationError(
                f"Experiment {record.entity_id} references missing proposal {record.proposal_id}"
            )

        proposal = self.storage.read_record(LedgerEntityType.PROPOSAL, record.proposal_id)
        if not isinstance(proposal, ProposalRecord):
            raise LedgerValidationError(
                f"Proposal lookup returned unexpected record for {record.proposal_id}"
            )
        if proposal.hypothesis_id != record.hypothesis_id:
            raise LedgerValidationError(
                "Experiment hypothesis_id must match the referenced proposal hypothesis_id"
            )

        for link in record.artifact_links:
            if link.artifact_id is None:
                continue
            if not self.storage.exists(LedgerEntityType.ARTIFACT, link.artifact_id):
                raise LedgerValidationError(
                    f"Experiment {record.entity_id} references missing artifact {link.artifact_id}"
                )

    def append_record(self, record: LedgerRecordT) -> LedgerRecordT:
        validate_record(record)
        if self.storage.exists(record.entity_type, record.entity_id):
            raise FileExistsError(f"Ledger record already exists: {record.entity_id}")
        if isinstance(record, ExperimentRecord):
            self._validate_experiment_semantics(record)
        self.storage.write_record(record)
        self.refresh_indexes()
        return record

    def append_record_with_strategy_family(
        self,
        record: LedgerRecordT,
        *,
        config: dict | None = None,
        strategy_family: str | None = None,
        strategy_family_source: str = STRATEGY_FAMILY_SOURCE,
    ) -> LedgerRecordT:
        resolved_family = (
            validate_strategy_family_name(strategy_family)
            if strategy_family is not None
            else resolve_strategy_family(dict(config or {}))
        )
        tagged_metadata = dict(record.metadata)
        tagged_metadata["strategy_family"] = resolved_family
        tagged_metadata["strategy_family_source"] = strategy_family_source
        tagged_record = replace(record, metadata=tagged_metadata)
        return self.append_record(tagged_record)

    def append_hypothesis(self, record: HypothesisRecord) -> HypothesisRecord:
        return self.append_record(record)

    def append_proposal(self, record: ProposalRecord) -> ProposalRecord:
        return self.append_record(record)

    def append_experiment(self, record: ExperimentRecord) -> ExperimentRecord:
        return self.append_record(record)

    def append_artifact(self, record: ArtifactRecord) -> ArtifactRecord:
        return self.append_record(record)

    def append_governance_decision(
        self, record: GovernanceDecisionRecord
    ) -> GovernanceDecisionRecord:
        return self.append_record(record)

    def append_promotion_record(self, record: PromotionRecord) -> PromotionRecord:
        return self.append_record(record)

    def append_champion_record(self, record: ChampionRecord) -> ChampionRecord:
        return self.append_record(record)

    def refresh_indexes(self) -> dict[str, dict]:
        hypotheses = self.storage.list_records(LedgerEntityType.HYPOTHESIS)
        proposals = self.storage.list_records(LedgerEntityType.PROPOSAL)
        experiments = self.storage.list_records(LedgerEntityType.EXPERIMENT)
        artifacts = self.storage.list_records(LedgerEntityType.ARTIFACT)
        governance = self.storage.list_records(LedgerEntityType.GOVERNANCE_DECISION)
        champions = self.storage.list_records(LedgerEntityType.CHAMPION_RECORD)

        hypothesis_index = build_hypothesis_index(
            hypotheses,
            proposal_records=proposals,
            experiment_records=experiments,
        )
        experiment_index = build_experiment_index(
            experiments,
            artifact_records=artifacts,
            governance_records=governance,
        )
        champion_index = build_champion_index(champions)

        self.storage.write_index("hypothesis", hypothesis_index)
        self.storage.write_index("experiment", experiment_index)
        self.storage.write_index("champion", champion_index)
        return {
            "hypothesis_index": hypothesis_index,
            "experiment_index": experiment_index,
            "champion_index": champion_index,
        }
