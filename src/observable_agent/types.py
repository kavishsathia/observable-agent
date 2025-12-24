from typing import Any, Dict
from enum import Enum
from dataclasses import dataclass
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool


class VerificationResultStatus(Enum):
    PASS = "pass"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"
    SKIPPED = "skipped"


@dataclass
class VerificationResult:
    status: VerificationResultStatus
    commitment_name: str
    actual: str
    expected: str
    context: Dict[str, Any] | None = None


@dataclass
class IntermediateVerificationResult:
    status: VerificationResultStatus
    actual: str
    expected: str
    context: Dict[str, Any] | None = None


@dataclass
class ToolCall:
    tool: BaseTool
    args: Dict[str, Any]
    tool_context: ToolContext
    tool_response: Dict
