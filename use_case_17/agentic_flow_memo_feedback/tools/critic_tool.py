from agents import RunResult           
from agentic_flow_memo_creation.agent_library.critic_agent import (
    create_critic_agent,
)

_CRITIC = create_critic_agent()

async def _evaluation_json(run: RunResult) -> str:
    return run.final_output.model_dump_json()

critic_tool = _CRITIC.as_tool(
    tool_name="critic_tool",
    tool_description=(
        "Run style‑guide and factual checks on draft outputs; "
        "returns an Evaluation_Report JSON string."
    ),
    custom_output_extractor=_evaluation_json,
)