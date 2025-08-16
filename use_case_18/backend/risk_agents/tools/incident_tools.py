from __future__ import annotations

from typing import List, Dict
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

CATEGORY_OPTIONS: List[str] = [
    "Strategy risk",
    "Cyber security risk",
    "Security risk",
    "Legal risk",
    "People risk",
    "Technology risk",
    "Information risk",
    "Financial risk",
]

CATEGORY_DESCRIPTIONS: Dict[str, str] = {
    "Strategy risk": "Risks from identifying and pursuing a strategy that is poorly defined, based on flawed or inaccurate data, or fails to support commitments, plans, or objectives due to a changing macro-environment (e.g., political, economic, social, technological, environmental, or legislative change).",
    "Cyber security risk": "Risks from failing to prevent malicious activity against information systems, including threats such as malware, phishing, data breaches, or other forms of cyber attack, and non-compliance with data protection regulations (e.g., GDPR).",
    "Security risk": "Risks from failing to prevent unauthorised or inappropriate access to premises, assets, or information, leading to harm, theft, disruption, or breaches of safety and physical security.",
    "Legal risk": "Risks from defective transactions, litigation (including counterclaims), or other legal events that result in liability or loss, or from failing to meet legal/regulatory requirements or protect assets (e.g., intellectual property).",
    "People risk": "Risks from ineffective leadership and engagement, poor culture, inappropriate behaviours, insufficient capacity/capability, industrial action, or non-compliance with employment law/HR policies, resulting in negative performance impacts.",
    "Technology risk": "Risks from technology failing to deliver expected services due to inadequate/deficient system or process development, poor performance, or insufficient resilience.",
    "Information risk": "Risks from failing to produce robust, accurate, and appropriate data/information, or failing to exploit data/information to its full potential.",
    "Financial risk": "Risks from failing to manage finances in line with requirements and constraints, resulting in poor investment returns, ineffective asset/liability management, lack of value for money, or non-compliant financial reporting."
}


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

    cat = str(DRAFT.get("category", "") or "")
    if cat:
        if cat not in CATEGORY_OPTIONS:
            hints.append(
                "Category should be one of: Strategy risk, Cyber security risk, Security risk, "
                "Legal risk, People risk, Technology risk, Information risk, Financial risk."
            )
            if "category" in completed:
                completed.remove("category")
            if "category" not in missing:
                missing.append("category")
    else:
        hints.append(
            "Pick the top-level category from the predefined taxonomy (e.g., Strategy risk, Cyber security risk, etc.)."
        )

    if set(REQUIRED_FIELDS) - set(missing) and ("root cause" in missing or (root_cause and len(root_cause) < 50)):
        hints.append(
            "If foundational details are captured but root cause is missing or shallow, hand off to the "
            "Root Cause Specialist for a focused deep dive."
        )

    return FormStatus(
        is_complete=len(missing) == 0,
        completed=completed,
        missing=missing,
        quality_hints=hints,
        category_descriptions=CATEGORY_DESCRIPTIONS,
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