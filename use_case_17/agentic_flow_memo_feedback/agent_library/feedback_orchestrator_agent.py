import json
from agents import Agent
from agentic_flow_memo_feedback.schemas import DraftSections
from agentic_flow_memo_feedback.agent_config_loader import load_agent_config
from agentic_flow_memo_feedback.agent_library.section_refiner_agent import (
    get_section_refiner_tool,
)

_TOOLS = {
    "section_refinement_tool": get_section_refiner_tool(),
}

def create_feedback_orchestrator_agent() -> Agent:
    cfg = load_agent_config("Feedback Orchestrator Agent")
    tools = [_TOOLS[t] for t in cfg.get("tools", [])]

    return Agent(
        name=cfg["name"],
        model=cfg["model"],
        instructions=cfg["instructions"],
        tools=tools,
        output_type=DraftSections
    )
