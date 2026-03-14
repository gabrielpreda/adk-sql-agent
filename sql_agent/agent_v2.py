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

def loop_termination_callback(context: CallbackContext):
    logger.info(f"Callback for agent: {context.agent_name}")
    logger.info(f"Context state: {context.state}")
    logger.info(f"User content: {context.user_content}")

# --- Safety Validator Agent ---
safety_validation_instruction = """
You are the Safety Validation Agent. You MUST validate every user request before ANY SQL processing occurs.

Analyze the user's request to determine if it is SAFE and AUTHORIZED.

**UNAUTHORIZED OPERATIONS** (return decision="REJECT"):
- Deleting entire databases or tables (DROP DATABASE, DROP TABLE)
- Deleting records (DELETE FROM)
- Truncating tables (TRUNCATE)
- Altering database schema (ALTER TABLE, CREATE TABLE, etc.)
- Any write, update, or destructive operations
- Requests that could compromise data integrity

**AUTHORIZED OPERATIONS** (return decision="PROCEED"):
- SELECT queries (read-only operations)
- Aggregations, joins, analytical queries
- Data exploration and reporting

**Output Format**:
1. `decision`: Either "PROCEED" or "REJECT"
2. `message`: 
   - If REJECT: A complete, polite explanation to the user about why the operation is not authorized
   - If PROCEED: A brief confirmation like "Request is authorized. Proceeding with query generation..."

**CRITICAL**: 
- If you return decision="REJECT", your message will be shown to the user and the system will EXIT IMMEDIATELY.
- If you return decision="PROCEED", the system will continue to SQL generation.

**Example REJECT message**:
"I cannot perform this operation. Your request attempts to delete data from the database, which is not authorized. This system only allows read-only SELECT queries for data exploration and analysis. Please rephrase your request to query the data instead of modifying it."
"""

class SafetyValidationOutput(BaseModel):
    decision: Literal["PROCEED", "REJECT"]
    message: str

safety_validator = LlmAgent(
    name="safety_validator",
    model="gemini-2.5-pro",
    description="First-line security: validates that user requests are authorized before any SQL processing.",
    instruction=safety_validation_instruction,
    output_schema=SafetyValidationOutput
)

# --- Conditional Router Agent ---
conditional_router_instruction = """
You are a Conditional Router. You check the safety validation decision and route accordingly.

You will receive:
- `decision`: Either "PROCEED" or "REJECT"
- `message`: The message from the safety validator

**Your job**:

1. If decision is "REJECT":
   - Simply output the message to the user EXACTLY as provided
   - This is the FINAL response - add nothing more
   - Example output: "I cannot perform this operation. Your request attempts to delete data..."

2. If decision is "PROCEED":
   - Output: "Proceeding with your request..."
   - The system will continue to SQL generation

**CRITICAL**: 
- For REJECT: Output ONLY the message. This terminates the pipeline.
- For PROCEED: Output a brief confirmation. The pipeline continues.
"""

class ConditionalRouterInput(BaseModel):
    decision: Literal["PROCEED", "REJECT"]
    message: str

conditional_router = LlmAgent(
    name="conditional_router",
    model="gemini-2.5-pro",
    description="Routes based on safety decision. Terminates on REJECT, continues on PROCEED.",
    instruction=conditional_router_instruction,
    input_schema=ConditionalRouterInput
)

# --- Refinement Loop (only runs if safety check passes) ---
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

# --- Root Agent ---
# The pipeline is: safety_validator → conditional_router → refinement_loop
# If REJECT: conditional_router outputs final message, refinement_loop should not execute
# If PROCEED: conditional_router passes through, refinement_loop executes
root_agent = SequentialAgent(
    name="IterativeSQLPipeline",
    sub_agents=[
        safety_validator,      # Step 1: Validate safety
        conditional_router,    # Step 2: Route based on decision  
        refinement_loop        # Step 3: Only should run if PROCEED
    ],  
    description="Security-first SQL agent: validates safety, then processes authorized requests."
)
