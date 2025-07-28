import os
import logging
import asyncio
import uuid
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part



from sql_agent.sql_agent import root_agent as sql_agent
from dotenv import load_dotenv

load_dotenv()


APP_NAME = "adk-sql-agent"
USER_ID = os.getenv("USER_ID", "user")
SESSION_ID = str(uuid.uuid4())

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)


app = FastAPI()
runner: Runner = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    history: list[str] = []




def build_content_from_history_and_query(query: str, history: List[str]) -> Content:
    parts = []

    # Include the history as prior messages
    for h in history:
        # optionally split "User: ...\nAgent: ..." if needed
        if "User:" in h and "Agent:" in h:
            user_part = h.split("User:")[1].split("Agent:")[0].strip()
            agent_part = h.split("Agent:")[1].strip()
            parts.append(Part(text=user_part))
            parts.append(Part(text=agent_part))
        else:
            parts.append(Part(text=h))

    # Add the current query
    parts.append(Part(text=query))

    return Content(role="user", parts=parts)


@app.on_event("startup")
async def init_runner():
    """
    Init runner
    Args:  
        None
    Returns:
        None
    """
    global runner
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
    runner = Runner(
        agent=sql_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    logger.info("Runner initialized and session created.")

@app.post("/query")
async def process_query(req: QueryRequest):

    global runner

    content = build_content_from_history_and_query(query=req.query, 
                                                   history=req.history)
    
    response_text = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text += event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
    logger.info("System response: {response_text}")
    return {"response_text": response_text}