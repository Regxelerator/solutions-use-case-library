import os
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_promt_for_determine_html_section_markers(html_text:str)->str:
     
     return f"""
    # Role & task
    You are a knowledge manager. You are presented with text from an annual report in HTML. Your task is to identify the sections of the Management's Discussion and Analysis (MD&A).

    # Instructions
    1. Locate the MD&A-specific table of contents (typically at the start of the MD&A section itself)
    2. Identify all the items in the table of contents at the most granular level. 
    3. For each item, extract the title along with the corresponding html anchor. 

    # Output

    Your output consists of a valid JSON array with objects, where each object follows this structure:

    [
    {{"section_title": "Risk Management", "html_anchor": "#18"}},
    {{"section_title": "Financial Highlights", "html_anchor": "#22"}}
    ]

    # Additional rules
    * You must strictly extract the section title verbatim
    * You must strictly cover the complete list of sections of the MD&A - do not omit any section
    * For the section_title, strictly ONLY return the title of the section without any numerical value

    # Input

    {html_text}
    """

def determine_html_section_markers(html_text: str) -> tuple:
   
    response = client.chat.completions.create(
        model="o4-mini", reasoning_effort="medium", messages=[{"role": "user", "content": get_promt_for_determine_html_section_markers(html_text)}]
    )
    return json.loads(response.choices[0].message.content.strip()), response.choices[0].message.content.strip()


def get_prompt_for_extract_information(section_text: str)->str:

    return f"""
    # Role & task
    You are an expert in financial supervision tasked with extracting detailed information on cyber risk from the Management Discussion and Analysis (MD&A) section of a bank's annual report.

    # Instructions:
    1. Carefully read the provided MD&A section.
    2. Extract detailed information specifically related to cyber risk, emphasizing the following focus areas:
    - Risk exposure: Identify any descriptions of potential vulnerabilities, exposure metrics, trends, or scenarios related to cyber risk.
    - Risk controls: Extract details about the specific controls, safeguards, or mitigation measures implemented to address cyber threats and vulnerabilities and/or planned investments for new controls.
    - Risk incidents: Locate and document any references to past cyber incidents, breaches, or disruptions, including any reported impacts or incident responses.
    - Risk governance: Capture information on the oversight, reporting, and governance frameworks established for managing cyber risk.
    - Other information: Other information relevant to 
    3. Additionally, extract the name of the bank.

    # Output
    Your output must be a valid JSON structured with the following exact structure:
    
    {{
        "bank_name": ["Name of bank"],
        "synthesis": {{
            "risk_exposure": ["Extracted information snippet 1", "Extracted information snippet 2"],
            "risk_controls":  ["Extracted information snippet 1", "Extracted information snippet 2"],
            "risk_incidents": ["Extracted information snippet 1", "Extracted information snippet 2"],
            "risk_governance":["Extracted information snippet 1", "Extracted information snippet 2"]
        }}
    }}
    
    If the MD&A contains no disclosure for a dimension, use the literal string "not_disclosed" instead of an array.

    # Additional guidelines:
    * Preserve the exact technical terms as per the original information.
    * Extract information precisely and comprehensively so it is clearly understandable without additional context.
    * Strictly only include information explicitly found within the provided text section.
    * Capture both qualitative and quantitative information (if available).
    * Remain factual and strictly refrain from adding any analysis, interpretation, or personal viewpoints.
    
    # Input
    
    MD&A Section:
    {section_text}
    
    """
    
def extract_information(section_text: str) -> tuple:

    response = client.chat.completions.create(
        model="o4-mini", reasoning_effort="medium", messages=[{"role": "user", "content": get_prompt_for_extract_information(section_text)}]
    )
    return json.loads(response.choices[0].message.content.strip()), response.choices[0].message.content.strip()


def get_prompt_for_synthesize_information(risk_info_json: str) -> str:
    return f"""
    # Role & task
    You are a senior financial‑supervision analyst. Your task is to produce an auditable synthesis of a bank’s cyber‑risk disclosures from the Management Discussion and Analysis, based **solely** on the extracted risk information provided (in JSON format) along the main risk management dimensions:
    - Risk exposure  
    - Risk controls  
    - Risk incidents  
    - Risk governance  
    
    # Instructions  
    1. Read through the provided JSON containing per‑section risk extractions.  
    2. For each risk management dimension, synthesize the key information into a detailed yet concise paragraph.  
    3. Highlight material developments that indicate changes in risk levels or shifts in the bank’s approach, flagging any trends, changes, or emerging issues.  

    # Output  
    
    Your output must be a valid JSON structured with the following exact structure, with each key under synthesis mapping to a paragraph in continuous prose:
        
    {{
        "bank_name": ["Name of bank"],
        "synthesis": {{
            "risk_exposure": ["Synthesized narrative for risk exposure"],
            "risk_controls":  ["Synthesized narrative for risk controls"],
            "risk_incidents": ["Synthesized narrative for risk incidents"],
            "risk_governance": ["Synthesized narrative for risk govenrance"]
        }}
    }}
    
    # Additional guidelines  
    * Be specific and comprehensive in the synthesis, taking into account all available information.
    * Where useful for context, highlight from which specific section information was sourced from (e.g. if a risk is addressed in a top risk or emerging risk section that should be reflected in the narrative).
    * Preserve the exact technical terms as per the original information.
    * Strictly only rely on the provided information - do not inject any extraneous information.
    * Remain factual and strictly refrain from adding any analysis/assessment of effectiveness, interpretation, or personal viewpoints.
    * If information on a specific dimension is "not_disclosed", make this explicit in the narrative.
    
    # Input
    
    Risk Information JSON:
    {risk_info_json}
    """

def synthesize_information(risk_info_json: str) -> tuple:
    response = client.chat.completions.create(
        model="o3", reasoning_effort="medium", messages=[{"role": "user", "content": get_prompt_for_synthesize_information(risk_info_json)}]
    )
    return (json.loads(response.choices[0].message.content.strip()), response.choices[0].message.content.strip()
    )


def get_prompt_for_comparative_analysis(combined_analysis_json: str) -> str:
    return f"""
    # Role & task
    You are a senior financial‑supervision analyst. Your task is to carry out a comparative analysis of disclosed cyber risk information from a bank (based on information the annual report's MD&A section) over two consecutive years. 
    Your objective is to identify supervisory-relevant shifts for each of the identified risk dimensions based on provided results of a risk synthesis.

    # Instructions

    1. Identify Key Changes: Compare the data for each risk dimension between the two years.
    2. Analyze Developments: Determine significant changes or trends in the following areas:
    - Risk exposure
    - Risk controls
    - Risk incidents
    - Risk governance
    
    3. Synthesize Information: Write succinct paragraphs detailing key developments for each dimension, highlighting key shifts and trends.

    # Output Format

    Your output must be a valid JSON structured with the following exact structure, with each key under synthesis mapping to a paragraph in continuous prose:
    {{
        "bank_name": ["Name of bank"],
        "synthesis": {{
            "risk_exposure": ["Comparative analysis for risk exposure"],
            "risk_controls":  ["Comparative analysis for risk controls"],
            "risk_incidents": ["Comparative analysis for risk incidents"],
            "risk_governance": ["Comparative analysis for risk governance"]
        }}
    }}

    Each entry should clearly highlight the year-on-year development for the respective risk dimension.


    # Additional guidelines  
    * Be specific in your comparative analysis, taking into account all available information.
    * In your analysis, focus on highlighting relevant shifts and changes. If risk information is consistent across the two years with no visible changes, make this explicit in your analysis.
    * Where possible, add specific evidential information to support your conclusion. 
    * Preserve the exact technical terms as per the original information.
    * Strictly only rely on the provided information - do not inject any extraneous information.
    * Remain factual and objective. 

    # Input

    Analysis results from both years:
    {combined_analysis_json}
    """

def perform_comparative_analysis(combined_analysis_json: str) -> tuple:
    response = client.chat.completions.create(
        model="o3", reasoning_effort="medium", messages=[{"role": "user", "content": get_prompt_for_comparative_analysis(combined_analysis_json)}]
    )
    return (json.loads(response.choices[0].message.content.strip()), response.choices[0].message.content.strip()
    )