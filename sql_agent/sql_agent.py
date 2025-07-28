from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from functions.db_tools import get_schema_tool
from functions.db_tools  import run_sql_query_tool
from subagents.evaluate_result import evaluate_result_agent

instruction_prompt = """
You are an SQL query agent specialized in interpreting user input, generating an SQL query, run it, evaluate the response, and return the query result
and a summary.

Ypu have access to two Functions and one Agent Tool:
    - 'get_schema_tool'
    - 'run_sql_query_tool'
    - 'evaluate_result_agent'


- Use `get_schema_tool` to retrieve the SQL database schema. 
    This would be the first action typically.
    Use `get_schema_tool` Function Tool without an input or  with input: {"table": "<table_name>"}  

After that, using the user input and the database schema, generate an sql query
- Use `run_sql_query_tool` to run the sql query you generated.
    Use this tool once you generated an sql query.
    Use `run_sql_query_tool` Function Tool with input: {"query": "<sql>"}  

- Use `evaluate_result_agent` Agent Tool to validate if the result obtained by running the query. 
    With this tool, evaluate if the result is consistent with the user input, the database schema, the sql query generated, and the result of runing the sql query.
   Use `evaluate_result_agent` with the following input fields:
    {
    "user_input": "<original user question>",
    "sql_query": "<the SQL query you generated>",
    "result": "<the result returned from running the query>",
    "schema": "<the database schema used to generate the query>"
    }

    Call this agent only after running the SQL query. It will return "OK" if the result is correct, or "KO" if not.

- Do not ask the user for confirmation before calling the tools.

# OUTPUT
Return a JSON with the sql query, raw result, summary, and the evaluation of the result.

The raw result is the result of running the generated sql query.
The summary is a description in natural language of the result of running the query.
The evaluation of the result is the `evaluate_result_agent` output
Allways return a JSON, even if sql query, summary, or evaluation failed.
Only perform one iteration of 'get_schema_tool', 'run_sql_query_tool' function calls.

Respond in JSON:
    {{
        "summary": str,
        "sql": str,
        "raw_result": str,
        "result_evaluation": str
    }}
"""

root_agent = Agent(
    name="sql_query_agent",
    model="gemini-2.5-pro",
    description="From user input in natural language, generate an SQL query, run it, evaluate the response, and return the query result, and a summary",
    instruction=instruction_prompt,
    tools=[
        get_schema_tool,
        run_sql_query_tool,
        AgentTool(agent=evaluate_result_agent)
    ]
)