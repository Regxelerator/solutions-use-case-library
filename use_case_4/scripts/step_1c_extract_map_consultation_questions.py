import os
import json
from utils.file_handler import save_json
from llm.llm_engine import (
    fetch_openai_response,
    get_prompt_to_assign_chapter_ids,
    get_prompt_to_extract_questions,
)


def extract_questions_from_consultation(
    chapter_title: str, chapter_content: str
) -> list:
    """Extract consultation questions from a given chapter"""

    prompt = get_prompt_to_extract_questions(chapter_title, chapter_content)
    parsed_response = fetch_openai_response(prompt)
    return [q for q in parsed_response.get("questions", []) if isinstance(q, str)]


def assign_chapter_ids(chapters_file: str, questions_file: str) -> None:
    """Assigns chapter IDs to consultation questions and updates the file"""
    try:
        with open(chapters_file, "r", encoding="utf-8") as cf:
            chapters_data = json.load(cf)
        with open(questions_file, "r", encoding="utf-8") as qf:
            questions_data = json.load(qf)
    except FileNotFoundError as e:
        print("File not found:", e)
        return
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return
    prompt = get_prompt_to_assign_chapter_ids(chapters_data, questions_data)
    parsed_response = fetch_openai_response(prompt)
    updated_questions = parsed_response.get("consultation_questions", [])

    with open(questions_file, "w", encoding="utf-8") as qf:
        json.dump(
            {"consultation_questions": updated_questions},
            qf,
            ensure_ascii=False,
            indent=2,
        )


def extracting_and_mapping_questions(segmented_json_file: str, output_dir: str) -> str:
    """
    Extracts consultation questions from a JSON file containing segmented chapters
    and maps them into a structured output JSON file.

    Args:
        segmented_json_file (str): Path to the input JSON file containing segmented chapters.
        output_dir (str): Path to the output directory to create JSON file to store extracted questions.

    """

    with open(segmented_json_file, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    all_questions = []
    question_counter = 1

    for chapter_index, chapter in enumerate(chapters, start=1):
        title = chapter.get("chapter_title", "")
        content = chapter.get("chapter_content", "")

        raw_questions = extract_questions_from_consultation(title, content)

        for q_text in raw_questions:
            all_questions.append(
                {"id": f"question_{question_counter}", "question": q_text.strip()}
            )
            question_counter += 1

    output_json_questions = save_json(
        {"consultation_questions": all_questions},
        output_dir,
        'consultation_questions.json'
    )
    assign_chapter_ids(segmented_json_file, output_json_questions)
    return output_json_questions
