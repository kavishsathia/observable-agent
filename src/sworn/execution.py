from dataclasses import dataclass, field
from contextvars import ContextVar, Token
from typing import TYPE_CHECKING, Any

from sworn.types import ToolCall, VerificationResult

if TYPE_CHECKING:
    from sworn.contract import Contract
    from sworn.observability.observer import Observer

_context_execution: ContextVar["Execution"] = ContextVar("execution")


@dataclass
class Execution:
    _contract: "Contract"
    tool_calls: list[ToolCall] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    _token: Token["Execution"] | None = field(default=None, init=False, repr=False)

    def __enter__(self) -> "Execution":
        self._token = _context_execution.set(self)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if self._token is not None:
            _context_execution.reset(self._token)
            self._token = None
        return False

    def verify(self, observer: "Observer | None" = None) -> list[VerificationResult]:
        """Verify this execution against its contract's commitments."""
        return self._contract._verify(self, observer)

    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Manually add a tool call to this execution."""
        self.tool_calls.append(tool_call)

    def add_context(self, context: str) -> None:
        """Add context information to this execution."""
        self.context.append(context)

    def format(self) -> str:
        """Formats the execution context and tool calls for logging or display purposes."""
        context_str = "\n".join(self.context)
        tool_calls_str = "\n".join([
            f"[{i}] Tool: {tc.tool_name}, Args: {tc.args}, Response: {tc.tool_response}"
            for i, tc in enumerate(self.tool_calls)
        ])
        return f"===Context===\n{context_str}\n===Execution===\n{tool_calls_str}"
