import asyncio
import json
import traceback
from pathlib import Path
from typing import Dict, List

from scripts.agent_1_planning import plan_searches, DEFAULT_ENTITY_DIR
from scripts.agent_2_search import run_searches_concurrently
from scripts.agent_3_validation import validate_items, ValidationResult
from scripts.agent_4_consolidation import consolidate, ConsolidatedMemo

def _extract_items_for_validation(raw_outputs: List[str], cutoff_date: str) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for raw in raw_outputs:
        raw_str = raw.strip()
        if not raw_str.startswith("{"):
            continue 
        try:
            payload = json.loads(raw_str)
            for art in payload.get("articles", []):
                items.append(
                    {
                        "id": art.get("id", ""),
                        "title": art.get("name", ""),
                        "description": art.get("description", ""),
                        "source": art.get("provider", art.get("source", "")),
                        "cutoff_date": cutoff_date,
                    }
                )
        except Exception as exc:
            print("[WARN] invalid JSON from search agent:", exc)
    return items


async def run_research_flow(entity_name: str, cutoff_date: str) -> None:

    print("(--------Planning OSINT searches--------)\n")
    plan = await plan_searches(entity_name, cutoff_date, DEFAULT_ENTITY_DIR)
    for it in plan.searches:
        print(f" • {it.query}  (freshness: {it.freshness})")
    
    print("(--------Executing OSINT searches--------)\n")
    raw_search_outputs = await run_searches_concurrently(plan.searches)
    
    to_validate = _extract_items_for_validation(raw_search_outputs, cutoff_date)
    if not to_validate:
        print("No items to validate – workflow finished.")
        return
    
    print("(--------Validating findings--------)\n")
    validated_results: List[ValidationResult] = await validate_items(entity_name, to_validate, cutoff_date)
    
    print("(--------Consolidating findings--------)\n")
    memo: ConsolidatedMemo = await consolidate(entity_name, validated_results)
    
    print("(--------Final memo ready--------)\n")
    print(memo.model_dump_json(indent=2))


async def main() -> None:
    entity = input("Enter the name of the entity to research: ")
    cutoff = input("Enter the cut-off date for the searches (YYYY-MM-DD): ")
    await run_research_flow(entity, cutoff)


if __name__ == "__main__": 
    asyncio.run(main())