from dataclasses import dataclass, field
from observable_agent.types import ToolCall
from google.adk.tools.base_tool import BaseTool


@dataclass
class Execution:
    name: str
    model: str
    instruction: str
    tools: list[BaseTool] = field(default_factory=list)
    description: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

    def format_tool_calls(self) -> str:
        return "\n".join([
            f"Tool: {tc.tool.name}, Args: {tc.args}, Response: {tc.tool_response}"
            for tc in self.tool_calls
        ])
