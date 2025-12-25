"""
Observable Agent: Contract-based verification for AI agents.

A framework for defining behavioral contracts and verifying AI agent compliance
using both deterministic and semantic (LLM-based) verification. Integrates with
Datadog for observability and supports progressive hardening from semantic to
deterministic verifiers as failure modes are discovered.
"""

from observable_agent.agent import ObservableAgent
from observable_agent.contract import Contract
from observable_agent.commitment import Commitment
from observable_agent.types import VerificationResult, VerificationResultStatus, ToolCall, IntermediateVerificationResult
from observable_agent.verifier import RootVerifier
from observable_agent.observability.datadog import DatadogObservability

__all__ = [
    "ObservableAgent",
    "Contract",
    "Commitment",
    "VerificationResult",
    "IntermediateVerificationResult",
    "VerificationResultStatus",
    "ToolCall",
    "RootVerifier",
    "DatadogObservability",
]
