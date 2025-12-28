from abc import ABC, abstractmethod


class Observer(ABC):
    """Abstract base class for observability integrations."""

    @abstractmethod
    def capture_span(self) -> None:
        """Captures a span context for evaluations."""
        pass

    @abstractmethod
    def submit_evaluation(self, label: str, value: str, reasoning: str) -> None:
        """Submits an evaluation metric."""
        pass
