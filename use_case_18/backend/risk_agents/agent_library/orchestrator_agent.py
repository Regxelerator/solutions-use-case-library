from __future__ import annotations
from datetime import datetime

from agents import Agent, Runner, handoff
from agents.model_settings import ModelSettings

from ..schemas import OrchestratorOut
from ..agent_config_loader import load_agent_config
from ..tools import TOOL_REGISTRY
from .root_cause_agent import create_root_cause_agent


def _create_orchestrator(root_cause_agent: Agent | None = None) -> Agent:
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

    rc_agent = root_cause_agent or create_root_cause_agent()
    rc_handoff = handoff(
        agent=rc_agent,
        tool_name_override="transfer_to_root_cause_specialist",
        tool_description_override=(
            "Hand off to the Root Cause Specialist when foundational incident details have been captured "
            "and a deeper root cause analysis is needed. The specialist will lead a focused dialogue and "
            "populate 'root cause'."
        ),
    )

    return Agent(
        name=cfg["name"],
        model=cfg.get("model", "gpt-5"),
        instructions=dynamic_instructions,
        tools=tools,
        handoffs=[rc_handoff],
        output_type=OrchestratorOut,
        model_settings=ModelSettings(tool_choice="auto"),
    )


async def run_incident_flow(user_text: str, session=None, context=None) -> dict:
    """
    Runs one turn of the incident flow with the orchestration agent handling the initial information gathering and then handing off to the root cause agent.
    Once the handoff to the root cause agent was performed, the deep dive conversation continues with that agent until it concludes.
    """
    orchestrator = _create_orchestrator()
    root_cause = create_root_cause_agent()

    starting_agent = (
        root_cause
        if getattr(context, "active_agent_name", None) == root_cause.name
        else orchestrator
    )

    res = await Runner.run(starting_agent, user_text, session=session, context=context)

    try:
        if hasattr(res, "last_agent") and res.last_agent is not None:
            if context is not None:
                context.active_agent_name = res.last_agent.name
    except Exception:
        pass

    out = res.final_output
    out_dict = out.model_dump() if hasattr(out, "model_dump") else dict(out)
    return out_dict