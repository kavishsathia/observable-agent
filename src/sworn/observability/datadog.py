from ddtrace.llmobs import LLMObs
from sworn.observability.observer import Observer


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
        except Exception as e:
            pass
