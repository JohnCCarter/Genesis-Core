"""
Attribution tracker for composable strategy POC.

Tracks component veto counts and confidence distributions to understand
which components add value.
"""

from dataclasses import dataclass


@dataclass
class ComponentStats:
    """Statistics for a single component."""

    name: str
    total_evaluations: int = 0
    veto_count: int = 0
    confidences: list[float] | None = None

    def __post_init__(self):
        if self.confidences is None:
            self.confidences = []


class AttributionTracker:
    """
    Tracks component-level statistics across multiple strategy evaluations.

    Collects veto counts and confidence distributions to identify which
    components are most restrictive and how they affect overall confidence.
    """

    def __init__(self):
        self.stats: dict[str, ComponentStats] = {}
        self.total_decisions = 0
        self.total_allowed = 0
        self.total_vetoed = 0

    def record(self, decision):
        """
        Record a strategy decision for attribution tracking.

        Args:
            decision: StrategyDecision from ComposableStrategy.evaluate()
        """
        self.total_decisions += 1

        if decision.allowed:
            self.total_allowed += 1
        else:
            self.total_vetoed += 1

        if decision.component_results is None:
            return

        for component_name, result in decision.component_results.items():
            if component_name not in self.stats:
                self.stats[component_name] = ComponentStats(name=component_name)

            stats = self.stats[component_name]
            stats.total_evaluations += 1
            stats.confidences.append(result.confidence)

            if not result.allowed:
                stats.veto_count += 1

    def get_report(self) -> str:
        """
        Generate attribution report showing component impact.

        Returns:
            Multi-line string report with statistics.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("COMPONENT ATTRIBUTION REPORT")
        lines.append("=" * 70)
        lines.append(f"Total Decisions: {self.total_decisions}")
        lines.append(f"Allowed: {self.total_allowed} ({self._pct(self.total_allowed)}%)")
        lines.append(f"Vetoed: {self.total_vetoed} ({self._pct(self.total_vetoed)}%)")
        lines.append("")

        if not self.stats:
            lines.append("No component data recorded.")
            return "\n".join(lines)

        lines.append("Component Statistics:")
        lines.append("-" * 70)

        for component_name in sorted(self.stats.keys()):
            stats = self.stats[component_name]
            lines.append(f"\n{component_name}:")
            lines.append(f"  Evaluations: {stats.total_evaluations}")
            lines.append(
                f"  Vetoes: {stats.veto_count} ({self._pct(stats.veto_count, stats.total_evaluations)}%)"
            )

            if stats.confidences:
                avg_conf = sum(stats.confidences) / len(stats.confidences)
                min_conf = min(stats.confidences)
                max_conf = max(stats.confidences)
                lines.append(
                    f"  Confidence: avg={avg_conf:.3f}, min={min_conf:.3f}, max={max_conf:.3f}"
                )

        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)

    def _pct(self, count: int, total: int | None = None) -> str:
        """Calculate percentage string."""
        if total is None:
            total = self.total_decisions
        if total == 0:
            return "0.0"
        return f"{100.0 * count / total:.1f}"
