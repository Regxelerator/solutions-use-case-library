from __future__ import annotations

from agents import Agent
from agents.model_settings import ModelSettings

from ..schemas import OrchestratorOut
from ..agent_config_loader import load_agent_config
from ..tools import TOOL_REGISTRY


def create_root_cause_agent() -> Agent:

    cfg = load_agent_config("Root Cause Specialist Agent")

    tool_names = cfg.get("tools", []) or []
    tools = [TOOL_REGISTRY[name] for name in tool_names if name in TOOL_REGISTRY]

    return Agent(
        name=cfg["name"],
        model=cfg.get("model", "gpt-5"),
        instructions=cfg["instructions"],
        tools=tools,
        output_type=OrchestratorOut,
        model_settings=ModelSettings(tool_choice="auto"),
    )
