from google.adk.agents import LlmAgent
from pydantic import BaseModel
from typing import Literal

instruction_prompt = """
You are a Reflexion & Decision Agent. Your goal is to review the analysis of an SQL query execution and decide whether to proceed or retry.

You will receive:
- `user_input`: The user's original request.
- `analysis`: The analysis provided by the Analyzer Agent.
- `past_history`: (Optional) Summary of previous attempts.

Your output must include:
1. `decision`: Either "GO" (success) or "NO-GO" (failure/needs refinement).
2. `feedback`: If "NO-GO", provide specific instructions on what to fix (e.g., "The query failed because table X does not exist. Try using table Y."). If "GO", provide a final polite summary for the user.

Constraints:
- If the analysis says the result is correct and answers the question, output "GO".
- If there is an error or the result is wrong, output "NO-GO".
"""

class ReflexionInput(BaseModel):
    user_input: str
    analysis: str

class ReflexionOutput(BaseModel):
    decision: Literal["GO", "NO-GO"]
    feedback: str

reflexion_agent = LlmAgent(
    name="reflexion_agent",
    model="gemini-2.5-pro",
    description="Decides whether to accept the result or retry based on analysis.",
    instruction=instruction_prompt,
    input_schema=ReflexionInput,
    output_schema=ReflexionOutput
)
