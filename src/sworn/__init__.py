"""
Sworn: Contract-based verification for AI agents.

A framework for defining behavioral contracts and verifying AI agent compliance
using both deterministic and semantic (LLM-based) verification. Integrates with
Datadog for observability and supports progressive hardening from semantic to
deterministic verifiers as failure modes are discovered.
"""

from sworn.contract import Contract
from sworn.commitment import Commitment
from sworn.execution import Execution
from sworn.types import VerificationResult, VerificationResultStatus, ToolCall, IntermediateVerificationResult
from sworn.observability.observer import Observer
from sworn.observability.datadog import DatadogObservability

__all__ = [
    "Contract",
    "Commitment",
    "Execution",
    "VerificationResult",
    "IntermediateVerificationResult",
    "VerificationResultStatus",
    "ToolCall",
    "Observer",
    "DatadogObservability",
]
