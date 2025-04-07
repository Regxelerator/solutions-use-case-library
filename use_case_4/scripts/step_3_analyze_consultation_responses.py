import os
import json
from typing import Tuple
from llm.llm_engine import (
    openai_chat_request,
    get_prompt_for_summarizing_responses,
    get_prompt_for_executive_summary,
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


def summarize_responses_for_question(
    question_data: dict,
    background_info: dict,
    chapter_content: str,
    previous_summaries: str = "",
) -> str:
    """
    Generates a summary of responses for a specific consultation question using OpenAI's API.

    Args:
        question_data (dict): The question details and responses.
        background_info (dict): Background information about the consultation.
        chapter_content (str): The text of the associated chapter from the consultation paper.
        previous_summaries (str, optional): Summaries of previous questions for reference.

    Returns:
        str: A summary of the responses to the consultation question.
    """

    prompt = get_prompt_for_summarizing_responses(
        question_data, background_info, chapter_content, previous_summaries
    )

    response = openai_chat_request(prompt, model="gpt-4o-mini")

    if isinstance(response, dict) and "error" in response:
        return f"Error generating summary: {response['error']}"

    return response if isinstance(response, str) else json.dumps(response, indent=2)


def create_executive_summary(background_info: dict, question_summaries: list) -> str:
    """
    Generates an executive summary based on all consultation responses.

    Args:
        background_info (dict): Background information about the consultation.
        question_summaries (list): List of summarized responses to individual consultation questions.

    Returns:
        str: A structured executive summary.
    """

    prompt = get_prompt_for_executive_summary(background_info, question_summaries)
    response = openai_chat_request(prompt, model="o1")

    if isinstance(response, dict) and "error" in response:
        return f"Error generating summary: {response['error']}"

    return response if isinstance(response, str) else json.dumps(response, indent=2)


def analyzing_consultation_responses(
    consult_paper_info_json: str,
    mapped_responses_json: str,
    consultation_quest_json: str,
    segmented_json_file: str,
    output_dir: str,
) -> Tuple[str, str]:
    """
    Analyzes consultation responses by summarizing individual question responses and
    compiling an executive summary.

    Args:
        consult_paper_info_json (str): Path to the JSON file containing consultation paper information.
        mapped_responses_json (str): Path to the JSON file containing mapped responses.
        consultation_quest_json (str): Path to the JSON file containing consultation questions.
        segmented_json_file (str): Path to the JSON file containing segmented consultation chapters.
        output_dir (str): Directory path where processed outputs will be stored.

    Returns:
        tuple: Path to the generated executive summary JSON file and consultation question summaries JSON File.
    """

    consultation_paper = load_json(consult_paper_info_json)
    questions_merged = load_json(mapped_responses_json)
    consultation_questions = load_json(consultation_quest_json)
    segmented_chapters = load_json(segmented_json_file)

    chapters_by_id = {str(chap["chapter_id"]): chap for chap in segmented_chapters}
    consultation_questions_by_id = {
        str(q["id"]): q for q in consultation_questions["consultation_questions"]
    }

    results = []
    previous_summaries_list = []

    for question_item in questions_merged["questions"]:
        question_id = question_item["id"]
        chapter_id = question_item["chapter_id"]

        chapter_data = chapters_by_id.get(chapter_id, {})
        chapter_title = chapter_data.get("chapter_title", "")
        chapter_content = chapter_data.get("chapter_content", "")

        previous_summaries_str = "\n".join(previous_summaries_list)

        summary_text = summarize_responses_for_question(
            question_data=question_item,
            background_info=consultation_paper,
            chapter_content=chapter_content,
            previous_summaries=previous_summaries_str,
        )

        results.append(
            {
                "id": question_id,
                "question": question_item["question"],
                "chapter_id": chapter_id,
                "chapter_title": chapter_title,
                "response_summary": summary_text,
            }
        )

        previous_summaries_list.append(summary_text)
    consult_quest_summary_json = os.path.join(
        output_dir, "consultation_question_summaries.json"
    )
    with open(consult_quest_summary_json, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)

    executive_summary_text = create_executive_summary(
        background_info=consultation_paper, question_summaries=results
    )

    executive_summary_json = os.path.join(output_dir, "executive_summary.json")
    with open(executive_summary_json, "w", encoding="utf-8") as f:
        json.dump(
            {"executive_summary": executive_summary_text},
            f,
            ensure_ascii=False,
            indent=2,
        )
    return executive_summary_json, consult_quest_summary_json
