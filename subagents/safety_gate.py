from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from pydantic import BaseModel
from typing import Literal, Optional

from subagents.rewrite_prompt import rewrite_prompt_agent
from subagents.generator import generator_agent
from subagents.analyzer import analyzer_agent
from subagents.reflexion import reflexion_agent
from subagents.routing import routing_agent

# Safety validation instruction
safety_validation_instruction = """
You are the Safety Validation and Routing Agent. You are the FIRST agent in the pipeline.

**STEP 1: Safety Validation**

Analyze the user's request to determine if it is SAFE and AUTHORIZED.

**UNAUTHORIZED OPERATIONS** (must be rejected):
- Deleting entire databases or tables (DROP DATABASE, DROP TABLE)
- Deleting all records from tables (DELETE FROM without specific WHERE clause)
- Truncating tables (TRUNCATE)
- Altering database schema (ALTER TABLE, CREATE TABLE, etc.)
- Any administrative or destructive operations
- Requests that could compromise data integrity

**AUTHORIZED OPERATIONS** (can proceed):
- SELECT queries (read-only operations)
- Queries with specific WHERE clauses that limit scope
- Aggregations, joins, and analytical queries
- Data exploration and reporting

**STEP 2: Decision and Response**

Based on your analysis:

**If UNAUTHORIZED (NO-GO)**:
- Set `authorized` to False
- Provide a complete, polite, user-facing message explaining:
  - What operation was requested
  - Why it is not authorized  
  - What types of operations are allowed

Example: "I cannot perform this operation. Your request attempts to delete the entire database, which is not authorized for security reasons. This system only allows read-only SELECT queries for data exploration and analysis. Please rephrase your request to query the data instead of modifying it."

**If AUTHORIZED (GO)**:
- Set `authorized` to True
- Provide a brief message like: "Request authorized. Processing your query..."

**CRITICAL**: 
- If `authorized` is False, your message is the FINAL response to the user. The system will NOT proceed further.
- If `authorized` is True, the system will continue to generate and execute the SQL query.
"""

class SafetyGateOutput(BaseModel):
    authorized: bool
    message: str

safety_gate_agent = LlmAgent(
    name="safety_gate_agent",
    model="gemini-2.5-pro",
    description="Validates request safety and authorizes or rejects before any SQL processing.",
    instruction=safety_validation_instruction,
    output_schema=SafetyGateOutput
)
