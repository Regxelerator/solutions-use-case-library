import re
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from agents import Agent, ModelSettings, WebSearchTool, function_tool

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BING_API_KEY = os.getenv("BING_API_KEY")
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/news/search"

def bing_news_search(
    query: str,
    freshness: Literal["Day", "Week", "Month"] = "Week",
    count: int = 100,
    market: str = "en-US",
) -> dict:
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {
        "q": query,
        "freshness": freshness,
        "count": count,
        "setLang": market,
        "textDecorations": True,
        "textFormat": "HTML",
        "sortBy": "Date",
    }

    resp = requests.get(BING_ENDPOINT, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    raw = resp.json()
    items = raw.get("value", [])

    pruned = []
    for idx, art in enumerate(items, start=1):
        pruned.append(
            {
                "id": str(idx),
                "name": art.get("name"),
                "url": art.get("url"),
                "description": art.get("description"),
                "provider": art.get("provider", [{}])[0].get("name"),
            }
        )

    return {"articles": pruned}

def get_instructions_for_Planner_Agent():
    return """
    You are a financial supervision analyst. Your task is to perform an open source intelligence (OSINT) search using Bing News Search for a licensed entity. 
    You are to perform a search for the entity and key position holders (if specified).
    To that end you are provided with the contents of a YAML file containing the name of the entity and - if applicable - the key position holders which should be the focus of your search.
    Based on the file's contents you create a query that consists of the name of the entity or key position holder, the adverse keywords, the start date of the search (based on the initial input) and the names of the excluded sites.
    Specifically, your output is a valid JSON with the following keys (adjust the number of keywords based on the keywords in the file):
    - query: ("Name of entity or key position holder") AND (adverse_keyword_1 OR adverse_keyword_2 OR adverse_keyword_3 OR adverse_keyword_4) -site:[name of excluded site]
    - freshness: time interval for search
    The value for freshness must be determined based on the cut-off date. 
    You must return individual queries for the entity and each of the key position holders.
    """

class WebSearchItem(BaseModel):
    query: str
    freshness: Literal["Day", "Week", "Month"]

class WebSearchPlan(BaseModel):
    searches: List[WebSearchItem]

Planner_Agent = Agent(
    name="PlannerAgent",
    model="gpt-4.1",
    instructions=get_instructions_for_Planner_Agent(),
    output_type=WebSearchPlan,
)


def get_instructions_for_Search_Agent():
    return """
    # Role & task
    You are a financial supervision analyst. Your task is to perform an open source intelligence (OSINT) search using Bing News Search for a licensed entity and identify any adverse information.
    
    # Instructions
    1. Call the tool bing_news_tool and pass the query along with the freshness parameter as is.
    2. Once you receive the results from the bing_news_tool, pass these to the LLM and review them for any adverse information/developments.
    3. An item is considered adverse in nature for the specific entity if it involves matters such as:
    * Enforcement action
    * Investigation
    * Lawsuit
    * Misconduct
    * Fraud
    * Breach 
    * Disruption (e.g. an operational outage)
    * Cyber event
    * Consumer / investor complaint
    * Investigation, breach, misconduct, a cyber event
    4. If you identify any adverse information/developments, flag these for further review. 
    
    # Output
    Your output consists of the flagged information/developments in the form of a valid JSON with the following structure:
    
    {
      "articles": [
        {
          "id": "article ID",
          "name": "name / headline of the article",
          "description": "short description of the article",
          "source": "provider of the article"
        },
        …
      ]
    }
    
    If there are no adverse information / developments, you strictly return the phrase:
    No adverse information / developments identified.
    
    # Additional instructions
    * You strictly only call the bing_news_tool once with the provided query and freshness parameter
    * You strictly pass the query as is
    * If search results relate to the same matter, then you strictly only flag the item once using the most reliable source
    
    """

def _core_term(query: str) -> str:
    m = re.search(r'"([^"\']+)"', query)
    if m:
        return m.group(1)
    parts = query.split("AND", 1)
    return parts[0].strip().strip("()").strip()

@function_tool
async def bing_news_tool(query: str, freshness: str) -> str:
    """
    Run Bing News, prune to {"articles": […]}, save to debug/<core>.json,
    and return that JSON string (or the 'No adverse…' phrase).
    """
    print(f"\n🔍 Executing Bing News search for query:\n    {query}\n    freshness: {freshness}\n")

    pruned = bing_news_search(query, freshness=freshness)  # type: ignore[arg-type]
    json_str = json.dumps(pruned, indent=2)

    core = _core_term(query)
    safe_name = re.sub(r"\s+", "_", core)

    out_dir = Path(__file__).parent / "debug_news_results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{safe_name}.json").write_text(json_str, encoding="utf-8")

    return json_str

News_Search_Agent = Agent(
    name="NewsSearchAgent",
    model="o3-mini",
    instructions=get_instructions_for_Search_Agent(),
    tools=[bing_news_tool],
    tool_use_behavior="run_llm_again",
)


def get_instructions_for_Validation_Agent():
    return """
    # Role & task

    You are a financial supervision analyst, tasked with performing an open source intelligence (OSINT) search for a licensed entity.
    Your specific task is to validate a potentially adverse news item about a specific entity by running a second search, obtaining additional information and then validating the relevance of the item.

    # Instructions

    1. Based on the news item name, description and the original source, perform an additional search using the WebSearchTool. 
    2. Based on the results of the search and the additional information obtained, you must confirm that:
    * The item is indeed adverse in nature for the specific entity, i.e. relates to a lawsuit, an investigation, breach, misconduct, a cyber event
    * Is based on reliable information 
    * Was published on or after the cut-off date
    3. If the news is adverse and meets all re-validation criteria (i.e. it is based on reliable information AND published on or after the cut-off date), write a summary. Else, classify it as not relevant.

    # Output

    If the news is validated as relevant adverse news and meets all re-validation criteria, return a JSON with the following keys:
    - validation_result: relevant
    - validation_result_reason: A concise reason why the item is relevant
    - title: News item title
    - publication_date: YYYY-MM-DD
    - source: Source of the news
    - summary: A detailed summary of the adverse news, written in neutral, professional language.
    
    If the news is outdated, unreliable, or not adverse, strictly return a JSON with just the following two key-value pairs:
    - validation_result: not relevant
    - validation_result_reason: A concise reason why the item is not relevant
    
    # Additional instructions
    * For each item subject to validation you must strictly perform a search using the WebSearchTool to locate additional information that you use to validate the item.
    
    """

class ValidationResult(BaseModel):
    validation_result: Literal["Relevant", "Not relevant"] = Field(
        ..., description="Whether the item passed re-validation"
    )
    validation_result_reason: str = Field(
        ..., description="A short reason why it was marked Relevant or Not relevant"
    )
    title: Optional[str] = Field(
        None, description="News item title (only present if validation_result is 'Relevant')"
    )
    publication_date: Optional[str] = Field(
        None, description="Publication date (only if 'Relevant')"
    )
    source: Optional[str] = Field(
        None, description="News source (only if 'Relevant')"
    )
    summary: Optional[str] = Field(
        None, description="A detailed summary of the news item (only if 'Relevant')"
    )
    url: Optional[str] = Field(
        None, description="URL to source article (only if 'Relevant')"
    )

Validation_Agent = Agent(
    name="ValidationAgent",
    model="gpt-4.1",
    instructions=get_instructions_for_Validation_Agent(),
    tools=[WebSearchTool(search_context_size="high")],
    tool_use_behavior="run_llm_again",
    model_settings=ModelSettings(tool_choice="required"),
    output_type=ValidationResult,
)


def get_instructions_for_Consolidation_Agent():
    return """
    # Role & Task
    You are a financial supervision analyst. Your task is to prepare a focused memo documenting adverse news items about a licensed entity and its key position holders from an open source intelligence (OSINT) search using Bing Search.

    # Instructions
    1. Review in detail the identified adverse findings from the validation agent.
    2. Extract all items marked as "Relevant".
    3. Based on the relevant findings, generate a structured memo that includes a detailed synthesis of the individual findings, contextualized as appropriate.

    # Output format
    Your output consists of a valid JSON with the following keys:
    - entity_name: name of the investigated entity
    - memo_date: current date (YYYY-MM-DD)
    - findings: a narrative summary for each of the findings

    # Additional instructions
    * You strictly only rely on the information provided to you in preparing the synthesis without introducing any extraneous information
    * You use professional and objective language in synthesizing the information.
    * You only focus on findings marked as relevant/adverse 
    * If no adverse findings were identified, you simply return: No adverse findings were identified

    """

class ConsolidatedMemo(BaseModel):
    entity_name: str = Field(..., description="Name of the entity investigated")
    memo_date: str = Field(..., description="Date of memo preparation (YYYY-MM-DD)")
    findings: List[str] = Field(..., description="List of consolidated adverse findings")


Consolidation_Agent = Agent(
    name="ConsolidationAgent",
    model="o3",
    instructions=get_instructions_for_Consolidation_Agent(),
    output_type=ConsolidatedMemo,
)
