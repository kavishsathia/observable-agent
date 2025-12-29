import pytest
from unittest.mock import Mock, patch
from sworn import contract
from sworn.commitment import Commitment
from sworn.types import VerificationResultStatus, IntermediateVerificationResult
from sworn.execution import Execution
from sworn.contract import Contract


@pytest.fixture
def mock_execution():
    """Create a fake execution."""
    execution = Mock(spec=Execution)
    execution.format.return_value = "tool1(arg1) -> result1"
    execution.tool_calls = []
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


class TestContractVerify:
    def test_all_commitments_pass(self, mock_execution, passing_verifier):
        commitmentA = Commitment(
            name="test1",
            terms="do the thing",
            verifier=passing_verifier,
            semantic_sampling_rate=0
        )
        commitmentB = Commitment(
            name="test2",
            terms="do another thing",
            verifier=passing_verifier,
            semantic_sampling_rate=0
        )
        contract = Contract(commitments=[commitmentA, commitmentB])
        results = contract._verify(mock_execution)
        assert all(result.status ==
                   VerificationResultStatus.PASS for result in results)

    def test_commitment_violation_triggers_on_violation(self, mock_execution, failing_verifier):
        on_violation = Mock()

        commitment = Commitment(
            name="test1",
            terms="do the thing",
            verifier=failing_verifier,
            on_violation=on_violation
        )

        contract = Contract(commitments=[commitment])
        results = contract._verify(mock_execution)
        assert results[0].status == VerificationResultStatus.VIOLATION
        on_violation.assert_called_once()

    def test_commitment_violation_triggers_on_violation_when_contract_violation_exists(self, mock_execution, failing_verifier):
        on_violation = Mock()

        commitment = Commitment(
            name="test1",
            terms="do the thing",
            verifier=failing_verifier,
            on_violation=on_violation
        )

        contract = Contract(
            commitments=[commitment], on_violation=on_violation)
        results = contract._verify(mock_execution)
        assert results[0].status == VerificationResultStatus.VIOLATION
        on_violation.assert_called_once()

    def test_contract_violation_triggers_on_violation_when_commitment_violation_doesnt_exist(self, mock_execution, failing_verifier):
        on_violation = Mock()

        commitment = Commitment(
            name="test1",
            terms="do the thing",
            verifier=failing_verifier,
        )

        contract = Contract(
            commitments=[commitment], on_violation=on_violation)
        results = contract._verify(mock_execution)
        assert results[0].status == VerificationResultStatus.VIOLATION
        on_violation.assert_called_once()
