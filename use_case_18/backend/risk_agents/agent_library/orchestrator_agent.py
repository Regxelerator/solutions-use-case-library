from __future__ import annotations
from datetime import datetime

from agents import Agent, Runner
from agents.model_settings import ModelSettings

from ..schemas import OrchestratorOut
from ..agent_config_loader import load_agent_config
from ..tools import TOOL_REGISTRY


def _create_orchestrator() -> Agent:
    cfg = load_agent_config("Orchestrator Agent")

    tool_names = cfg.get("tools", []) or []
    tools = [TOOL_REGISTRY[name] for name in tool_names if name in TOOL_REGISTRY]
    if not tools:
        tools = [
            TOOL_REGISTRY["get_form_status_tool"],
            TOOL_REGISTRY["update_fields_tool"],
        ]

    base_instructions: str = cfg["instructions"]

    def dynamic_instructions(context, agent_self) -> str:

        now = datetime.now().astimezone()
        today = now.strftime("%Y-%m-%d")
        dow = now.strftime("%A")
        tz = now.tzname() or "local time"

        prefix = (
            f"Today's date is {today} ({dow}, {tz}). "
            "Use this to interpret relative time phrases from the user and to infer "
            "'date_occured' and 'date_identified' when appropriate."
        )
        return f"{prefix}\n\n{base_instructions}"

    return Agent(
        name=cfg["name"],
        model=cfg.get("model", "gpt-5"),
        instructions=dynamic_instructions,
        tools=tools,
        output_type=OrchestratorOut,
        model_settings=ModelSettings(tool_choice="auto"),
    )


async def run_incident_flow(user_text: str, session=None, context=None) -> dict:
    agent = _create_orchestrator()
    res = await Runner.run(agent, user_text, session=session, context=context)

    out = res.final_output
    out_dict = out.model_dump() if hasattr(out, "model_dump") else dict(out)
    return out_dict