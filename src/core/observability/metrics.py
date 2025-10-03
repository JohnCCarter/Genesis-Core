import time
from typing import Any


class Metrics:
    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.gauges: dict[str, float] = {}
        self.events: list[dict] = []

    def inc(self, name: str, value: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = float(value)

    def event(self, name: str, payload: dict[str, Any] | None = None) -> None:
        self.events.append({"ts": int(time.time()), "name": name, "payload": payload or {}})


metrics = Metrics()


def get_dashboard() -> dict:
    return {
        "counters": dict(metrics.counters),
        "gauges": dict(metrics.gauges),
        "events": metrics.events[-100:],
    }
