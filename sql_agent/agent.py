from google.adk.agents import SequentialAgent, LoopAgent

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

# --- Refinement Loop ---
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
root_agent = SequentialAgent(
    name="IterativeSQLPipeline",
    sub_agents=[
        refinement_loop
    ],  
    description="Iteratively rephrases, generates, analyzes, and refines SQL queries."
)
