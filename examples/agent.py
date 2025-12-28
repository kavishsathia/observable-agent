from sworn import Contract, Commitment
from sworn import DatadogObservability
from sworn.verifiers.semantic_verifier import semantic_verifier
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent
from google.genai import types
from dotenv import load_dotenv
load_dotenv()


observer = DatadogObservability()
contract = Contract(observer=observer)
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


@contract.actuator
def write_file(filename: str, content: str) -> dict:
    """Write content to a file."""
    print(f"[TOOL] Writing to {filename}: {content[:50]}...")
    return {"status": "success", "filename": filename}


def on_complete(verifier):
    pass


write_tool = FunctionTool(func=write_file)


async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="demo",
        user_id="user",
        session_id="session"
    )

    with contract.execution() as execution:
        root_agent = Agent(
            name="ReportWriter",
            model="gemini-2.0-flash",
            instruction="You are a report writing assistant. When asked to write a report, use the write_file tool to save it.",
            description="An agent that writes reports to files",
            tools=[write_tool],
        )
        runner = Runner(
            agent=root_agent,
            app_name="demo",
            session_service=session_service
        )

        msg = types.Content(role='user', parts=[
            types.Part(
                text="Write a brief Q3 financial summary report and save it to report.txt. Make up the numbers.")
        ])

        print("Running agent...")
        async for event in runner.run_async(
            user_id="user", session_id="session", new_message=msg
        ):
            if hasattr(event, 'content') and event.content:
                print(f"Agent: {event.content}")

        print(execution.format_tool_calls())
        results = execution.verify()
        print(f"Verification results: {results}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
