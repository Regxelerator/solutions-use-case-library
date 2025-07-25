from agents import ToolCallOutputItem, RunResult
from agent_library.critic_agent import create_critic_agent

_CRITIC = create_critic_agent()

async def _evaluation_json(run: RunResult) -> str:
    return run.final_output.model_dump_json()

critic_tool = _CRITIC.as_tool(
    tool_name="critic_tool",
    tool_description=("""
        Run style guide and factual checks on a draft outputs; returns an evaluation JSON string.
        """
    ),
    custom_output_extractor=_evaluation_json
)
