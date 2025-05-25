import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _prompt(group_id: str, requirements: str, filings_json: str) -> str:

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
        - Note the degree of completeness, clarity, and substance for each entity’s disclosure on that concept
    3. Return your insights for each rule_id in the form of an analysis in continuous prose in the prescribed JSON format. 

    # Output

    Your put consists of a valid JSON consisting of a single array where each element contains: 
    - `rule_id`: The string value of the analyzed rule.
    - `analysis_results`: Analysis findings for the specific disclosure requirement

    # Additional instructions
    * Be specific in your analysis, taking into account all available information.
    * Focus on highlighting key commonalities and differences.
    * Preserve the exact terminology as per the original information and rule text.
    * Strictly only rely on the provided information - do not inject any extraneous information.
    * Remain factual and objective. 

    # Inputs
    
    ## Rule ID
    {group_id}

    ## Applicable requirements
    {requirements}

    ## Disclosures
    {filings_json}

""".strip()


def perform_comparative_analysis(
    *, group_id: str, requirements_text: str, entity_filings_json: str
) -> tuple[dict, str]:

    response = client.chat.completions.create(
        model="o3",
        reasoning_effort="medium",
        messages=[
            {
                "role": "user",
                "content": _prompt(group_id, requirements_text, entity_filings_json),
                "response_format": { "type": "json_object" }
            }
        ],
    )
    raw = response.choices[0].message.content.strip()
    return json.loads(raw), raw