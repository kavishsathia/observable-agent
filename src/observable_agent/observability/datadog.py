from ddtrace.llmobs import LLMObs


class DatadogObservability:
    def __init__(self):
        self._span_context = None

    def __enter__(self):
        LLMObs.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        LLMObs.flush()

    def capture_span(self) -> None:
        self._span_context = LLMObs.export_span(span=None)

    def submit_evaluation(self, label: str, value: str, reasoning: str) -> None:
        span_context = self._span_context or LLMObs.export_span(span=None)
        print(span_context)
        LLMObs.submit_evaluation(
            span=span_context,
            label=label,
            metric_type="categorical",
            value=value,
            tags={"type": "custom"},
            assessment="pass" if value == "pass" else None if value == "skipped" else "fail",
            reasoning=reasoning,
        )
