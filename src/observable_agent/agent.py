from typing import Callable
from google.adk.agents import Agent
from google.adk.tools.base_tool import BaseTool
from observable_agent.contract import Contract
from observable_agent.observability.datadog import DatadogObservability
from observable_agent.types import ToolCall
from observable_agent.execution import Execution
from observable_agent.verifier import RootVerifier
from google.adk.agents.callback_context import CallbackContext


def ObservableAgent(
    name: str,
    model: str,
    instruction: str,
    contract: Contract,
    tools: list[BaseTool] | None = None,
    description: str | None = None,
    on_tool_call: Callable[[ToolCall], None] | None = None,
    on_implementation_complete: Callable[[RootVerifier], None] | None = None,
    observer: DatadogObservability | None = None
):
    if tools is None:
        tools = []

    tool_calls: list[ToolCall] = []

    execution = Execution(
        name=name,
        model=model,
        instruction=instruction,
        tools=tools,
        description=description,
        tool_calls=tool_calls
    )

    terms = f"""
        You are bound by the following contract terms:
        {contract.get_terms()}
    """

    def _get_after_tool_callback() -> Callable[[ToolCall], None] | None:
        def append_tool_call(tool, args, tool_context, tool_response):
            tool_calls.append(ToolCall(
                tool=tool,
                args=args,
                tool_context=tool_context,
                tool_response=tool_response))

        if not on_tool_call:
            return append_tool_call

        def combined_callback(tool, args, tool_context, tool_response):
            on_tool_call(ToolCall(
                tool=tool,
                args=args,
                tool_context=tool_context,
                tool_response=tool_response))
            append_tool_call(tool, args, tool_context, tool_response)

        return combined_callback

    def _after_agent_callback(callback_context: CallbackContext = None):
        if observer:
            observer.capture_span()

        if on_implementation_complete:
            verifier = RootVerifier(
                execution=execution, contract=contract, observer=observer)
            on_implementation_complete(verifier)
        return None

    agent = Agent(
        name=name,
        model=model,
        instruction=instruction + "\n" + terms,
        description=description,
        after_tool_callback=_get_after_tool_callback(),
        after_agent_callback=_after_agent_callback,
        tools=tools
    )

    return agent
