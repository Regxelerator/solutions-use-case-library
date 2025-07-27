"""Agentic workflow runner for Briefing‑Memo Creator."""
from __future__ import annotations

import json
import logging
import logging.handlers
import uuid
from pathlib import Path
from typing import Dict, List

from agentic_flow_memo_creation.agent_library import (
    Runner,
    SQLiteSession,
    trace,
    create_outline_agent,
    create_planner_agent,
    create_section_orchestrator_agent,
)
from agentic_flow_memo_creation.schemas import DraftSections, Outline, Plan

from .content_store import _load as _load_masterlist
from .memo_store import _save as _save_memo

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_handler = logging.handlers.RotatingFileHandler(
    LOG_DIR / "agentic_flow.log",
    maxBytes=5_000_000,
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


AGENTS: dict[str, callable] = {
    "Outline Agent": create_outline_agent,
    "Section Orchestrator Agent": create_section_orchestrator_agent,
}

def _agent_factory(name: str):
    try:
        return AGENTS[name]()
    except KeyError as exc:
        raise ValueError(f"Unknown agent “{name}” declared in plan") from exc

def _dump_raw(prefix: str, payload):
    """Persist raw agent output for post‑mortem inspection."""
    try:
        stem = f"agent_raw_{prefix.replace(' ', '_')}"
        path = LOG_DIR / f"{stem}.json"
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            try:
                path.write_text(json.dumps(payload.model_dump(), indent=2), encoding="utf-8")
            except Exception:
                path = path.with_suffix(".txt")
                path.write_text(repr(payload), encoding="utf-8")
        _logger.info("↳ raw output saved to %s", path.relative_to(LOG_DIR.parent))
    except Exception as exc:  
        _logger.warning("Could not dump raw output for %s: %s", prefix, exc)


async def _execute_plan(plan: Plan, session: SQLiteSession) -> DraftSections:
    outline: Outline | None = None
    drafts: DraftSections | None = None

    for step in plan.steps:
        agent = _agent_factory(step.agent)

        input_data = (
            outline.model_dump_json(indent=None)
            if step.agent == "Section Orchestrator Agent" and outline is not None
            else step.inputs or agent.instructions
        )

        _logger.info("→ %s start", step.agent)
        res = await Runner.run(agent, input_data, session=session)
        out = res.final_output
        _dump_raw(step.agent, out)
        _logger.info("← %s done (type=%s)", step.agent, type(out).__name__)

        if isinstance(out, Outline):
            outline = out

        elif isinstance(out, DraftSections):              
            drafts = out

        elif getattr(out, "draft_sections", None) is not None:
            dictified = [
                s if isinstance(s, dict) else getattr(s, "model_dump", lambda: dict())()
                for s in out.draft_sections
            ]
            drafts = DraftSections.model_validate({"draft_sections": dictified})
            _logger.warning("DraftSections accepted via duck‑typing (class identity mismatch).")

    if drafts is None:
        raise RuntimeError(
            "Section drafts were not produced by the workflow – "
            f"inspect {LOG_DIR}/agent_raw_Section_Orchestrator_Agent.* for details."
        )

    return drafts


async def run_agentic_generate(instruction: str) -> List[Dict]:
    """High‑level orchestrator used by the FastAPI endpoint."""
    _logger.info("Agentic run invoked with prompt: %.120s", instruction.replace("\n", " "))

    session = SQLiteSession("memo_run")

    with trace("Briefing memo generation workflow"):
        planner = create_planner_agent()
        p_res = await Runner.run(planner, instruction, session=session)
        plan: Plan = p_res.final_output
        _logger.info("Planner produced %d step(s)", len(plan.steps))

        drafts = await _execute_plan(plan, session)

    master = _load_masterlist()
    fn_to_id = {item["filename"]: item["id"] for item in master}

    processed: List[Dict] = []
    for idx, sd in enumerate(drafts.draft_sections):
        sec = sd.model_dump()
        sec["id"] = str(uuid.uuid4())
        sec["order"] = idx
        sec["sources"] = [fn_to_id.get(s, s) for s in sec.get("sources", [])]
        processed.append(sec)

    _save_memo(processed)
    _logger.info("Memo saved – %d section(s) written to memo_sections.json", len(processed))
    return processed