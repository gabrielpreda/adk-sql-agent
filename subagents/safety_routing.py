from google.adk.agents import LlmAgent
from pydantic import BaseModel
from typing import Literal

routing_instruction = """
You are a Safety Routing Agent. You check the decision from the Safety Validator Agent.

- If the decision is "GO", you should pass control to the next agent to continue processing.
- If the decision is "NO-GO", you MUST immediately output a final response to the user explaining that the request is not authorized, and FORCE EXIT the entire pipeline.

Your response should be clear and professional, explaining why the operation cannot be performed.

**CRITICAL**: When you receive a "NO-GO" decision, you MUST exit immediately. Do not allow any further processing.
"""

class SafetyRoutingInput(BaseModel):
    decision: Literal["GO", "NO-GO"]
    reason: str
    user_input: str

safety_routing_agent = LlmAgent(
    name="safety_routing_agent",
    model="gemini-2.5-pro",
    description="Routes based on safety validation decision and exits immediately if unauthorized.",
    instruction=routing_instruction,
    input_schema=SafetyRoutingInput
)
