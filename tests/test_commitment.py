import pytest
from unittest.mock import Mock, patch
from sworn.commitment import Commitment
from sworn.types import VerificationResultStatus, IntermediateVerificationResult


@pytest.fixture
def mock_execution():
    """Create a fake execution."""
    execution = Mock()
    execution.format_tool_calls.return_value = "tool1(arg1) -> result1"
    return execution


@pytest.fixture
def passing_verifier():
    """A verifier that always passes."""
    return lambda exec, terms: IntermediateVerificationResult(
        status=VerificationResultStatus.PASS,
        actual="did the thing",
        expected="do the thing",
        context={}
    )


@pytest.fixture
def failing_verifier():
    """A verifier that always fails."""
    return lambda exec, terms: IntermediateVerificationResult(
        status=VerificationResultStatus.VIOLATION,
        actual="did something else",
        expected="do the thing",
        context={}
    )


class TestCommitmentVerify:
    def test_uses_deterministic_verifier_when_provided(self, mock_execution, failing_verifier):
        commitment = Commitment(
            name="test",
            terms="do the thing",
            verifier=failing_verifier
        )
        result = commitment.verify(mock_execution)
        assert result.status == VerificationResultStatus.VIOLATION

    @patch('sworn.commitment.random.random', return_value=0.9)
    def test_skips_semantic_verifier_when_deterministic_verifier_passes_but_sampled_out(self, mock_random, mock_execution, passing_verifier):
        commitment = Commitment(
            name="test",
            terms="do the thing",
            verifier=passing_verifier,
            semantic_sampling_rate=0.5
        )
        result = commitment.verify(mock_execution)
        assert result.status == VerificationResultStatus.PASS

    @patch('sworn.commitment.random.random', return_value=0.1)
    @patch('sworn.commitment.semantic_verifier', return_value=IntermediateVerificationResult(
        status=VerificationResultStatus.VIOLATION,
        actual="did the thing",
        expected="do the thing",
        context={}
    ))
    def test_uses_semantic_verifier_when_deterministic_verifier_passes_and_sampled_in(self, mock_semantic_verifier, mock_random, mock_execution, passing_verifier):
        commitment = Commitment(
            name="test",
            terms="do the thing",
            verifier=passing_verifier,
            semantic_sampling_rate=0.5
        )
        result = commitment.verify(mock_execution)
        assert result.status == VerificationResultStatus.VIOLATION

    @patch('sworn.commitment.random.random', return_value=0.9)
    def test_skips_semantic_verifier_when_no_deterministic_and_sampled_out(self, mock_random, mock_execution):
        commitment = Commitment(
            name="test",
            terms="do the thing",
            semantic_sampling_rate=0.5
        )
        result = commitment.verify(mock_execution)
        assert result.status == VerificationResultStatus.SKIPPED

    @patch('sworn.commitment.random.random', return_value=0.1)
    @patch('sworn.commitment.semantic_verifier', return_value=IntermediateVerificationResult(
        status=VerificationResultStatus.VIOLATION,
        actual="did the thing",
        expected="do the thing",
        context={}
    ))
    def test_calls_semantic_verifier_when_no_deterministic_and_sampled_in(self, mock_semantic_verifier, mock_random, mock_execution):
        commitment = Commitment(
            name="test",
            terms="do the thing",
            semantic_sampling_rate=0.5
        )
        result = commitment.verify(mock_execution)
        assert result.status == VerificationResultStatus.VIOLATION


class TestCommitmentGetTerm:
    def test_returns_terms(self):
        commitment = Commitment(name="test", terms="must do X")
        assert commitment.get_term() == "must do X"
