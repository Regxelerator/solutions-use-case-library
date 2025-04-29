import asyncio
import json
from datetime import date
from pathlib import Path
from typing import List
from agents import Runner, trace
from llm.llm_engine import Consolidation_Agent, ConsolidatedMemo, ValidationResult

def _format_findings(results: List[ValidationResult]) -> str:
    """Run *Agent_4_Consolidation* to convert ValidationResult objects into the plaintext list expected by the agent prompt."""
    
    lines: List[str] = []
    for r in results:
        if r.validation_result == "Relevant":
            finding = (
                f"- [RELEVANT] {r.title} ({r.publication_date})\n"
                f"  Source: {r.source}\n"
                f"  Reason: {r.validation_result_reason}\n"
                f"  Summary: {r.summary}\n"
                f"  URL: {r.url}\n"
            )
        else:
            finding = (
                f"- [NOT RELEVANT] {r.title or 'Untitled'}\n"
                f"  Reason: {r.validation_result_reason}\n"
            )
        lines.append(finding)
    return "\n".join(lines)


def _save_memo(entity: str, memo: ConsolidatedMemo, out_dir: Path = Path("final_memos")) -> Path:
    """Persist the ConsolidatedMemo as formatted JSON for record keeping."""
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"{entity}_{memo.memo_date}.json".replace(" ", "_")
    path.write_text(memo.model_dump_json(indent=2), encoding="utf-8")
    print(memo.model_dump_json(indent=2))
    return path

async def consolidate(
    entity_name: str,
    validated_results: List[ValidationResult],
) -> ConsolidatedMemo:
    """Run Consolidation_Agent on the full set of validation outputs."""
    findings_block = _format_findings(validated_results)
    prompt = (
        f"Entity name: {entity_name}\n"
        f"Memo date: {date.today().isoformat()}\n"
        f"Validated items:\n\n{findings_block}"
    )

    with trace("Agent 4: Consolidation of findings"):
        run = await Runner.run(Consolidation_Agent, prompt)

    memo = run.final_output_as(ConsolidatedMemo)
    _save_memo(entity_name, memo)
    return memo