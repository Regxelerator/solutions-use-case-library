from agents import Agent
from agentic_flow_memo_feedback.schemas import SectionDraft
from agentic_flow_memo_feedback.agent_config_loader import load_agent_config
from agentic_flow_memo_creation.tools.content_loader import content_loader
from agentic_flow_memo_creation.tools.critic_tool import critic_tool

_TOOLS = {
    "content_loader": content_loader,
    "critic_tool": critic_tool,
}

def create_section_refiner_agent() -> Agent:
    cfg = load_agent_config("Section Refiner Agent")
    tools = [_TOOLS[t] for t in cfg.get("tools", [])]

    return Agent(
        name=cfg["name"],
        model=cfg["model"],
        instructions=cfg["instructions"],
        tools=tools,
        output_type=SectionDraft,
    )


def get_section_refiner_tool():
    return create_section_refiner_agent().as_tool(
        tool_name="section_refinement_tool",
        tool_description=(
            "Refines a single memo section so that it incorporates the user’s "
            "feedback and passes a quality review.  Returns a SectionDraft."
        ),
    )
