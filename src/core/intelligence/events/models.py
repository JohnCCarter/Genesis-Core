from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


def json_dumps_stable(payload: JsonObject) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(frozen=True, slots=True)
class IntelligenceReference:
    kind: str
    ref: str
    label: str | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> IntelligenceReference:
        return cls(
            kind=str(payload.get("kind", "")),
            ref=str(payload.get("ref", "")),
            label=(str(payload["label"]) if payload.get("label") is not None else None),
        )

    def to_payload(self) -> JsonObject:
        return {
            "kind": str(self.kind),
            "label": (str(self.label) if self.label is not None else None),
            "ref": str(self.ref),
        }


@dataclass(frozen=True, slots=True)
class IntelligenceEvent:
    event_id: str
    source: str
    timestamp: str
    asset: str
    topic: str
    signal_type: str
    confidence: float
    references: tuple[IntelligenceReference, ...] = ()
    summary: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> IntelligenceEvent:
        references_raw = payload.get("references") or []
        return cls(
            event_id=str(payload.get("event_id", "")),
            source=str(payload.get("source", "")),
            timestamp=str(payload.get("timestamp", "")),
            asset=str(payload.get("asset", "")),
            topic=str(payload.get("topic", "")),
            signal_type=str(payload.get("signal_type", "")),
            confidence=float(payload.get("confidence", 0.0)),
            references=tuple(
                IntelligenceReference.from_payload(item)
                for item in references_raw
                if isinstance(item, dict)
            ),
            summary=str(payload.get("summary", "")),
        )

    def to_payload(self) -> JsonObject:
        return {
            "asset": str(self.asset),
            "confidence": float(self.confidence),
            "event_id": str(self.event_id),
            "references": [reference.to_payload() for reference in self.references],
            "signal_type": str(self.signal_type),
            "source": str(self.source),
            "summary": str(self.summary),
            "timestamp": str(self.timestamp),
            "topic": str(self.topic),
        }

    def to_json(self) -> str:
        return json_dumps_stable(self.to_payload())


@dataclass(frozen=True, slots=True)
class ValidatedIntelligenceEvent:
    event: IntelligenceEvent
    validator_version: str = "intelligence_event.v1"

    def to_payload(self) -> JsonObject:
        return {
            "event": self.event.to_payload(),
            "validator_version": str(self.validator_version),
        }
