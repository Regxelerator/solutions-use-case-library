import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _prompt(rule_id: str, requirements: str, filings_json: str) -> str:

    return f"""
    # Role & Task
    You are a senior financial supervision analyst responsible reviewing public cybersecurity disclosures submitted in U.S. Securities and Exchange Commission (SEC) as part of their 2024 year-end 10-K filings prepared in accordance with the Cyber Disclosure (CYD) XBRL taxonomy. To that end, you are provided with:

    * A subset of the rules under the SEC's cyber disclosure rules, mapped against the relevant concepts from the CYD XBRL taxonomy
    * JSON-formatted disclosures by entities grouped by concepts 

    Your specific task is to perform a point-in-time analysis across entities, identifying key trends cyber risk management practices based on the disclosed information.  

    # Instructions

    1. Review the disclosures from all entities for the specific concepts listed under that rule_id.
    2. Compare and contrast entity responses:
        - Identify notable similarities and differences in how entities address the requirement.
        - Point out common trends, recurring gaps, or significant outliers (positive or negative).
        - As part of the analysis, note the degree of completeness, clarity, and substance for each entity’s disclosure with respect to the specific concept / requirement
    3. Return your insights for each rule_id in the form of an analysis in continuous prose in the prescribed JSON format. 

    # Output

    Your put consists of a valid JSON in the following specific structure:
    
    - `rule_id`: the rule id subject to analysis (string).
    - `analysis_results` : an object with:
          - `key_trends_and_commonalities` (string, unnumbered bulleted list).
          - `key_differences_and_notable_outliers` (string, unnumbered bulleted list).

    # Additional instructions
    * Be specific in your analysis, taking into account all available information, while keeping the output succinct.
    * Do not name individual entities unless addressing a material outlier. 
    * Preserve the exact terminology as per the original information and rule text.
    * Do not reference concept names - instead reference the associated label.
    * When analyzing disclosures involving boolean values, focus purely on aggregating the number of responses by value.
    * Remain factual and objective in your analysis.
    * Strictly only rely on the provided information - do not inject any extraneous information.

    # Inputs
    
    ## Rule ID
    {rule_id}

    ## Applicable requirements
    {requirements}

    ## Disclosures
    {filings_json}

    """.strip()


def _exec_summary_prompt(parent_rule_id: str, comparative_json: str) -> str:

    return f"""
    # Role & Task
    You are a senior financial supervision analyst tasked with preparing an *executive summary* for investors. You have already performed a detailed comparative analysis of registrant disclosures for a parent rule_id **and** all of its subsidiary requirements (hierarchy levels 2 and 3).  The JSON below contains those analysis results.

    # Instructions
    1. Read all comparative‑analysis results in the JSON.
    2. Distil the key insights into a concise executive summary (≈1‑3 paragraphs) that captures overarching themes, including notable commonalities and differences including any material outliers.
    3. Discuss findings in aggregate terms unless citing an outlier.

    # Output
    Return a *single* valid JSON object with:
      - `parent_rule_id`: the hierarchy‑level‑1 rule ID you are summarising;
      - `executive_summary`: the summary text in continuous prose.

    # Inputs
    ## Parent Rule ID
    {parent_rule_id}

    ## Comparative‑analysis results (JSON)
    {comparative_json}
    """.strip()


def perform_comparative_analysis(*, rule_id: str, requirements_text: str, entity_filings_json: str) -> tuple[dict, str]:

    response = client.chat.completions.create(
        model="o3",
        reasoning_effort="medium",
        messages=[
            {
                "role": "user",
                "content": _prompt(rule_id, requirements_text, entity_filings_json),
                "response_format": {"type": "json_object"},
            }
        ],
    )
    raw = response.choices[0].message.content.strip()
    return json.loads(raw), raw


def perform_executive_summary(*, top_rule_id: str, grouped_analysis_json: str) -> tuple[dict, str, str]:

    prompt_txt = _exec_summary_prompt(top_rule_id, grouped_analysis_json)
    response = client.chat.completions.create(
        model="o3",
        reasoning_effort="medium",
        messages=[
            {
                "role": "user",
                "content": prompt_txt,
                "response_format": {"type": "json_object"},
            }
        ],
    )
    raw = response.choices[0].message.content.strip()
    return json.loads(raw), raw, prompt_txt