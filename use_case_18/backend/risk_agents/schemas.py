from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class OrchestratorOut(BaseModel):
    reply: str
    patch: Optional[List[Dict[str, Any]]] = None


class IncidentFields(BaseModel):
    reporterName: Optional[str] = None
    department: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = None
    date_occured: Optional[str] = Field(default=None, description="Date incident occurred, e.g. 2025-08-08")
    date_identified: Optional[str] = Field(default=None, description="Date incident was identified, e.g. 2025-08-09")
    category: Optional[str] = None
    severity: Optional[str] = None  

    root_cause: Optional[str] = Field(default=None, alias="root cause")
    impact: Optional[str] = None
    mitigation: Optional[str] = None
    remediation: Optional[str] = None
    notes: Optional[str] = None


class FormStatus(BaseModel):
    is_complete: bool
    completed: List[str]
    missing: List[str]
    quality_hints: List[str] = []
    category_descriptions: Dict[str, str] = {}