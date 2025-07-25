from agents import Agent
from schemas import SectionDraft
from agent_config_loader import load_agent_config
from tools.content_loader import content_loader
from tools.critic_tool import critic_tool


TOOLS_REGISTRY = {
    "content_loader": content_loader,
    "critic_tool": critic_tool,
}

def create_section_writer_agent() -> Agent:

    cfg = load_agent_config("Section Writer Agent")
    tools = [TOOLS_REGISTRY[t] for t in cfg.get("tools", [])]

    instructions = (
        cfg["instructions"]
    )

    return Agent(
        name=cfg["name"],
        model=cfg["model"],
        instructions=instructions,
        tools=tools,
        output_type=SectionDraft,
    )

def get_section_writer_tool():

    return create_section_writer_agent().as_tool(
        tool_name="section_creation_tool",
        tool_description=("""
            Creates a single memo section based on the instructions from the memo outline for the respective section and has that section quality reviewed.
            Returns a SectionDraft.
            """
        ),
    )