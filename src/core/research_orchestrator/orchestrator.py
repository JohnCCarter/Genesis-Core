from __future__ import annotations

from dataclasses import dataclass

from core.intelligence.collection.interface import IntelligenceCollector
from core.intelligence.evaluation.interface import IntelligenceEvaluator
from core.intelligence.features.interface import IntelligenceFeatureExtractor
from core.intelligence.ledger_adapter.interface import IntelligenceLedgerAdapter
from core.intelligence.normalization.interface import IntelligenceNormalizer
from core.intelligence.parameter.interface import ParameterIntelligenceAnalyzer
from core.research_orchestrator.models import ResearchResult, ResearchTask
from core.research_orchestrator.workflow import orchestrate_research_task


@dataclass(frozen=True, slots=True)
class DeterministicResearchOrchestrator:
    collector: IntelligenceCollector
    normalizer: IntelligenceNormalizer
    feature_extractor: IntelligenceFeatureExtractor
    evaluator: IntelligenceEvaluator
    parameter_analyzer: ParameterIntelligenceAnalyzer
    ledger_adapter: IntelligenceLedgerAdapter

    def run(self, task: ResearchTask) -> ResearchResult:
        return orchestrate_research_task(
            task,
            collector=self.collector,
            normalizer=self.normalizer,
            feature_extractor=self.feature_extractor,
            evaluator=self.evaluator,
            parameter_analyzer=self.parameter_analyzer,
            ledger_adapter=self.ledger_adapter,
        )
