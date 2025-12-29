from dataclasses import dataclass
from typing import Callable
from sworn.observability.observer import Observer
from sworn.types import IntermediateVerificationResult, VerificationResult, VerificationResultStatus
from sworn.execution import Execution
from sworn.verifiers.semantic_verifier import semantic_verifier
import random


@dataclass
class Commitment:
    """A commitment representing a specific term in a contract."""
    name: str
    terms: str
    verifier: Callable[[Execution, str],
                       IntermediateVerificationResult] | None = None
    semantic_sampling_rate: float = 1.0
    on_violation: Callable[[VerificationResult], None] | None = None

    def verify(self, execution: Execution, observer: Observer | None = None) -> VerificationResult:
        """
            Verifies the execution against the commitment terms and takes into account the sampling rate.
            If a deterministic verifier is provided, it is called first. If it passes and the sampling checks in,
            the semantic verifier is called. If no deterministic verifier is provided, the semantic verifier is called
            based on the sampling rate.
        """
        sampled_in = random.random() <= self.semantic_sampling_rate

        if self.verifier:
            try:
                intermediate_result = self.verifier(execution, self.terms)
            except Exception as e:
                return VerificationResult(
                    status=VerificationResultStatus.VERIFICATION_ERROR,
                    commitment_name=self.name,
                    actual=f"Verifier raised an exception: {str(e)}",
                    expected=self.terms,
                    context={}
                )

            deterministic_passed = intermediate_result.status == VerificationResultStatus.PASS
            if deterministic_passed and sampled_in:
                intermediate_result = semantic_verifier(execution, self.terms)

        elif sampled_in:
            intermediate_result = semantic_verifier(execution, self.terms)

        else:
            return VerificationResult(
                status=VerificationResultStatus.SKIPPED,
                commitment_name=self.name,
                actual="Verification skipped due to sampling rate.",
                expected="N/A",
                context={}
            )

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
            context=intermediate_result.context,
            cover=intermediate_result.cover
        )

    def get_term(self) -> str:
        """Returns the terms of the commitment."""
        return self.terms
