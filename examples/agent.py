from dotenv import load_dotenv
load_dotenv()

from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from observable_agent.verifiers.semantic_verifier import semantic_verifier
from observable_agent import DatadogObservability
from observable_agent import ObservableAgent, Contract, Commitment


def write_file(filename: str, content: str) -> dict:
    """Write content to a file."""
    print(f"[TOOL] Writing to {filename}: {content[:50]}...")
    return {"status": "success", "filename": filename}


def on_complete(verifier):
    print("\n" + "=" * 50)
    print("VERIFICATION RESULTS")
    print("=" * 50)
    results = verifier.verify()
    for result in results:
        print(f"Commitment: {result.commitment_name}")
        print(f"Status: {result.status}")
        print(f"Expected: {result.expected}")
        print(f"Actual: {result.actual}")
        print(f"Context: {result.context}")
    print("=" * 50)


write_tool = FunctionTool(func=write_file)

contract = Contract()
contract.add_commitment(Commitment(
    name="file_naming_policy",
    terms="You must save reports to a file named 'report.txt'",
    semantic_sampling_rate=1.0
))
contract.add_commitment(Commitment(
    name="content_policy",
    terms="The report must include year-over-year comparison data",
    semantic_sampling_rate=1.0
))


async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="demo",
        user_id="user",
        session_id="session"
    )

    with DatadogObservability() as obs:
        root_agent = ObservableAgent(
            name="ReportWriter",
            model="gemini-2.0-flash",
            instruction="You are a report writing assistant. When asked to write a report, use the write_file tool to save it.",
            description="An agent that writes reports to files",
            contract=contract,
            tools=[write_tool],
            on_implementation_complete=on_complete,
            observer=obs
        )

        runner = Runner(
            agent=root_agent,
            app_name="demo",
            session_service=session_service
        )

        msg = types.Content(role='user', parts=[
            types.Part(
                text="Write a brief Q3 financial summary report and save it.")
        ])

        print("Running agent...")
        async for event in runner.run_async(
            user_id="user", session_id="session", new_message=msg
        ):
            if hasattr(event, 'content') and event.content:
                print(f"Agent: {event.content}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
