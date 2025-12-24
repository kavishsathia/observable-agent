from dataclasses import dataclass, field
from observable_agent.commitment import Commitment
from typing import Callable
from observable_agent.observability.datadog import DatadogObservability
from observable_agent.types import VerificationResult, VerificationResultStatus
from observable_agent.execution import Execution


@dataclass
class Contract:
    commitments: list[Commitment] = field(default_factory=list)
    on_violation: Callable[[VerificationResult], None] | None = None

    def verify(self, execution: Execution, observer: DatadogObservability | None = None) -> list[VerificationResult]:
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
        self.commitments.append(commitment)

    def get_terms(self) -> str:
        return "\n".join([commitment.get_term() for commitment in self.commitments])
