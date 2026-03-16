from __future__ import annotations

from core.research_ledger.enums import ChampionStatus, ExperimentStatus, LedgerEntityType
from core.research_ledger.models import ChampionRecord, ExperimentRecord, JsonObject, record_to_dict
from core.research_ledger.storage import LedgerStorage


class LedgerQueries:
    def __init__(self, storage: LedgerStorage) -> None:
        self.storage = storage

    def list_experiments(
        self,
        *,
        hypothesis_id: str | None = None,
        proposal_id: str | None = None,
        status: ExperimentStatus | None = None,
    ) -> list[ExperimentRecord]:
        experiments = self.storage.list_records(LedgerEntityType.EXPERIMENT)
        filtered: list[ExperimentRecord] = []
        for experiment in experiments:
            if hypothesis_id is not None and experiment.hypothesis_id != hypothesis_id:
                continue
            if proposal_id is not None and experiment.proposal_id != proposal_id:
                continue
            if status is not None and experiment.status != status:
                continue
            filtered.append(experiment)
        return sorted(filtered, key=lambda item: item.entity_id)

    def list_champions(
        self,
        *,
        symbol: str | None = None,
        timeframe: str | None = None,
        status: ChampionStatus | None = None,
    ) -> list[ChampionRecord]:
        champions = self.storage.list_records(LedgerEntityType.CHAMPION_RECORD)
        filtered: list[ChampionRecord] = []
        for champion in champions:
            if symbol is not None and champion.symbol != symbol:
                continue
            if timeframe is not None and champion.timeframe != timeframe:
                continue
            if status is not None and champion.status != status:
                continue
            filtered.append(champion)
        return sorted(filtered, key=lambda item: (item.symbol, item.timeframe, item.entity_id))

    def get_hypothesis_lineage(self, hypothesis_id: str) -> JsonObject:
        hypotheses = self.storage.list_records(LedgerEntityType.HYPOTHESIS)
        proposals = self.storage.list_records(LedgerEntityType.PROPOSAL)
        experiments = self.storage.list_records(LedgerEntityType.EXPERIMENT)
        artifacts = self.storage.list_records(LedgerEntityType.ARTIFACT)
        governance = self.storage.list_records(LedgerEntityType.GOVERNANCE_DECISION)
        promotions = self.storage.list_records(LedgerEntityType.PROMOTION_RECORD)
        champions = self.storage.list_records(LedgerEntityType.CHAMPION_RECORD)

        hypothesis = next(record for record in hypotheses if record.entity_id == hypothesis_id)
        proposal_records = [record for record in proposals if record.hypothesis_id == hypothesis_id]
        experiment_records = [
            record for record in experiments if record.hypothesis_id == hypothesis_id
        ]
        experiment_ids = {record.entity_id for record in experiment_records}
        artifact_records = [
            artifact for artifact in artifacts if artifact.experiment_id in experiment_ids
        ]
        governance_records = [
            decision
            for decision in governance
            if decision.subject_id in experiment_ids or decision.subject_id == hypothesis_id
        ]
        governance_ids = {record.entity_id for record in governance_records}
        promotion_records = [
            promotion
            for promotion in promotions
            if promotion.subject_experiment_id in experiment_ids
            or promotion.governance_decision_id in governance_ids
        ]
        promotion_ids = {record.entity_id for record in promotion_records}
        champion_records = [
            champion for champion in champions if champion.promotion_record_id in promotion_ids
        ]

        return {
            "hypothesis": record_to_dict(hypothesis),
            "proposals": [
                record_to_dict(record)
                for record in sorted(proposal_records, key=lambda x: x.entity_id)
            ],
            "experiments": [
                record_to_dict(record)
                for record in sorted(experiment_records, key=lambda x: x.entity_id)
            ],
            "artifacts": [
                record_to_dict(record)
                for record in sorted(artifact_records, key=lambda x: x.entity_id)
            ],
            "governance_decisions": [
                record_to_dict(record)
                for record in sorted(governance_records, key=lambda x: x.entity_id)
            ],
            "promotion_records": [
                record_to_dict(record)
                for record in sorted(promotion_records, key=lambda x: x.entity_id)
            ],
            "champion_records": [
                record_to_dict(record)
                for record in sorted(champion_records, key=lambda x: x.entity_id)
            ],
        }
