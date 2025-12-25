from dataclasses import dataclass

from observable_agent.observability.datadog import DatadogObservability
from observable_agent.types import VerificationResult

from observable_agent.execution import Execution
from observable_agent.contract import Contract


@dataclass
class RootVerifier:
    """A root verifier that verifies an execution against a contract."""
    execution: Execution
    contract: Contract
    observer: DatadogObservability | None = None

    def verify(self) -> list[VerificationResult]:
        """Verifies the execution against the contract."""
        return self.contract.verify(self.execution, observer=self.observer)
