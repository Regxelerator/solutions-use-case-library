from __future__ import annotations

from typing import List
from agents import RunContextWrapper
from agents.tool import function_tool
from draft_store import DRAFT
from ..schemas import IncidentFields, FormStatus
from ..context import IncidentRunContext

REQUIRED_FIELDS: List[str] = [
    "title",
    "description",
    "date_occured",
    "date_identified",
    "category",
    "severity",
    "impact",
    "mitigation",
    "remediation",
    "reporterName",
    "department",
]


@function_tool(
    name_override="get_form_status_tool",
    description_override="Return which required fields are completed vs missing and provide quality hints."
)
def get_form_status() -> FormStatus:
    completed = [k for k in REQUIRED_FIELDS if str(DRAFT.get(k, "")).strip() != ""]
    missing = [k for k in REQUIRED_FIELDS if k not in completed]

    hints: List[str] = []
    desc = str(DRAFT.get("description", "") or "")
    if desc and len(desc) < 80:
        hints.append("Description appears brief; ask for timeline, who noticed it, and specific steps/events.")
    impact = str(DRAFT.get("impact", "") or "")
    if impact and len(impact) < 60:
        hints.append("Impact looks short; request magnitude (customers affected, transactions, financial/ops effect).")
    root_cause = str(DRAFT.get("root cause", "") or "")
    if root_cause and len(root_cause) < 50:
        hints.append("Root cause looks high-level; probe for specific failure, control gaps, or contributing factors.")
    sev = str(DRAFT.get("severity", "") or "")
    if sev and sev not in {"Low", "Medium", "High", "Critical"}:
        hints.append("Severity should be one of: Low, Medium, High, Critical.")

    return FormStatus(
        is_complete=len(missing) == 0,
        completed=completed,
        missing=missing,
        quality_hints=hints,
    )


@function_tool(
    name_override="update_fields_tool",
    description_override=(
        "Update the incident report form with any fields you extracted. "
        "Provide ONLY fields you want to set/replace in this turn. "
        "Returns a JSON-Patch list of replace ops to apply."
    ),
)
def update_fields(ctx: RunContextWrapper[IncidentRunContext], fields: IncidentFields):
    if fields is None:
        ctx.context.last_patch = []
        return []

    try:
        payload = fields.model_dump(exclude_none=True, by_alias=True)
    except Exception:
        payload = fields.dict(exclude_none=True, by_alias=True)        

    patch = []
    for key, value in payload.items():
        if isinstance(value, str):
            value = value.strip()
        patch.append({"op": "replace", "path": f"/{key}", "value": value})

    ctx.context.last_patch = patch
    return patch