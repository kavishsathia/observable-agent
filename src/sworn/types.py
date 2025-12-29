from typing import Any, Dict, Literal
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


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
    cover: list[int] = field(default_factory=list)


@dataclass
class IntermediateVerificationResult:
    """Intermediate result from a verifier before finalizing."""
    status: VerificationResultStatus
    actual: str
    expected: str
    context: Dict[str, Any] | None = None
    cover: list[int] = field(default_factory=list)


@dataclass
class ToolContext:
    """Contextual information about a tool call."""
    started_at: datetime
    ended_at: datetime
    duration_ms: float


@dataclass
class ToolCall:
    """Represents a tool call made by the agent."""
    tool_name: str
    function: Literal["sensor", "actuator"]
    args: Dict[str, Any]
    tool_context: ToolContext
    tool_response: Any
    error: Exception | None
