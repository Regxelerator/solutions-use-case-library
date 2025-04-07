from typing import List
from utils.pdf_parser import extract_pdf_to_markdown
from utils.file_handler import save_json
from llm.llm_engine import get_prompt_chapter_extraction_prompt, openai_chat_request


def determine_markdown_pattern(markdown_text: str) -> List[str]:
    """
    Identify the main chapter headings in the consultation paper.

    Args:
        markdown_text (str): The extracted Markdown text.

    Returns:
        list: A list of chapter headings in Markdown format.
    """
    prompt = get_prompt_chapter_extraction_prompt(markdown_text)
    response = openai_chat_request(prompt)
    return response if isinstance(response, list) else []


def segment_by_known_headings(lines: list, main_headings: list) -> list:
    """
    Segment the Markdown text based on identified headings.

    Args:
        lines (list): List of Markdown text lines.
        main_headings (list): Identified main chapter headings.

    Returns:
        list: A list of segmented chapters with their content.
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


def segmenting_consultation_paper(
    consultation_pdf: str, output_path: str
) -> None | str:
    """
    Segments the consultation paper into chapters and saves them as JSON.
    Args:
        consultation_pdf (str): Path to the input PDF file.
        output_path (str): Directory to save the segmented JSON data.

    Returns:
        return:path to a JSON file segmented data .
    """
    markdown_text = extract_pdf_to_markdown(consultation_pdf)
    headings = determine_markdown_pattern(markdown_text)

    if not headings:
        print("Headings not found. Exiting...")
        return None

    lines = markdown_text.splitlines(keepends=True)
    segments = segment_by_known_headings(lines, headings)

    chapters_list = [
        {
            "chapter_id": idx,
            "chapter_title": seg["heading"] or "NO_HEADING",
            "chapter_content": "".join(seg["content"]).strip(),
        }
        for idx, seg in enumerate(segments, start=1)
    ]
    return save_json(chapters_list, output_path, "consultation_paper_segmented.json")
