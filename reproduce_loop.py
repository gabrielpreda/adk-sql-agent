import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from sql_agent.agent import root_agent

logging.basicConfig(level=logging.INFO)

async def run_test():
    session_service = InMemorySessionService()
    session_id = "test_session"
    await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id=session_id,
    )
    
    runner = Runner(
        agent=root_agent,
        app_name="test_app",
        session_service=session_service,
    )
    
    # Query that should succeed (assuming db_tools is fixed)
    query = "Count the number of books."
    content = Content(role="user", parts=[Part(text=query)])
    
    print("Starting run...")
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session_id,
        new_message=content
    ):
        pass # Just consume events
    print("Run finished.")

if __name__ == "__main__":
    asyncio.run(run_test())
