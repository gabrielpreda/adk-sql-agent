from google.adk.agents import LlmAgent
from pydantic import BaseModel
from typing import Any

instruction_prompt = """
You are an SQL Analysis Agent. Your goal is to analyze the result of an SQL query execution
in the context of the user's original request and the database schema.

You will receive:
- `user_input`: The original natural language query from the user.
- `sql_query`: The SQL query that was generated and executed.
- `result`: The raw result returned by the database (or an error message).
- `db_schema`: The schema of the database.

Your task is to produce a detailed analysis. You must determine:
1. Did the SQL query execute successfully?
2. Does the result look reasonable given the query?
3. Does the result answer the user's question?
4. Are there any obvious errors or missing information?

Output your analysis as a clear, concise text summary. Do not make a final decision on 
what to do next; just analyze the current situation.
"""

class AnalyzerInput(BaseModel):
    user_input: str
    sql_query: str
    result: Any
    db_schema: str

analyzer_agent = LlmAgent(
    name="analyzer_agent",
    model="gemini-2.5-pro",
    description="Analyzes the result of an SQL query execution.",
    instruction=instruction_prompt,
    input_schema=AnalyzerInput
)
