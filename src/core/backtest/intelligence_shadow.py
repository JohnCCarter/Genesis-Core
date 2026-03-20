from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.intelligence.collection import (
    CollectionRequest,
    DeterministicIntelligenceCollector,
)
from core.intelligence.evaluation import DeterministicIntelligenceEvaluator
from core.intelligence.events.models import (
    IntelligenceEvent,
    IntelligenceReference,
    JsonObject,
    json_dumps_stable,
)
from core.intelligence.features import DeterministicIntelligenceFeatureExtractor
from core.intelligence.ledger_adapter import DeterministicIntelligenceLedgerAdapter
from core.intelligence.normalization import DeterministicIntelligenceNormalizer
from core.intelligence.parameter import (
    ApprovedParameterSet,
    DeterministicParameterIntelligenceAnalyzer,
)
from core.research_ledger import ResearchLedgerService
from core.research_ledger.storage import LedgerStorage
from core.research_orchestrator import (
    DeterministicResearchOrchestrator,
    ResearchTask,
)
from core.strategy.family_registry import STRATEGY_FAMILY_SOURCE, resolve_strategy_family

_SHADOW_SOURCE = "champion_shadow"
_SHADOW_TOPIC = "regime_shadow"
_SIGNAL_TYPE = "decision_observation"
_SEGMENT_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_segment(value: str) -> str:
    sanitized = _SEGMENT_PATTERN.sub("-", str(value).strip()).strip("-")
    return sanitized or "unknown"


def _stable_json_clone(payload: dict[str, Any]) -> JsonObject:
    return json.loads(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def _stable_fingerprint(payload: dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _normalize_timestamp(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    iso = getattr(value, "isoformat", None)
    if callable(iso):
        return str(iso())
    return str(value)


def _extract_confidence(result: dict[str, Any]) -> float:
    raw_confidence = (result or {}).get("confidence")
    if isinstance(raw_confidence, dict):
        for key in ("overall", "buy", "sell"):
            value = raw_confidence.get(key)
            if value is None:
                continue
            try:
                return max(0.0, min(1.0, float(value)))
            except (TypeError, ValueError):
                continue
        return 0.0
    try:
        return max(0.0, min(1.0, float(raw_confidence)))
    except (TypeError, ValueError):
        return 0.0


def _extract_reasons(meta: dict[str, Any]) -> tuple[str, ...]:
    decision = (meta or {}).get("decision") or {}
    reasons = decision.get("reasons") or ()
    if not isinstance(reasons, list | tuple):
        return ()
    return tuple(str(item) for item in reasons)


def _extract_size(meta: dict[str, Any]) -> float:
    decision = (meta or {}).get("decision") or {}
    raw_size = decision.get("size", 0.0)
    try:
        return float(raw_size)
    except (TypeError, ValueError):
        return 0.0


def derive_shadow_run_id(summary_path: Path) -> str:
    if summary_path.stem == "shadow_summary" and summary_path.parent.name:
        return summary_path.parent.name
    return _sanitize_segment(summary_path.stem)


def derive_shadow_ledger_root(*, repo_root: Path, run_id: str) -> Path:
    return repo_root / "artifacts" / "intelligence_shadow" / run_id / "research_ledger"


def derive_shadow_parameter_set(
    *,
    symbol: str,
    timeframe: str,
    merged_config: dict[str, Any],
    effective_config_fingerprint: str | None,
) -> ApprovedParameterSet:
    config_payload = _stable_json_clone(merged_config)
    fingerprint = effective_config_fingerprint or _stable_fingerprint(config_payload)
    return ApprovedParameterSet(
        parameter_set_id=f"champion-shadow-{fingerprint[:16]}",
        parameters=config_payload,
        sensitivity_score=0.5,
        stability_score=0.5,
        consistency_score=0.5,
        source_ledger_entity_ids=(),
        baseline_weight=1.0,
        risk_multiplier=1.0,
    )


@dataclass(slots=True)
class BacktestIntelligenceShadowRecorder:
    symbol: str
    timeframe: str
    repo_root: Path
    events: list[IntelligenceEvent] = field(default_factory=list)

    def _build_event(
        self,
        *,
        result: dict[str, Any],
        meta: dict[str, Any],
        candles: dict[str, Any],
    ) -> IntelligenceEvent:
        timestamps = candles.get("timestamp") or []
        timestamp_value = timestamps[-1] if timestamps else None
        timestamp = _normalize_timestamp(timestamp_value)
        bar_index = candles.get("bar_index")
        action = str((result or {}).get("action") or "NONE").strip().upper() or "NONE"
        reasons = _extract_reasons(meta)
        size = _extract_size(meta)
        row_id = f"{self.symbol}|{self.timeframe}|{bar_index}"
        summary = (
            f"Champion shadow observation action={action};"
            f"size={size:.6f};"
            f"reasons={';'.join(reasons) if reasons else 'NONE'}"
        )
        return IntelligenceEvent(
            event_id=(
                f"shadow-{_sanitize_segment(self.symbol)}-"
                f"{_sanitize_segment(self.timeframe)}-{int(bar_index):06d}"
            ),
            source=_SHADOW_SOURCE,
            timestamp=timestamp,
            asset=self.symbol,
            topic=_SHADOW_TOPIC,
            signal_type=_SIGNAL_TYPE,
            confidence=_extract_confidence(result),
            references=(IntelligenceReference(kind="backtest_row", ref=row_id, label=action),),
            summary=summary,
        )

    def create_hook(self, *, upstream_hook: Any | None):
        def hook(result: dict[str, Any], meta: dict[str, Any], candles: dict[str, Any]):
            if upstream_hook is not None:
                result, meta = upstream_hook(result, meta, candles)

            safe_result = result if isinstance(result, dict) else {}
            safe_meta = meta if isinstance(meta, dict) else {}
            safe_candles = candles if isinstance(candles, dict) else {}
            self.events.append(
                self._build_event(result=safe_result, meta=safe_meta, candles=safe_candles)
            )
            return result, meta

        return hook

    def finalize(
        self,
        *,
        results: dict[str, Any],
        merged_config: dict[str, Any],
        summary_path: Path,
    ) -> dict[str, Any]:
        if not self.events:
            raise ValueError("intelligence shadow produced no events")

        summary_path.parent.mkdir(parents=True, exist_ok=True)
        run_id = derive_shadow_run_id(summary_path)
        ledger_root = derive_shadow_ledger_root(repo_root=self.repo_root, run_id=run_id)
        ledger_root.mkdir(parents=True, exist_ok=True)

        backtest_info = (results or {}).get("backtest_info") or {}
        effective_config_fingerprint = backtest_info.get("effective_config_fingerprint")
        approved_parameter_set = derive_shadow_parameter_set(
            symbol=self.symbol,
            timeframe=self.timeframe,
            merged_config=merged_config,
            effective_config_fingerprint=(
                str(effective_config_fingerprint) if effective_config_fingerprint else None
            ),
        )
        collection_request = CollectionRequest(
            source=_SHADOW_SOURCE,
            asset=self.symbol,
            topic=_SHADOW_TOPIC,
        )
        task = ResearchTask(
            task_id=f"champion-shadow-{run_id}",
            collection_request=collection_request,
            approved_parameter_sets=(approved_parameter_set,),
        )
        service = ResearchLedgerService(LedgerStorage(root=ledger_root))
        strategy_family = resolve_strategy_family(merged_config)
        orchestrator = DeterministicResearchOrchestrator(
            collector=DeterministicIntelligenceCollector(events=tuple(self.events)),
            normalizer=DeterministicIntelligenceNormalizer(),
            feature_extractor=DeterministicIntelligenceFeatureExtractor(),
            evaluator=DeterministicIntelligenceEvaluator(),
            parameter_analyzer=DeterministicParameterIntelligenceAnalyzer(),
            ledger_adapter=DeterministicIntelligenceLedgerAdapter(
                service=service,
                strategy_config=merged_config,
                strategy_family=strategy_family,
            ),
        )
        research_result = orchestrator.run(task)

        summary: dict[str, Any] = {
            "shadow_status": "completed",
            "run_id": run_id,
            "decision_drift_observed": False,
            "advisory_only": True,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "summary_path": str(summary_path),
            "ledger_root": str(ledger_root),
            "collection_request": {
                "source": collection_request.source,
                "asset": collection_request.asset,
                "topic": collection_request.topic,
            },
            "backtest": {
                "start_date": backtest_info.get("start_date"),
                "end_date": backtest_info.get("end_date"),
                "bars_processed": backtest_info.get("bars_processed"),
                "warmup_bars": backtest_info.get("warmup_bars"),
                "seed": backtest_info.get("seed"),
                "git_hash": backtest_info.get("git_hash"),
                "effective_config_fingerprint": effective_config_fingerprint,
            },
            "derived_parameter_set": {
                "strategy_family": strategy_family,
                "strategy_family_source": STRATEGY_FAMILY_SOURCE,
                "parameter_set_id": approved_parameter_set.parameter_set_id,
                "parameter_count": len(approved_parameter_set.parameters),
                "baseline_weight": approved_parameter_set.baseline_weight,
                "risk_multiplier": approved_parameter_set.risk_multiplier,
                "scores": {
                    "sensitivity": approved_parameter_set.sensitivity_score,
                    "stability": approved_parameter_set.stability_score,
                    "consistency": approved_parameter_set.consistency_score,
                },
            },
            "counts": {
                "captured_events": len(self.events),
                "collected_events": len(research_result.stage_outputs.collected_events),
                "normalized_events": len(research_result.stage_outputs.normalized_events),
                "feature_sets": len(research_result.stage_outputs.feature_sets),
                "evaluations": len(research_result.stage_outputs.evaluations),
                "parameter_recommendations": len(
                    research_result.stage_outputs.parameter_recommendations
                ),
            },
            "recommended_parameter_set_ids": list(research_result.recommended_parameter_set_ids),
            "preferred_parameter_set_ids": list(research_result.preferred_parameter_set_ids),
            "top_advisory_parameter_set_id": research_result.top_advisory_parameter_set_id,
            "persisted_event_ids": list(
                research_result.stage_outputs.persistence_result.persisted_event_ids
            ),
            "ledger_entity_ids": list(
                research_result.stage_outputs.persistence_result.ledger_entity_ids
            ),
        }
        summary_path.write_text(json_dumps_stable(summary), encoding="utf-8")
        return summary
