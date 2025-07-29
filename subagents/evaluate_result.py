from google.adk.agents import Agent
from pydantic import BaseModel

instruction_prompt = """
You are an SQL query result verification agent. Your role is to evaluate the correctness of the result of 
running an SQL query.

You will be given the following input fields:
- user_input: the user's original question or instruction
- sql_query: the SQL query that was generated
- result: the result returned after executing the SQL query
- db_schema: (optional) the database schema that may help with understanding context

Based on this information, decide whether the query result correctly answers the user's intent.

Just return "Correct" if the result is correct, or "Partial" if it is not.
Return only "Correct" or "Partial" — no explanation.
"""

class EvaluateResultInput(BaseModel):
    user_input: str
    sql_query: str
    result: str
    db_schema: str


evaluate_result_agent = Agent(
    name="evaluate_result",
    model="gemini-2.5-pro",
    description="Evaluate SQL query result for correctness.",
    instruction=instruction_prompt,
    input_schema=EvaluateResultInput
)