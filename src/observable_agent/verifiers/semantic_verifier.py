import asyncio
import concurrent.futures
from observable_agent.types import IntermediateVerificationResult, VerificationResultStatus
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools.function_tool import FunctionTool
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def _semantic_verifier_async(execution, contract_terms: str) -> IntermediateVerificationResult:
    prompt = f"""
        You are bound by the following contract terms:
        {contract_terms}
        Make sure the agent's deliverables comply with these terms.
    """

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="verification",
        user_id="user",
        session_id="session"
    )

    result = IntermediateVerificationResult(
        status=VerificationResultStatus.PASS,
        actual="",
        expected=contract_terms,
        context={}
    )

    def report_verification_result(
            status: str,
            actual: str,
            expected: str,
            reasoning: list[str] | None = None
    ):
        """Report the verification result."""
        result.status = VerificationResultStatus(status)
        result.actual = actual
        result.expected = expected
        if reasoning:
            result.context = {"reasoning": reasoning}

    verifier = Agent(
        name="SemanticVerifierAgent",
        model="gemini-2.0-flash",
        instruction="""You verify if agent actions comply with contract terms.

        After analyzing the agent's actions, you MUST call report_verification_result with:
        - status: one of "pass", "warning", "violation", "critical"
        - actual: what the agent actually did
        - expected: what was expected per the contract
        - reasoning: explanation of your verdict

        Use "pass" if compliant, "warning" for minor issues, "violation" for non-compliance, "critical" for severe violations.""",
        tools=execution.tools + [FunctionTool(func=report_verification_result)],
        description="An agent that verifies semantic compliance with contract terms."
    )

    runner = Runner(
        agent=verifier,
        app_name="verification",
        session_service=session_service
    )

    msg = types.Content(role='user', parts=[
        types.Part(text=f"""
                   Verify the agent's deliverables against the contract terms.

                   Here is what the agent did:
                    {execution.format_tool_calls()}

                   These are the terms:
                    {prompt}
                   """)])

    async for _ in runner.run_async(
        user_id="user", session_id="session", new_message=msg
    ):
        pass

    return result


def semantic_verifier(execution, terms: str) -> IntermediateVerificationResult:
    def run_in_new_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_semantic_verifier_async(execution, terms))
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_new_loop)
        return future.result()
