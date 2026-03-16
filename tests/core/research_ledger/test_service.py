from __future__ import annotations

from pathlib import Path

import pytest

from core.research_ledger.enums import (
    ArtifactKind,
    ChampionStatus,
    GovernanceDecisionKind,
    LedgerEntityType,
    PromotionTargetKind,
)
from core.research_ledger.models import (
    ArtifactRecord,
    ChampionRecord,
    ExperimentRecord,
    GovernanceDecisionRecord,
    HypothesisRecord,
    IntelligenceRef,
    PromotionRecord,
    ProposalRecord,
)
from core.research_ledger.service import ResearchLedgerService
from core.research_ledger.storage import LedgerStorage


def _service(tmp_path: Path) -> ResearchLedgerService:
    return ResearchLedgerService(LedgerStorage(root=tmp_path / "artifacts" / "research_ledger"))


def test_append_record_refreshes_indexes_and_lineage(tmp_path: Path) -> None:
    service = _service(tmp_path)

    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Ledger lineage",
        hypothesis="Append-only lineage should stay queryable.",
        intelligence_refs=(
            IntelligenceRef(
                module="regime_intelligence",
                ref_kind="artifact_metadata",
                label="ri-proof",
            ),
        ),
    )
    proposal = ProposalRecord(
        entity_id="PROP-2026-0001",
        entity_type=LedgerEntityType.PROPOSAL,
        created_at="2026-03-16T12:05:00+00:00",
        hypothesis_id=hypothesis.entity_id,
        title="Phase B proposal",
        summary="Run a deterministic 1h RI comparison.",
        command_packet_path="docs/governance/templates/command_packet.md",
    )
    experiment = ExperimentRecord(
        entity_id="EXP-2026-0001",
        entity_type=LedgerEntityType.EXPERIMENT,
        created_at="2026-03-16T12:10:00+00:00",
        hypothesis_id=hypothesis.entity_id,
        proposal_id=proposal.entity_id,
        title="1h RI vs OFF",
        objective="Validate canonical Phase B on 1h.",
        metrics={"score": 0.1126, "profit_factor": 1.41},
    )
    artifact = ArtifactRecord(
        entity_id="ART-2026-0001",
        entity_type=LedgerEntityType.ARTIFACT,
        created_at="2026-03-16T12:15:00+00:00",
        experiment_id=experiment.entity_id,
        artifact_kind=ArtifactKind.RESULT_SUMMARY,
        path="results/hparam_search/run_20260316_123000/best_trial.json",
    )
    governance = GovernanceDecisionRecord(
        entity_id="GOV-2026-0001",
        entity_type=LedgerEntityType.GOVERNANCE_DECISION,
        created_at="2026-03-16T12:20:00+00:00",
        subject_type=LedgerEntityType.EXPERIMENT,
        subject_id=experiment.entity_id,
        decision=GovernanceDecisionKind.ACCEPTED,
        rationale="Experiment is traceable and passes gates.",
    )
    promotion = PromotionRecord(
        entity_id="PROMO-2026-0001",
        entity_type=LedgerEntityType.PROMOTION_RECORD,
        created_at="2026-03-16T12:25:00+00:00",
        subject_experiment_id=experiment.entity_id,
        governance_decision_id=governance.entity_id,
        target_kind=PromotionTargetKind.CHAMPION,
        target_ref="config/strategy/champions/tBTCUSD_1h.json",
        source_artifact_id=artifact.entity_id,
    )
    champion = ChampionRecord(
        entity_id="CHAMP-2026-0001",
        entity_type=LedgerEntityType.CHAMPION_RECORD,
        created_at="2026-03-16T12:30:00+00:00",
        symbol="tBTCUSD",
        timeframe="1h",
        promotion_record_id=promotion.entity_id,
        governance_decision_id=governance.entity_id,
        experiment_id=experiment.entity_id,
        artifact_id=artifact.entity_id,
        config_path="config/strategy/champions/tBTCUSD_1h.json",
        status=ChampionStatus.ACTIVE,
    )

    service.append_hypothesis(hypothesis)
    service.append_proposal(proposal)
    service.append_experiment(experiment)
    service.append_artifact(artifact)
    service.append_governance_decision(governance)
    service.append_promotion_record(promotion)
    service.append_champion_record(champion)

    lineage = service.queries.get_hypothesis_lineage(hypothesis.entity_id)
    assert lineage["hypothesis"]["entity_id"] == "HYP-2026-0001"
    assert [item["entity_id"] for item in lineage["proposals"]] == ["PROP-2026-0001"]
    assert [item["entity_id"] for item in lineage["experiments"]] == ["EXP-2026-0001"]
    assert [item["entity_id"] for item in lineage["artifacts"]] == ["ART-2026-0001"]
    assert [item["entity_id"] for item in lineage["promotion_records"]] == ["PROMO-2026-0001"]
    assert [item["entity_id"] for item in lineage["champion_records"]] == ["CHAMP-2026-0001"]

    hypothesis_index = service.storage.read_index("hypothesis")
    experiment_index = service.storage.read_index("experiment")
    champion_index = service.storage.read_index("champion")
    assert hypothesis_index["items"][0]["proposal_ids"] == ["PROP-2026-0001"]
    assert experiment_index["items"][0]["artifact_ids"] == ["ART-2026-0001"]
    assert champion_index["items"][0]["symbol"] == "tBTCUSD"


def test_append_record_rejects_duplicate_ids(tmp_path: Path) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Duplicate",
        hypothesis="Duplicate IDs must fail.",
    )

    service.append_hypothesis(hypothesis)
    with pytest.raises(FileExistsError, match="HYP-2026-0001"):
        service.append_hypothesis(hypothesis)


def test_allocate_id_is_storage_state_deterministic(tmp_path: Path) -> None:
    service = _service(tmp_path)

    assert service.allocate_id(LedgerEntityType.HYPOTHESIS, year=2026) == "HYP-2026-0001"
    service.append_hypothesis(
        HypothesisRecord(
            entity_id="HYP-2026-0001",
            entity_type=LedgerEntityType.HYPOTHESIS,
            created_at="2026-03-16T12:00:00+00:00",
            title="First",
            hypothesis="First",
        )
    )
    assert service.allocate_id(LedgerEntityType.HYPOTHESIS, year=2026) == "HYP-2026-0002"
