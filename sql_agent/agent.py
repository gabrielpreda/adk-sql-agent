from google.adk.agents import SequentialAgent, LoopAgent, LlmAgent
from pydantic import BaseModel
from typing import Literal

from subagents.rewrite_prompt import rewrite_prompt_agent
from subagents.generator import generator_agent
from subagents.analyzer import analyzer_agent
from subagents.reflexion import reflexion_agent
from subagents.routing import routing_agent

from google.adk.agents.callback_context import CallbackContext
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# STEP 1: SAFETY CHECK - Validate if request is secure
# ============================================================================

safety_check_instruction = """
You are the Safety Check Agent. Your ONLY job is to determine if a user request is SECURE or NOT SECURE.

**NOT SECURE (Unauthorized Operations)**:
- Deleting databases/tables: DROP DATABASE, DROP TABLE
- Deleting records: DELETE FROM
- Truncating tables: TRUNCATE
- Schema modifications: ALTER TABLE, CREATE TABLE, CREATE DATABASE
- Data modifications: INSERT INTO, UPDATE
- Administrative operations: GRANT, REVOKE
- Any destructive or write operations

**SECURE (Authorized Operations)**:
- SELECT queries (read-only)
- Aggregations: COUNT, SUM, AVG, MIN, MAX
- Joins, filtering, grouping
- Data exploration and analytical queries

**Output**:
- `is_secure`: true or false
- `reason`: Brief explanation

Examples:
- "delete entire database" → is_secure: false, reason: "Attempts to delete database"
- "show me top 10 books" → is_secure: true, reason: "Read-only SELECT query"
"""

class SafetyCheckOutput(BaseModel):
    is_secure: bool
    reason: str

safety_check_agent = LlmAgent(
    name="safety_check_agent",
    model="gemini-2.5-pro",
    description="Determines if request is secure or not.",
    instruction=safety_check_instruction,
    output_schema=SafetyCheckOutput
)

# ============================================================================
# STEP 2: SECURITY ROUTER - Exit immediately if not secure, continue if secure
# ============================================================================

security_router_instruction = """
You are the Security Router. You receive the security check result and route accordingly.

**Input**:
- `is_secure`: boolean
- `reason`: explanation from safety check
- `user_input`: original user request

**Your Decision**:

1. **If is_secure = false (NOT SECURE)**:
   - Output a FINAL rejection message to the user
   - Be polite and explain why the operation is not authorized
   - Mention that only read-only SELECT queries are allowed
   - This is the END - no further processing will occur
   
   Example: "I cannot perform this operation. Your request attempts to delete the entire database, which is not authorized for security reasons. This system only allows read-only SELECT queries for data exploration and analysis."

2. **If is_secure = true (SECURE)**:
   - Output: "Security check passed. Proceeding with your request..."
   - The system will continue to SQL generation and execution

**CRITICAL**: 
- NOT SECURE → Your message is the FINAL response, system exits
- SECURE → System continues to refinement loop
"""

class SecurityRouterInput(BaseModel):
    is_secure: bool
    reason: str
    user_input: str

security_router_agent = LlmAgent(
    name="security_router_agent",
    model="gemini-2.5-pro",
    description="Routes based on security: exits on not secure, continues on secure.",
    instruction=security_router_instruction,
    input_schema=SecurityRouterInput
)

# ============================================================================
# STEP 3: REFINEMENT LOOP - Only executes if request is secure
# ============================================================================

refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[
        rewrite_prompt_agent,
        generator_agent,
        analyzer_agent,
        reflexion_agent,
        routing_agent
    ],
    max_iterations=2,
)

# ============================================================================
# ROOT AGENT - Three-step pipeline
# ============================================================================
# 
# Architecture:
#   1. safety_check_agent: Checks if request is secure → {is_secure: bool}
#   2. security_router_agent: Routes based on security
#      - If NOT secure → Outputs rejection message and EXITS
#      - If secure → Outputs "proceeding..." and CONTINUES
#   3. refinement_loop: SQL generation and execution (only if secure)
#
# Note: Due to SequentialAgent behavior, all agents execute in sequence.
# However, the security_router outputs a terminal message on NOT SECURE,
# and the refinement loop will receive that as input and should handle it gracefully.

root_agent = SequentialAgent(
    name="SecureSQLPipeline",
    sub_agents=[
        safety_check_agent,      # Step 1: Check security
        security_router_agent,   # Step 2: Route (exit or continue)
        refinement_loop          # Step 3: Process query (if secure)
    ],  
    description="Security-first SQL agent: checks security, routes accordingly, processes if authorized."
)

