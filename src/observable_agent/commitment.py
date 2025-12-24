from dataclasses import dataclass
from typing import Callable
from observable_agent.observability.datadog import DatadogObservability
from observable_agent.types import IntermediateVerificationResult, VerificationResult, VerificationResultStatus
from observable_agent.execution import Execution
from observable_agent.verifiers.semantic_verifier import semantic_verifier
import random


@dataclass
class Commitment:
    name: str
    terms: str
    verifier: Callable[[Execution, str],
                       IntermediateVerificationResult] | None = None
    semantic_sampling_rate: float = 1.0
    on_violation: Callable[[VerificationResult], None] | None = None

    def verify(self, execution: Execution, observer: DatadogObservability | None = None) -> VerificationResult:
        if not self.verifier and random.random() > self.semantic_sampling_rate:
            return VerificationResult(
                status=VerificationResultStatus.SKIPPED,
                commitment_name=self.name,
                actual="Verification skipped due to sampling rate.",
                expected="N/A",
                context={}
            )

        if not self.verifier:
            verifier = semantic_verifier
        else:
            verifier = self.verifier

        intermediate_result = verifier(execution, self.terms)

        if observer:
            observer.submit_evaluation(
                label=self.name,
                value=intermediate_result.status.value,
                reasoning=f"""
Expected: {intermediate_result.expected}
Actual: {intermediate_result.actual}
Context: {intermediate_result.context}
"""
            )

        return VerificationResult(
            status=intermediate_result.status,
            commitment_name=self.name,
            actual=intermediate_result.actual,
            expected=intermediate_result.expected,
            context=intermediate_result.context
        )

    def get_term(self) -> str:
        return self.terms
