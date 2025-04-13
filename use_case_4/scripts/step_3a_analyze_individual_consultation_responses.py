import os
import json
from typing import List, Any, Tuple
from llm.llm_engine import (
    openai_chat_request,
    get_prompt_for_summarizing_individual_responses,
)


def load_json(file_path: str) -> dict:
    """
    Loads a JSON file and returns its contents as a dictionary.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_list(items: List[Any], size: int) -> List[List[Any]]:
    """
    Splits a list into chunks of a specified size.

    Args:
        items (List[Any]): The list to split.
        size (int): The maximum size of each chunk.

    Returns:
        List[List[Any]]: A list of chunked lists.
    """
    return [items[i : i + size] for i in range(0, len(items), size)]


def summarize_chunk(
    question_data: dict,
    background_info: dict,
    chapter_content: str,
) -> dict:
    """
    Generates a summary for a chunk of responses to a consultation question.

    Args:
        question_data (dict): The question details and the response chunk.
        background_info (dict): Background information about the consultation.
        chapter_content (str): The text of the associated chapter from the consultation paper.

    Returns:
        dict: Parsed JSON summary of the chunk.
    """
    prompt = get_prompt_for_summarizing_individual_responses(
        question_data, background_info, chapter_content
    )
    response = openai_chat_request(prompt, model="o3-mini")
    if isinstance(response, dict):
        return response
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {}


def analyzing_consultation_responses(
    consult_paper_info_json: str,
    mapped_responses_json: str,
    consultation_quest_json: str,
    segmented_json_file: str,
    output_dir: str,
) -> str:
    """
    Analyzes consultation responses by summarizing individual respondent answers for each question.

    Args:
        consult_paper_info_json (str): Path to the JSON file containing consultation paper information.
        mapped_responses_json (str): Path to the JSON file containing mapped responses.
        consultation_quest_json (str): Path to the JSON file containing consultation questions.
        segmented_json_file (str): Path to the JSON file containing segmented consultation chapters.
        output_dir (str): Directory path where processed outputs will be stored.

    Returns:
        str: Path to the generated consultation question summaries JSON file.
    """
    consultation_paper = load_json(consult_paper_info_json)
    questions_merged = load_json(mapped_responses_json)
    segmented_chapters = load_json(segmented_json_file)
    chapters_by_id = {str(ch["chapter_id"]): ch for ch in segmented_chapters}

    results = []

    for q in questions_merged["questions"]:
        chapter_id = str(q.get("chapter_id", ""))
        chapter_text = chapters_by_id.get(chapter_id, {}).get("chapter_content", "")

        merged_responses = []
        for resp_chunk in chunk_list(q.get("responses", []), 5):
            chunk_question_data = {
                "id": q["id"],
                "question": q["question"],
                "chapter_id": chapter_id,
                "responses": resp_chunk,
            }
            chunk_summary = summarize_chunk(
                question_data=chunk_question_data,
                background_info=consultation_paper,
                chapter_content=chapter_text,
            )
            merged_responses.extend(chunk_summary.get("responses", []))

        results.append(
            {
                "question_id": q["id"],
                "chapter_id": chapter_id,
                "summary": {
                    "consultation_question": q["question"],
                    "responses": merged_responses,
                },
            }
        )

    os.makedirs(output_dir, exist_ok=True)
    consult_quest_summary_json = os.path.join(
        output_dir, "summaries.json"
    )
    with open(consult_quest_summary_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return consult_quest_summary_json