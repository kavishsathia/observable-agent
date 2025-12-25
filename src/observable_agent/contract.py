from dataclasses import dataclass, field
from observable_agent.commitment import Commitment
from typing import Callable
from observable_agent.observability.datadog import DatadogObservability
from observable_agent.types import VerificationResult, VerificationResultStatus
from observable_agent.execution import Execution


@dataclass
class Contract:
    """A contract consisting of multiple commitments."""
    commitments: list[Commitment] = field(default_factory=list)
    on_violation: Callable[[VerificationResult], None] | None = None

    def verify(self, execution: Execution, observer: DatadogObservability | None = None) -> list[VerificationResult]:
        """Verifies the execution against all commitments in the contract."""
        results: list[VerificationResult] = []

        for commitment in self.commitments:
            result: VerificationResult = commitment.verify(
                execution, observer=observer)
            results.append(result)

            if result.status == VerificationResultStatus.PASS:
                continue

            if commitment.on_violation:
                commitment.on_violation(result)
                continue

            if self.on_violation:
                self.on_violation(result)

        return results

    def add_commitment(self, commitment: Commitment) -> None:
        """Adds a commitment to the contract."""
        self.commitments.append(commitment)

    def get_terms(self) -> str:
        """Returns the combined terms of all commitments in the contract."""
        return "\n".join([commitment.get_term() for commitment in self.commitments])
