from pathlib import Path
from agents import Agent
from agentic_flow_memo_feedback.schemas import Plan
from agentic_flow_memo_feedback.agent_config_loader import load_agent_config

def create_planner_agent() -> Agent:
    cfg = load_agent_config("Planner Agent")

    yaml_path = Path(__file__).resolve().parents[1] / "agents_list.yaml"
    roster = yaml_path.read_text(encoding="utf-8")

    instructions = (
        cfg["instructions"]
        + "\n\n---\n### Agent roster:\n```yaml\n"
        + roster
        + "\n```"
    )

    return Agent(
        name=cfg["name"],
        model=cfg["model"],
        instructions=instructions,
        output_type=Plan
    )
