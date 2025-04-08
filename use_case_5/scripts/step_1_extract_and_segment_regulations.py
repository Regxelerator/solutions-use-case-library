import os
import json
from llm.llm_engine import (
    get_prompt_for_logical_unit_summary,
    get_prompt_to_identify_logical_units,
    get_prompt_for_regulation_overview,
    get_openai_response,
)
from utils.file_handler import write_to_json_file
from utils.pdf_parser import extract_pdf_to_markdown


def regulation_overview(markdown_text: str) -> str:
    """
    Extracts high-level metadata about a regulation using LLM.

    Args:
        markdown_text (str): Raw regulation text in Markdown format

    Returns:
        str: JSON string containing regulation overview or empty string on failure


    """
    prompt = get_prompt_for_regulation_overview(markdown_text)
    response = get_openai_response(prompt, model="gpt-4o")
    if "Error occurred" in response:
        print("Error generating regulation overview.")
        return ""
    return response


def determine_markdown_pattern(markdown_text: str) -> str:
    """
    Identifies logical unit headings/structure in regulation text.

    Args:
        markdown_text (str): Raw regulation text

    Returns:
        str: JSON array of identified headings or empty string on failure

    """
    prompt = get_prompt_to_identify_logical_units(markdown_text)
    response = get_openai_response(prompt, model="o3-mini")
    if "Error occurred" in response:
        print("Error determining markdown pattern.")
        return ""
    return response


def segment_by_logical_units(lines: list, main_headings: list) -> list:
    """
    Splits regulation text into structured segments based on headings.

    Args:
        lines (list): Text lines from the regulation
        main_headings (list): Identified section headings

    Returns:
        list: Structured segments with IDs, headings, and content

    """
    segments = []
    segment_id = 1
    current_segment = {
        "logical_unit_id": segment_id,
        "logical_unit_heading": None,
        "logical_unit_content": [],
    }
    for line in lines:
        if line.strip() in main_headings:
            if (
                current_segment["logical_unit_heading"]
                or current_segment["logical_unit_content"]
            ):
                segments.append(current_segment)
            segment_id += 1
            current_segment = {
                "logical_unit_id": segment_id,
                "logical_unit_heading": line.strip(),
                "logical_unit_content": [],
            }
        else:
            current_segment["logical_unit_content"].append(line)
    if (
        current_segment["logical_unit_heading"]
        or current_segment["logical_unit_content"]
    ):
        segments.append(current_segment)
    return segments


def create_logical_unit_chunks(markdown_text: str, headings_json_str: str) -> list:
    """
    Creates final structured chunks from raw text and identified headings.

    Args:
        markdown_text (str): Full regulation text
        headings_json_str (str): JSON string of identified headings

    Returns:
        list: Fully structured regulation segments

    """
    try:
        main_headings = json.loads(headings_json_str)
    except json.JSONDecodeError:
        main_headings = []
    lines = markdown_text.splitlines()
    return segment_by_logical_units(lines, main_headings)


def extracting_and_segmenting_regulations(input_dir: str) -> None:
    """
    Main pipeline for processing PDF regulations into structured JSON.

    Args:
        input_dir (str): Base directory containing PDFs

    Output:
        Creates JSON files in ./Regulations/Processed Regulations/
    """
    pdf_dir = os.path.join(input_dir, "Regulations")
    processed_dir = os.path.join(pdf_dir, "Processed Regulations")
    os.makedirs(processed_dir, exist_ok=True)
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

    for idx, pdf_file in enumerate(pdf_files, start=1):
        pdf_path = os.path.join(pdf_dir, pdf_file)

        markdown_text = extract_pdf_to_markdown(pdf_path)
        overview_text = regulation_overview(markdown_text)
        headings_json_str = determine_markdown_pattern(markdown_text)
        chunks = create_logical_unit_chunks(markdown_text, headings_json_str)

        for logical_unit in chunks:
            prompt = get_prompt_for_logical_unit_summary(
                "\n".join(logical_unit["logical_unit_content"])
            )
            response = get_openai_response(prompt, model="o3-mini")
            if "Error occurred" in response:
                print(
                    "Error occurred while summarizing the logical unit in openAI response"
                )
                continue
            else:
                logical_unit["logical_unit_summary"] = response

        data = {"regulation_overview": overview_text, "response": chunks}
        final_json_path = os.path.join(processed_dir, f"regulation_{idx}.json")
        write_to_json_file(final_json_path, data)
