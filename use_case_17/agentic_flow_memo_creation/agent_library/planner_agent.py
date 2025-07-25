from pathlib import Path
from agents import Agent
from schemas import Plan
from agent_config_loader import load_agent_config

def create_planner_agent() -> Agent:
    cfg = load_agent_config("Planner Agent")

    yaml_path = Path(__file__).resolve().parents[1] / "agents_list.yaml"
    yaml_text = yaml_path.read_text(encoding="utf-8")

    instructions = (
        cfg["instructions"]
        + "\n\n---\n### Agent roster:\n```yaml\n"
        + yaml_text
        + "\n```"
    )

    return Agent(
        name=cfg["name"],
        model=cfg["model"],
        instructions=instructions,
        tools=[],
        output_type=Plan,
    )