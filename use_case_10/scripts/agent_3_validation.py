import asyncio
import json
import traceback
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional
from agents import Runner, trace
from llm.llm_engine import Validation_Agent, ValidationResult

def _build_prompt(entity_name: str, item: Dict[str, str], cutoff_date: str) -> str:
    """Compose the user prompt expected by *Validation_Agent*."""
    return (
        f"Entity name: {entity_name}\n"
        f"News item ID:   {item.get('id', '')}\n"
        f"News item title:{item.get('title', '')}\n"
        f"Description:    {item.get('description', '')}\n"
        f"Source:         {item.get('source', '')}\n"
        f"Cut-off date:   {cutoff_date}"
    )

def _save_validation_json(entity: str, results: List[ValidationResult], out_dir: Path = Path("debug_validation")) -> Path:
    """Persist the list of ValidationResult models as a JSON array for auditing."""
    out_dir.mkdir(exist_ok=True)
    fname = f"{entity}_{date.today().isoformat()}.json".replace(" ", "_")
    path = out_dir / fname
    payload = [r.model_dump() for r in results]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

async def validate_items(
    entity_name: str,
    items: List[Dict[str, str]],
    cutoff_date: str,
) -> List[ValidationResult]:
    """Run *Agent_3_Validation* for each news item and return the parsed results.

    Parameters
    ----------
    entity_name : str
        Name of the investigated entity.
    items : list[dict]
        Raw items (id, title, description, source, etc.) produced by the search step.
    cutoff_date : str
        ISO date string (YYYY-MM-DD) limiting recency.

    Returns
    -------
    list[ValidationResult]
        Structured validation outcomes.
    """

    results: List[ValidationResult] = []
    total = len(items)
    for idx, item in enumerate(items, start=1):
        prompt = _build_prompt(entity_name, item, cutoff_date)
        print(f"\n[validate {idx}/{total}] {item.get('title', 'Untitled')}")
        try:
            with trace("Agent 3: Validation of findings"):
                run = await Runner.run(Validation_Agent, prompt)
            res = run.final_output_as(ValidationResult)
            print(res.json())
            results.append(res)
        except Exception:
            print(f"[ERROR] validation failed for {item.get('title', 'Untitled')}\n", traceback.format_exc())

    _save_validation_json(entity_name, results)
    return results