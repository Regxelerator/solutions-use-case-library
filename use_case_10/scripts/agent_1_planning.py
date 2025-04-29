import asyncio
from datetime import date
from pathlib import Path
from typing import Optional
from agents import Runner, trace
from llm.llm_engine import Planner_Agent, WebSearchPlan

DEFAULT_ENTITY_DIR = Path("input") / "entity_files"

async def plan_searches(
    entity_name: str,
    cutoff_date: str,
    entity_files_dir: Path | str = DEFAULT_ENTITY_DIR,
) -> WebSearchPlan:
    """Run Agent_1_Planning for one entity and return the WebSearchPlan.

    Parameters
    ----------
    entity_name : str
        Name of the entity to investigate (expects ``{entity_name}.yaml`` in
        *entity_files_dir*).
    cutoff_date : str
        Searches should only consider items on/after this date (YYYY‑MM‑DD).
    entity_files_dir : str | Path, default "input/entity_files"
        Directory containing YAML profiles. If you pass a different folder, it
        overrides the default.
    """
    entity_path = Path(entity_files_dir) / f"{entity_name}.yaml"

    if not entity_path.exists():
        raise FileNotFoundError(
            f"Entity file '{entity_path.name}' not found in {entity_files_dir}."
        )

    entity_yaml = entity_path.read_text(encoding="utf-8")
    today = date.today().isoformat()

    prompt = (
        f"Entity name: {entity_name}"
        f"Time period: {cutoff_date}"
        f"Current date: {today}"
        f"{entity_yaml}"
    )

    with trace("Agent 1: Planning OSINT search"):
        run = await Runner.run(Planner_Agent, prompt)

    return run.final_output_as(WebSearchPlan)