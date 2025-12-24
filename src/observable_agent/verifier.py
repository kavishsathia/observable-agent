from dataclasses import dataclass

from observable_agent.observability.datadog import DatadogObservability
from observable_agent.types import VerificationResult

from observable_agent.execution import Execution
from observable_agent.contract import Contract


@dataclass
class RootVerifier:
    execution: Execution
    contract: Contract
    observer: DatadogObservability | None = None

    def verify(self) -> list[VerificationResult]:
        return self.contract.verify(self.execution, observer=self.observer)
