import os
import json
from typing import List, Dict, Any
from llm.llm_engine import (
    get_prompt_for_outsourcing_agreement,
    get_response_from_openai,
)
from utils.pdf_parser import convert_pdf_to_markdown
from utils.file_handler import write_to_json_file


def identify_logical_units(markdown_text: str) -> List[Dict[str, Any]]:
    """
    Segments an outsourcing agreement into its logical units and returns a JSON.

    Parameters:
    markdown_text (str): The text of the outsourcing agreement in Markdown format.

    Returns:
    List[Dict[str, Any]]: A list of dictionaries, each representing a segmented logical unit.
    """
    prompt = get_prompt_for_outsourcing_agreement(markdown_text)
    response = get_response_from_openai(prompt, "o3-mini")

    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return []


def segment_by_logical_units(
    lines: List[str], main_headings: List[str]
) -> List[Dict[str, Any]]:
    """
    Segments a list of text lines into logical units based on predefined main headings.

    Parameters:
    lines (List[str]): A list of strings representing the document lines.
    main_headings (List[str]): A list of strings representing the headings.

    Returns:
    List[Dict[str, Any]]: A list of dictionaries where each dictionary represents a logical unit.
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


def segment_outsourcing_agreement(pdf_file: str, output_dir: str) -> str:
    """
    Extracts and segments an outsourcing agreement from a PDF file.

    Parameters:
    pdf_file (str): Path to the input PDF file.
    output_dir (str): Path to save the structured JSON output.

    return :
       str: path to Outsourcing_Agreement json file
    """
    markdown_text = convert_pdf_to_markdown(pdf_file)
    markdown_file = os.path.join(output_dir, "Test_Agreement.md")
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(markdown_text)

    logical_units = identify_logical_units(markdown_text)
    lines = markdown_text.splitlines()
    chunks = segment_by_logical_units(lines, logical_units)
    data = {
        "file_name": pdf_file,
        "logical_units_array": logical_units,
        "segmented_logical_units": chunks,
    }
    outsourcing_agreement_json_path = os.path.join(
        output_dir, "Outsourcing_Agreement.json"
    )
    write_to_json_file(outsourcing_agreement_json_path, data, indent=4)
    return outsourcing_agreement_json_path
