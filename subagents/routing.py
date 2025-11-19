from google.adk.agents import LlmAgent
from pydantic import BaseModel
from typing import Literal

routing_instruction = """
You are a Routing Agent. You check the decision from the Reflexion Agent.
- If the decision is "GO", you should output a final response to the user summarizing the answer and the raw result.
Then FORCE exiting the loop.
- If the decision is "NO-GO", you should output a message indicating that we need to retry/refine, passing the feedback along.

However, since you are in a loop, your main job is to act as the gatekeeper.
"""

class RoutingInput(BaseModel):
    decision: Literal["GO", "NO-GO"]
    feedback: str
    analysis: str

routing_agent = LlmAgent(
    name="routing_agent",
    model="gemini-2.5-pro",
    description="Routes based on Go/No-Go decision.",
    instruction=routing_instruction,
    input_schema=RoutingInput
)
