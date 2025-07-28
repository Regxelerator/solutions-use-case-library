from __future__ import annotations

import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, List

from agentic_flow_memo_feedback.agent_library import (
    Runner,
    SQLiteSession,
    trace,
    create_planner_agent,
    create_feedback_orchestrator_agent,
)
from agentic_flow_memo_feedback.schemas import DraftSections, Plan

from .memo_store import (
    list_sections,
    patch_section,
) 

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_handler = logging.handlers.RotatingFileHandler(
    LOG_DIR / "agentic_flow_feedback.log",
    maxBytes=3_000_000,
    backupCount=3,
    encoding="utf-8",
)
_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s  [%(levelname)s]  %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_logger.addHandler(_handler)


def _dump_raw(prefix: str, payload):
    try:
        stem = f"feedback_raw_{prefix.replace(' ', '_')}"
        path = LOG_DIR / f"{stem}.json"
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            try:
                path.write_text(
                    json.dumps(payload.model_dump(), indent=2), encoding="utf-8"
                )
            except Exception:
                path = path.with_suffix(".txt")
                path.write_text(repr(payload), encoding="utf-8")
        _logger.info("↳ raw output saved to %s", path.relative_to(LOG_DIR.parent))
    except Exception:
        pass


async def _execute_plan(
    plan: Plan,
    feedback: list[dict],
    user_instructions: str,
    session: SQLiteSession,
) -> DraftSections:

    sections = list_sections()  

    orchestrator_input = json.dumps(
        {
            "plan": plan.model_dump(),
            "memo_sections": sections,
            "feedback": feedback,
            "user_instructions": user_instructions,
        },
        ensure_ascii=False,
    )

    orchestrator = create_feedback_orchestrator_agent()
    _logger.info("→ Feedback Orchestrator Agent start")
    res = await Runner.run(orchestrator, orchestrator_input, session=session)
    drafts: DraftSections = res.final_output               
    _dump_raw("Feedback Orchestrator Agent", drafts)
    _logger.info("← Feedback Orchestrator Agent done")

    return drafts


async def run_agentic_feedback(
    feedback: list[dict], user_instructions: str
) -> List[Dict]:

    _logger.info(
        "Feedback run invoked (feedback items=%d)",
        len(feedback),
    )

    session = SQLiteSession("memo_feedback_run")

    with trace("Memo feedback‑integration workflow"):
        planner = create_planner_agent()
        p_input = json.dumps(
            {"feedback": feedback, "user_instructions": user_instructions},
            ensure_ascii=False,
        )
        p_res = await Runner.run(planner, p_input, session=session)
        plan: Plan = p_res.final_output
        _logger.info("Planner produced %d step(s)", len(plan.steps))

        drafts = await _execute_plan(plan, feedback, user_instructions, session)

    updated_sections: List[Dict] = []
    for d in drafts.draft_sections:
        sec_id = d.id
        updated = {
            "title": d.title,
            "content": d.content,
            "status": "Draft",          
            "sources": d.sources,
            "history": d.history,
        }
        ok = patch_section(sec_id, updated)
        if ok:
            updated_sections.append({"id": sec_id, **updated})

    _logger.info("Feedback integration finished – %d section(s) updated", len(updated_sections))
    return list_sections()