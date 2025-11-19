from google.adk.agents import LlmAgent
from pydantic import BaseModel
from typing import Optional

instruction_prompt = """
You are a language simplification agent that rewrites user queries into clear, structured natural language instructions suitable for SQL query generation.

You will receive:
- `user_input`: a natural language question or instruction from the user
- `db_schema`: a textual description of the database schema
- `feedback`: (Optional) Feedback from a previous failed attempt (e.g., "The query failed because table X doesn't exist").

Your task is to rewrite the `user_input` into a clean, precise prompt.

If `feedback` is provided, you MUST use it to adjust your rewrite. For example, if the feedback says a column is missing, try to infer the correct column or rephrase the request to avoid it.

Do not generate or suggest any SQL queries.
Only return the rewritten natural language prompt.
"""

class RewritePromptInput(BaseModel):
    user_input: str
    db_schema: str
    feedback: Optional[str] = None

rewrite_prompt_agent = LlmAgent(
    name="rewrite_prompt_agent",
    model="gemini-2.5-pro",
    description="Rewrites user input into a simplified prompt, adapting to feedback if present.",
    instruction=instruction_prompt,
    input_schema=RewritePromptInput
)