from typing import Any, Dict
from enum import Enum
from dataclasses import dataclass
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool


class VerificationResultStatus(Enum):
    """Enumeration of verification result statuses."""
    PASS = "pass"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"
    SKIPPED = "skipped"
    VERIFICATION_ERROR = "verification_error"


@dataclass
class VerificationResult:
    """Final verification result after all checks."""
    status: VerificationResultStatus
    commitment_name: str
    actual: str
    expected: str
    context: Dict[str, Any] | None = None


@dataclass
class IntermediateVerificationResult:
    """Intermediate result from a verifier before finalizing."""
    status: VerificationResultStatus
    actual: str
    expected: str
    context: Dict[str, Any] | None = None


@dataclass
class ToolCall:
    """Represents a tool call made by the agent."""
    tool: BaseTool
    args: Dict[str, Any]
    tool_context: ToolContext
    tool_response: Dict
