from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ROOT_DIR = Path(__file__).resolve().parent.parent
OTHER_IN = ROOT_DIR / "input" / "other_input"

with open(OTHER_IN / "glossary.json", encoding="utf-8") as f:
    _glossary = json.load(f)

GLOSSARY_TEXT: str = "\n".join(
    f"{item['Term']}: {item['Definition / Description']}" for item in _glossary
)

with open(OTHER_IN / "section_specific_instructions.json", encoding="utf-8") as f:
    _SECTION_MAP: Dict[str, List[str]] = {
        e["section_name"]: e["section_instructions"] for e in json.load(f)
    }

def create_minutes_main_sections(transcript: str, section_name: str, model_name: str) -> str:
    """Generate minutes text (JSON string) for *section_name* using fine-tuned model."""
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": get_prompt_minute_creation_main_sections(section_name)},
                {"role": "user", "content": create_user_prompt(transcript, section_name)},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Error] Failed to generate meeting minutes ({section_name}): {e}")
        return ""

def get_prompt_minute_creation_main_sections(section_name: str) -> str:
    section_instr = "\n".join(_SECTION_MAP.get(section_name, []))
    return ("""
    
    ## GENERAL INSTRUCTIONS

    **Role & task**

    You are monetary policy specialist at the Bank of England. 
    Your task is to draft the official minutes of the latest Monetary Policy Committee (MPC) meeting based on the verbatim transcript of the meeting, suitable for public release. 
    You create the minutes section by section. 

    **Instructions** 
    1. Read through the transcript in full. 
    2. Extract and consolidate all information relevant to the assigned section. 
    3. Condense the dialogue into concise prose paragraphs, clearly highlighting the principal arguments, perspectives, and points raised by committee members. 
    4. Group similar metrics into coherent paragraphs in the order they appear in the transcript 
    5. In the case of the section "The immediate policy decision", clearly noting any consensus achieved or final votes taken. 

    **Style guidelines** 
    * Use third-person past-tense prose 
    * Write long, information-dense sentences linked by semicolons where natural 
    * Preserve factual accuracy 
    * Use the same terminology as the members of the MPC and consistent with that in the glossary provided - avoid colloquial language or informal expressions 
    * Favour collective phrasing such as “Members noted…”; avoid attributing points to specific committee members unless explicitly stated in the transcript 
    * Paraphrase discussions clearly; include direct quotations only if essential for clarity or emphasis 
    * Quantify judgements and cite data precisely where available 
    * Do not include any discussion of the internal voting procedure beyond the final vote count 
    * Omit repetition, irrelevant remarks, off-agenda conversations, or filler dialogue 
    * Adopt a neutral, professional tone suitable for an institutional record, avoiding rhetorical flourishes or subjective interpretations 

    **Other rules** 
    * Strictly only rely on the content from the transcript - do not introduce any extraneous information 
    * Strictly refrain from adding any conclusions or personal opinions 
    * In your interpretation of information, ensure consistency with the terms and definitions in the glossary provided 

    **Output** Your output consists of a valid JSON with the key section_name and section_paragraphs.

    ## SECTION-SPECIFIC INSTRUCTIONS
    """ + section_instr + """

    ## GLOSSARY
    """ + GLOSSARY_TEXT
    )


def create_user_prompt(transcript: str, section_name: str) -> str:
    """Return user‑message content following draft format."""
    return f"""**Section**: {section_name}

**Transcript**:
{transcript}"""