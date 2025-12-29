from ddtrace.llmobs import LLMObs
from sworn.observability.observer import Observer
from sworn.types import ToolCall


class DatadogObservability(Observer):
    """Datadog observability integration for capturing spans and submitting evaluations."""

    def __init__(self):
        self._span_context = None
        LLMObs.enable()

    def capture_span(self) -> None:
        """Captures a new span context for evaluations."""
        self._span_context = LLMObs.export_span(span=None)

    def submit_evaluation(self, label: str, value: str, reasoning: str) -> None:
        """Submits an evaluation metric to Datadog."""
        try:
            span_context = self._span_context or LLMObs.export_span(span=None)
            LLMObs.submit_evaluation(
                span=span_context,
                label=label,
                metric_type="categorical",
                value=value,
                tags={"type": "custom"},
                assessment="pass" if value == "pass" else None if value == "skipped" or value == "verification_error" else "fail",
                reasoning=reasoning,
            )
        except Exception:
            pass

    def submit_coverage(self, covered: list[ToolCall], uncovered: list[ToolCall]) -> None:
        """Submits coverage information to Datadog."""
        try:
            span_context = self._span_context or LLMObs.export_span(span=None)
            total = len(covered) + len(uncovered)
            coverage_pct = len(covered) / total * 100 if total > 0 else 100
            covered_names = [tc.tool_name for tc in covered]
            uncovered_names = [tc.tool_name for tc in uncovered]
            LLMObs.submit_evaluation(
                span=span_context,
                label="contract_coverage",
                metric_type="score",
                value=coverage_pct,
                tags={"type": "coverage"},
                reasoning=f"Covered: {covered_names}, Uncovered: {uncovered_names}",
            )
        except Exception:
            pass
