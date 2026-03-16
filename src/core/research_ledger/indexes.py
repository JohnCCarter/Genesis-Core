from __future__ import annotations

from core.research_ledger.enums import LedgerEntityType
from core.research_ledger.models import (
    ChampionRecord,
    ExperimentRecord,
    HypothesisRecord,
    JsonObject,
)


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted(set(values))


def build_hypothesis_index(
    hypotheses: list[HypothesisRecord],
    *,
    proposal_records: list,
    experiment_records: list,
) -> JsonObject:
    items: list[JsonObject] = []
    for hypothesis in sorted(hypotheses, key=lambda item: item.entity_id):
        proposal_ids = [
            proposal.entity_id
            for proposal in proposal_records
            if proposal.hypothesis_id == hypothesis.entity_id
        ]
        experiment_ids = [
            experiment.entity_id
            for experiment in experiment_records
            if experiment.hypothesis_id == hypothesis.entity_id
        ]
        items.append(
            {
                "entity_id": hypothesis.entity_id,
                "created_at": hypothesis.created_at,
                "status": str(hypothesis.status),
                "title": hypothesis.title,
                "proposal_ids": _sorted_unique(proposal_ids),
                "experiment_ids": _sorted_unique(experiment_ids),
            }
        )
    return {
        "schema_version": "research_ledger.v1",
        "entity_type": "hypothesis",
        "items": items,
    }


def build_experiment_index(
    experiments: list[ExperimentRecord],
    *,
    artifact_records: list,
    governance_records: list,
) -> JsonObject:
    items: list[JsonObject] = []
    for experiment in sorted(experiments, key=lambda item: item.entity_id):
        artifact_ids = [
            artifact.entity_id
            for artifact in artifact_records
            if artifact.experiment_id == experiment.entity_id
        ]
        governance_ids = [
            decision.entity_id
            for decision in governance_records
            if decision.subject_type == LedgerEntityType.EXPERIMENT
            and decision.subject_id == experiment.entity_id
        ]
        items.append(
            {
                "entity_id": experiment.entity_id,
                "created_at": experiment.created_at,
                "status": str(experiment.status),
                "hypothesis_id": experiment.hypothesis_id,
                "proposal_id": experiment.proposal_id,
                "artifact_ids": _sorted_unique(artifact_ids),
                "governance_ids": _sorted_unique(governance_ids),
            }
        )
    return {
        "schema_version": "research_ledger.v1",
        "entity_type": "experiment",
        "items": items,
    }


def build_champion_index(champions: list[ChampionRecord]) -> JsonObject:
    items: list[JsonObject] = []
    for champion in sorted(
        champions, key=lambda item: (item.symbol, item.timeframe, item.entity_id)
    ):
        items.append(
            {
                "entity_id": champion.entity_id,
                "created_at": champion.created_at,
                "symbol": champion.symbol,
                "timeframe": champion.timeframe,
                "status": str(champion.status),
                "promotion_record_id": champion.promotion_record_id,
                "predecessor_champion_id": champion.predecessor_champion_id,
            }
        )
    return {
        "schema_version": "research_ledger.v1",
        "entity_type": "champion",
        "items": items,
    }
