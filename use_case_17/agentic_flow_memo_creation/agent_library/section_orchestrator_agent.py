from agents import Agent
from schemas import DraftSections
from agent_config_loader import load_agent_config
from agent_library.section_writer_agent import get_section_writer_tool

TOOLS_REGISTRY = {
    "section_creation_tool": get_section_writer_tool(),
}

def create_section_orchestrator_agent() -> Agent:
    cfg = load_agent_config("Section Orchestrator Agent")
    
    tools = [TOOLS_REGISTRY[t] for t in cfg.get("tools", [])]

    return Agent(
        name=cfg["name"],
        model=cfg["model"],
        instructions=cfg["instructions"],
        tools=tools,
        output_type=DraftSections,
    )