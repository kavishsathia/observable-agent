from sworn.types import IntermediateVerificationResult, VerificationResultStatus
from transformers import pipeline


class NLIVerifier:
    def __init__(self, model: str = "facebook/bart-large-mnli", confidence_threshold: float = 0.7):
        self.classifier = pipeline("zero-shot-classification", model=model)
        self.confidence_threshold = confidence_threshold

    def _truncate_if_needed(self, text: str, max_tokens: int = 900) -> str:
        tokens = text.split()
        if len(tokens) > max_tokens:
            return " ".join(tokens[:max_tokens]) + "... [truncated]"
        return text


def nli_verifier(execution, terms: str, confidence_threshold: float = 0.7) -> IntermediateVerificationResult:
    try:
        verifier = NLIVerifier(confidence_threshold=confidence_threshold)

        execution_summary = verifier._truncate_if_needed(execution.format())

        result = verifier.classifier(
            execution_summary,
            candidate_labels=[
                f"complies with the requirement: {terms}",
                f"violates the requirement: {terms}"
            ],
        )

        top_label = result["labels"][0]
        confidence = result["scores"][0]

        if "complies" in top_label:
            if confidence >= confidence_threshold:
                status = VerificationResultStatus.PASS
                actual = f"Execution appears compliant (confidence: {confidence:.2f})"
            else:
                status = VerificationResultStatus.WARNING
                actual = f"Uncertain compliance (confidence: {confidence:.2f})"
        else:
            if confidence >= confidence_threshold:
                status = VerificationResultStatus.VIOLATION
                actual = f"Execution appears to violate terms (confidence: {confidence:.2f})"
            else:
                status = VerificationResultStatus.WARNING
                actual = f"Uncertain violation (confidence: {confidence:.2f})"

        cover = list(range(len(execution.tool_calls)))

        return IntermediateVerificationResult(
            status=status,
            actual=actual,
            expected=terms,
            context={
                "confidence": confidence,
                "all_scores": dict(zip(result["labels"], result["scores"]))
            },
            cover=cover
        )

    except Exception as e:
        return IntermediateVerificationResult(
            status=VerificationResultStatus.VERIFICATION_ERROR,
            actual=f"NLI verification failed: {str(e)}",
            expected=terms,
            context={"error": str(e)},
            cover=[]
        )
