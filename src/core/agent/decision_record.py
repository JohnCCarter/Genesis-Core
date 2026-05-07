from __future__ import annotations

import datetime as dt
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LOG_PATH = REPO_ROOT / "logs" / "agent_decisions.jsonl"
SCHEMA_VERSION = "v1"


def canonical_hash(payload: Any) -> str:
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def candles_hash(candles: dict[str, Any]) -> str:
    closes = candles.get("close") or []
    return canonical_hash({"n": len(closes), "tail": list(closes[-5:])})


def _decision_id() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S%f")


@dataclass(slots=True)
class DecisionRecord:
    ts_utc: str
    symbol: str
    trend_tf: str
    entry_tf: str
    candles_hash: dict[str, str]
    params_hash: str
    fib_signal: dict[str, Any]
    risk_check: dict[str, Any]
    submission: dict[str, Any] | None = None
    schema_version: str = SCHEMA_VERSION
    decision_id: str = field(default_factory=_decision_id)


def append_decision(
    record: DecisionRecord | dict[str, Any],
    *,
    path: Path | None = None,
) -> Path:
    target = path or DEFAULT_LOG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = record if isinstance(record, dict) else asdict(record)
    line = json.dumps(payload, separators=(",", ":"), default=str) + "\n"
    with open(target, "a", encoding="utf-8") as f:
        f.write(line)
    return target


def append_followup(
    *,
    decision_id: str,
    submission: dict[str, Any],
    path: Path | None = None,
) -> Path:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "decision_id": decision_id,
        "kind": "submission_followup",
        "ts_utc": dt.datetime.now(dt.UTC).isoformat(),
        "submission": submission,
    }
    return append_decision(payload, path=path)


def read_decisions(
    *,
    path: Path | None = None,
    limit: int = 50,
    symbol: str | None = None,
    decision_id: str | None = None,
) -> list[dict[str, Any]]:
    target = path or DEFAULT_LOG_PATH
    if not target.exists():
        return []
    out: list[dict[str, Any]] = []
    with open(target, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if symbol and rec.get("symbol") != symbol:
                continue
            if decision_id and rec.get("decision_id") != decision_id:
                continue
            out.append(rec)
    return out[-limit:]


def find_decision(
    decision_id: str,
    *,
    path: Path | None = None,
) -> dict[str, Any] | None:
    target = path or DEFAULT_LOG_PATH
    if not target.exists():
        return None
    with open(target, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("decision_id") == decision_id and rec.get("kind") != "submission_followup":
                return rec
    return None
