from agents import Agent
from schemas import Outline
from agent_config_loader import load_agent_config
from tools.content_metadata_loader import content_metadata_loader
from tools.critic_tool import critic_tool

TOOLS_REGISTRY = {
    "content_metadata_loader": content_metadata_loader,
    "critic_tool": critic_tool,         
}

def create_outline_agent() -> Agent:
    cfg = load_agent_config("Outline Agent")

    tools = [TOOLS_REGISTRY[t] for t in cfg.get("tools", [])]

    return Agent(
        name=cfg["name"],
        model=cfg["model"],
        instructions=cfg["instructions"],
        tools=tools,
        output_type=Outline,
    )