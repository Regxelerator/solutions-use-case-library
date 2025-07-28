from typing import List, Optional
from pydantic import BaseModel


class Step(BaseModel):
    id: str
    description: str
    agent: str
    inputs: str
    outputs: List[str]


class Plan(BaseModel):
    plan_name: str
    created: str
    steps: List[Step]


class Content(BaseModel):
    filename: str
    content_name: str


class Section(BaseModel):
    section_header: str
    description: str
    section_outline: str
    content: List[Content]


class Outline(BaseModel):
    sections: List[Section]


class SectionDraft(BaseModel):
    id: Optional[str] = ""                 
    order: int                            
    status: str = "Draft"                 
    title: str                            
    content: str                          
    sources: List[str]                   
    history: List[str] = []               


class DraftSections(BaseModel):
    draft_sections: List[SectionDraft]


class Evaluation(BaseModel):
    section: str
    passed: bool
    comments: str


class Evaluation_Report(BaseModel):
    evaluation_report: List[Evaluation]
    overall: str
