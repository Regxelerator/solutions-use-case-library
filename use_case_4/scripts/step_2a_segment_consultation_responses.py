import os
import json
from typing import List, Dict, Any


from utils.pdf_parser import extract_pdf_to_markdown
from llm.llm_engine import (
    get_prompt_to_identify_logical_units,
    get_prompt_to_identify_respondent,
    get_response_from_openai
)


def identify_respondent_name(markdown_text: str) -> str:
    """
    Extract the respondent's name from the provided Markdown text.

    Args:
        markdown_text (str): The extracted Markdown text.

    Returns:
        str: The identified respondent name.
    """

    
    prompt = get_prompt_to_identify_respondent(markdown_text)
    result, error= get_response_from_openai(prompt, model="gpt-4o-mini")
     
    if error:
        print("Something went wrong:", error)
        return None
    else:
        print("Success:", result)
        return result


def determine_markdown_pattern(markdown_text: str) -> str:
    """
    Identify the logical structure of the consultation response.

    Args:
        markdown_text (str): The extracted Markdown text.

    Returns:
        str: A JSON string representing the identified headings.
    """

    
    prompt = get_prompt_to_identify_logical_units(markdown_text)
    result, error=get_response_from_openai(prompt, model="o3-mini")
    if error:
        print("Something went wrong:", error)
        return None
    else:
        print("Success:", result)
        return result


def segment_by_logical_units(
    lines: List[str], main_headings: List[str]
) -> List[Dict[str, Any]]:
    """
    Segment the Markdown text into logical units based on main headings.

    Args:
        lines (List[str]): List of lines from the Markdown text.
        main_headings (List[str]): Identified main headings.

    Returns:
        List[Dict[str, Any]]: A list of segmented content with headings.
    """

    segments = []
    current_segment = {"heading": None, "content": []}

    for line in lines:
        if line.strip() in main_headings:
            if current_segment["heading"] or current_segment["content"]:
                segments.append(current_segment)
                current_segment = {"heading": None, "content": []}
            current_segment["heading"] = line.strip()
        else:
            current_segment["content"].append(line)

    if current_segment["heading"] or current_segment["content"]:
        segments.append(current_segment)

    return segments


def create_subsection_chunks(
    markdown_text: str, headings_json_str: str
) -> List[Dict[str, Any]]:
    """
    Divide Markdown text into logical subsections based on main headings.

    Args:
        markdown_text (str): The extracted Markdown text.
        headings_json_str (str): JSON string containing main headings.

    Returns:
        List[Dict[str, Any]]: List of segmented subsections.
    """

    try:
        main_headings = json.loads(headings_json_str)
    except json.JSONDecodeError:
        main_headings = []

    lines = markdown_text.splitlines()
    segments = segment_by_logical_units(lines, main_headings)

    return segments


def segmenting_consultation_response(input_dir: str, output_dir: str) -> None | str:
    """
    Process consultation response PDFs by extracting text, segmenting content, and saving structured responses.

    Args:
        input_dir (str): Directory containing consultation response PDFs.
        output_dir (str): Directory to store processed JSON responses.
    return:
        processed_dir(str):path to directory where processed JSON responses will be stored.
    """

    pdf_dir = os.path.join(input_dir, "Consultation Paper", "Responses")
    if not os.path.isdir(pdf_dir):
        raise FileNotFoundError(f"Directory not found: {pdf_dir}")
    processed_dir = os.path.join(
        output_dir, "Consultation Paper", "Processed Responses"
    )
    os.makedirs(processed_dir, exist_ok=True)

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

    for idx, pdf_file in enumerate(pdf_files, start=1):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        markdown_text = extract_pdf_to_markdown(pdf_path)

        respondent_name = identify_respondent_name(markdown_text)
        headings_json_str = determine_markdown_pattern(markdown_text)
        chunks = create_subsection_chunks(markdown_text, headings_json_str)

        data = {"respondent_name": respondent_name, "response": chunks}

        final_json_path = os.path.join(processed_dir, f"response_{idx}.json")
        with open(final_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    return processed_dir
