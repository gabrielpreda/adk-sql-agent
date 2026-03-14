from google.adk.agents import LlmAgent
from pydantic import BaseModel
from typing import Literal

routing_instruction = """
You are a Safety Decision Router. You receive the safety validation decision and route accordingly.

You will receive:
- `decision`: Either "GO" or "NO-GO" from the Safety Validator
- `reason`: The explanation from the Safety Validator
- `user_input`: The original user request

**Your task**:

1. If decision is "NO-GO":
   - Output the `reason` directly to the user as your final response
   - This is a TERMINAL response - the system will exit immediately
   - Do NOT suggest alternatives or try to help further
   - Simply deliver the security message

2. If decision is "GO":
   - Output a brief message like "Security check passed. Processing your request..."
   - The system will continue to the SQL generation pipeline

**CRITICAL**: 
- For NO-GO: Your output IS the final user-facing message. Make it clear and professional.
- For GO: Your output is just a status update. The actual query results will come later.

**Example NO-GO response**:
"I cannot perform this operation. Your request attempts to delete the entire database, which is not authorized for security reasons. This system only allows read-only SELECT queries for data exploration and analysis."

**Example GO response**:
"Security check passed. Processing your query..."
"""

class SafetyDecisionInput(BaseModel):
    decision: Literal["GO", "NO-GO"]
    reason: str
    user_input: str

safety_decision_router = LlmAgent(
    name="safety_decision_router",
    model="gemini-2.5-pro",
    description="Routes based on safety validation decision. Exits immediately on NO-GO.",
    instruction=routing_instruction,
    input_schema=SafetyDecisionInput
)
