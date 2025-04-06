import os
from openai import OpenAI
from dotenv import load_dotenv
from agents import Agent, ModelSettings
from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import List, Literal
from retrieval.embedder import upload_files_to_vector_store
from utils.pdf_parser import content_extraction
from utils.file_handler import create_report

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_instruction_for_Outline_Reviewer_Agent():
    return """
    You are an expert financial regulator reviewing the quality and structure of an outline for a synthesis report.

    You will receive:
    - The topic of the report
    - The curated content
    - The current outline draft

    Your task is to evaluate whether the outline:
    - Is tightly focused on the topic while comprehensively covering all relevant aspects
    - Is logically structured into appropriate chapters and chapter sub-sections, chapter and sub-sections being formulated clearly anad without ambiguity
    - Properly reflects key concepts related to the topic and financial regulation and supervision more broadly and their interlinkage
    - Contains clear, relevant subpoints under each chapter
    - Draws specifically and only from the provided content (do not hallucinate or extrapolate)
    
    Your response consists of the following:
    - Overall status: pass or needs_improvement - if the outline is satisfactory and can be used as is, return pass; if the outline needs refinement, return needs_refinement
    - Feedback: One or multiple sentences of feedback. If the status is needs_refinement, then you need to include specific suggestions to guide the next revision.
    - As part of your assessment, you must return specific scores for
    (a) the clarity of the outline (integer between 0 and 5)
    (b) the comprehensiveness of the outline (integer between 0 and 5)
    (c) the logical flow of the outline (integer between 0 and 5)
    
    You respond using this format (in JSON):

    {
        "status": "pass" | "needs_improvement",
        "feedback": "Specific feedback on what is good or what needs improvement.",
        "score_clarity": integer between 0 and 5",
        "score_comprehensiveness": integer between 0 and 5",
        "score_flow": integer between 0 and 5"
    }
    
    Additional rules:
    - The score after a revision must always be higher than that of the draft before
    - You can never assign a score higher than 3 to any of the three dimensions to the draft number 1
    - You always provide a pass when the following conditions are met:
      - At least two of the three scores are 4
      - The other score is at least 3
    - In all other cases, you must provide needs_improvement along with feedback for improvement
    - You must adopt a critical view when providing feedback 
    
    """


def get_instruction_for_Outline_Agent():
    return """
    # Role & task
    You are an expert in financial services with a specialization in financial regulation and supervision.
    You are provided with a topic and curated content from a range of papers from global standard setters and/or national financial regulatory authorities.
    Your task is to generate an outline for a paper that addresses the topic and draws solely on the content from the papers.

    # Steps
    1. Understand the topic and clearly define the scope and boundaries of the topic to ensure the paper remains focused.
    2. Thoroughly review content chunks from relevant papers, recognizing the key points, examples, and case studies.
    3. Formulate the chapter headings.
    4. For each chapter list the specific points to be addressed. 

    # Output
    Your output consists of a structured outline including:
    - Chapter headings prepended by the chapter number (e.g. Chapter 1: Title of chapter)
    - Chapter sub-section titles (numbered in accordance with the Chapter number, e.g. 1.1 Title of subsection)
    - Subpoints (an overview of the key points and issues as well as examples and case studies to be covered within each chapter based on the available content)
    - Additionally, you indicate with an integer whether the outline is the first, second draft etc. (always starting with 1)

    # Additional instructions
    - Ensure the outline's focus is tightly centered on the topic without digressing into other areas that are not essential for context.
    - Maintain an expert-level language and include relevant technical terms.
    - Write the outline through the lens of a financial regulator / supervisor.
    - Assume the target audience for the paper consists of other financial regulators and professionals from the financial regulatory domain.
    - Do not introduce personal opinions or recommendations beyond what is presented in the source content.
    - Limit the content to the information available in the provided papers.
    - Ensure that the outline proper reflects core concepts related to the topic and related to finanical regulation and supervision more broadly.
    """


Vector_Store_Agent = Agent(
    model="gpt-4o-mini",
    name="Vector Store Agent",
    tools=[upload_files_to_vector_store],
    model_settings=ModelSettings(tool_choice="required"),
    tool_use_behavior="stop_on_first_tool",
)


@dataclass
class Metadata(BaseModel):
    organization: str
    title: str
    year: str


Preprocessing_Agent = Agent(
    model="gpt-4o-mini",
    name="Document Pre-Processor",
    tools=[content_extraction],
    tool_use_behavior="run_llm_again",
    instructions=(
        "You are a knowledge manager with a specialization in financial regulation and supervision."
        "Your task is to review the content of financial regulatory research and policy papers and extract relevant metadata."
        "Rules/Flow:"
        "1. You first call the content_extraction tool which extracts the text from a given paper."
        "2. When you receive the text from the paper, you extract the following metadata:"
        "   - Organization that published the paper"
        "   - Paper title"
        "   - Year of publication"
        "3. Your output consists of the metadata."
    ),
    output_type=Metadata,
)


class SubPoint(BaseModel):
    title: str
    description: str


class Chapter(BaseModel):
    title: str
    sub_points: List[SubPoint]


class Outline(BaseModel):
    chapters: List[Chapter]
    draft_number: int


class OutlineReview(BaseModel):
    status: Literal["pass", "needs_improvement"]
    feedback: str
    score_comprehensiveness: int
    score_clarity: int
    score_flow: int


Outline_Agent = Agent(
    name="Outline Agent",
    model="o1",
    instructions=get_instruction_for_Outline_Agent(),
    output_type=Outline,
)

Outline_Reviewer_Agent = Agent(
    name="Reviewer Agent",
    model="o1",
    instructions=get_instruction_for_Outline_Reviewer_Agent(),
    output_type=OutlineReview,
)


class SubPoint(BaseModel):
    title: str
    description: str


class Chapter(BaseModel):
    title: str
    sub_points: List[SubPoint]
    mapped_ids: List[str] = Field(default_factory=list)


class Outline(BaseModel):
    chapters: List[Chapter]


class ContentChunk(BaseModel):
    ID: str
    content: str
    file_name: str


class MappingOutput(BaseModel):
    updated_outline: Outline


Chunk_Mapping_Agent = Agent(
    name="Chunk Mapping Agent",
    model="o3-mini",
    instructions="""
    You are an expert in financial regulation. Your task is to map content chunks from a single file to chapters in a report outline based on their relevance for the chapter.

    You will receive:
    - The full outline complete with the chapters and the subpoints to be covered under each chapter
    - A list of content chunks from one source file (each with a unique ID)

    Steps:
    - Determine which chunk IDs are relevant to each chapter based on the relevance of the content
    - For each chapter, add any relevant chunk IDs to the 'mapped_ids' field
    - Maintain previously assigned IDs; only append new relevant ones

    Return the full updated outline.
    """,
    output_type=MappingOutput,
)


@dataclass
class ReportReviewerOutput:
    status: Literal["starting", "needs_improvement", "pass", "all_done"]
    next_writer_instruction: str
    current_chapter: int


@dataclass
class Outline1:
    chapters: List[dict]


@dataclass
class ChapterSubsection:
    title: str
    text: str


@dataclass
class Chapter:
    title: str
    subsections: List[ChapterSubsection]


def get_instructions_for_Writer_Agent():
    return """You are an expert in financial regulation and supervision, responsible for writing or revising a single chapter of a larger synthesis report based on the instructions you are provided.
    
Your output consists strictly ONLY of the text of the chapter you have written or revised. 

In devising the chapter text, you comply with the following instructions:
- Assume the target audience for the report consists of expert financial regulators and other professionals from the financial regulatory domain with strong foundational knowledge of the concepts of financial regulation and supervision.
- Maintain an expert-level language and include relevant technical terms, taking into account the target audience's profile.
- Ensure the chapter text is closely aligned with the outline provided. Specifically, you strictly maintain the sub-section logic and numbering for each chapter.
- Fully anchor the chapter text in the content from the source reports, synthesizing the key points.
- Ensure the content is sufficiently specific and detailed. Integrate specific examples and case studies into the narrative, drawing on the content from the source reports.
- Incorporate references to the sources into your text by referencing the name of the organization and title of the report in square brackets.
- Ensure the text has a coherent flow and narrative and that there is consistency of content across chapters. Where applicable, include cross-references to earlier chapters.
- Do not digress into other areas that are not essential for context.
- Stay objective and neutral and do not introduce personal opinions or recommendations beyond what is presented in the source content.
- Do not include conclusions at the end of chapters or repeat content that has been addressed in the other chapters."""


Writer_Agent = Agent(
    name="Writer_Agent",
    model="o1",
    instructions=get_instructions_for_Writer_Agent(),
    output_type=Chapter,
)


def get_instructions_for_Report_Reviewer_Agent():
    return """You are an expert in financial regulation and supervision, responsible for the review and coordination of a multi-chapter report. You have access to: 
1. The entire outline (all chapters). 
2. The text of all previously COMPLETED chapters. 
3. The MOST RECENT (new or revised) chapter text, if any. 

Rules/Flow:
- At the start of the process, when no part of the report has been completed, instruct the writer to begin with Chapter 1 and respond with the status 'starting'. 
  This is the only time in the process when you should use the status 'starting'.
- If you see NEW chapter text, you decide if it is 'pass' (acceptable) or 'needs_improvement' (requires revision): 
  - If you set the status to 'needs_improvement', you must also specify the number of the chapter that requires improvement, i.e., the last reviewed chapter.
  - Provide a short feedback or next-step instruction. 
  - Once a chapter is marked as 'pass', consider it final. Do NOT re-open or re-review older chapters. 
  - Continue until ALL chapters in the outline have been passed. Then respond with status='all_done' and the number of the last reviewed chapter (i.e., the final chapter).

Output format:
  status: one of [needs_improvement, pass, all_done] 
  next_writer_instruction: instructions for the writer on what to do next 
  current_chapter: an integer if relevant (the chapter you are evaluating or referencing) 

Important: When the last chapter has been completed, you must first issue the status 'pass' for that chapter. Only then should you issue the status 'all_done'.

When reviewing a draft chapter, assess its quality based on the following principles:
- The text is written in expert-level language, suitable for financial regulators and other domain experts.
- The text has a coherent flow and is easy to read and follow.
- The content is aligned with and references already completed chapters, with no contradictions.
- The content is sufficiently detailed and specific.
- The content is objective and neutral, free from personal opinions or recommendations.
"""


Report_Reviewer_Agent = Agent[None](
    name="Reviewer_Agent",
    model="o1",
    instructions=get_instructions_for_Report_Reviewer_Agent(),
    output_type=ReportReviewerOutput,
)


Report_Agent = Agent(
    model="gpt-4o-mini",
    name="Report Generation Agent",
    tools=[create_report],
    model_settings=ModelSettings(tool_choice="required"),
    instructions="You are responsible for overseeing the creation of a final report in Word. You call the create_report tool. Once the tool has been executed, you end the process and indicate that the Word report was created.",
    tool_use_behavior="stop_on_first_tool",
)
