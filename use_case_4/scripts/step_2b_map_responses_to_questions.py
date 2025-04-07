import os
import glob
import json
from concurrent.futures import ThreadPoolExecutor
from llm.llm_engine import fetch_openai_response, get_prompt_for_relevance_check


def get_relevance_for_chunk(questions, heading, content):
    """
    Determines the relevance of a response chunk to consultation questions using an AI model.

    Args:
        questions (list): A list of dictionaries containing question IDs and text.
        heading (str): The heading of the response chunk.
        content (str): The content of the response chunk.

    Returns:
        dict: A dictionary mapping question IDs to relevance scores (1 for relevant, 0 for not relevant).
    """

    questions_str = " ".join([f"{q['id']}: {q['question']}" for q in questions])
    prompt = get_prompt_for_relevance_check(questions_str, heading, content)

    try:
        parsed = fetch_openai_response(prompt)
        relevance_map = parsed.get("relevance", {})
        output = {q["id"]: relevance_map.get(q["id"], 0) for q in questions}
        return output
    except Exception as exc:
        return {q["id"]: 0 for q in questions}


def process_single_response_file(
    file_path: str, consultation_questions: list, output_dir: str
) -> str:
    """
    Processes a single consultation response file, mapping response segments to relevant consultation questions.

    Args:
        file_path (str): Path to the JSON file containing respondent's answers.
        consultation_questions (list): List of consultation questions, each with an "id" and "question" text.
        output_dir (str): Directory where the processed JSON output will be saved.

    Returns:
        str: Path to the output JSON file containing consultation questions with mapped responses.
    """

    with open(file_path, "r", encoding="utf-8") as rf:
        response_data = json.load(rf)

    respondent_name = response_data.get("respondent_name", "Unknown Respondent")
    chunks = response_data.get("response", [])

    question_replies = {q["id"]: "" for q in consultation_questions}

    for chunk in chunks:
        heading = chunk.get("heading", "")
        content = chunk.get("content", "")

        if isinstance(content, list):
            content = " ".join(content)

        relevance_map = get_relevance_for_chunk(
            consultation_questions, heading, content
        )

        for qid, is_relevant in relevance_map.items():
            if is_relevant == 1:
                question_replies[qid] += f"\n\n---\n\nHeading: {heading}\n\n{content}"

    output_questions = []
    for q in consultation_questions:
        qid = q["id"]
        accumulated_text = question_replies[qid].strip()
        q_copy = {
            "id": qid,
            "question": q["question"],
            "chapter_id": q.get("chapter_id", ""),
            "responses": [],
        }
        if accumulated_text:
            q_copy["responses"].append(
                {"respondent_name": respondent_name, "content": accumulated_text}
            )

        output_questions.append(q_copy)

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    out_file = os.path.join(
        output_dir, f"consultation_questions_with_responses_{base_name}.json"
    )

    with open(out_file, "w", encoding="utf-8") as of:
        json.dump({"questions": output_questions}, of, indent=2, ensure_ascii=False)

    return out_file


def map_consultation_responses_to_questions(
    processed_dir, output_dir, consultation_quest_json
) -> str:
    """
    Maps consultation responses to relevant consultation questions.

    Args:
        processed_dir (str): Directory containing processed response JSON files.
        output_dir (str): Directory where the mapped responses will be stored.
        consultation_quest_json (str): Path to the JSON file containing consultation questions.

    Returns:
        : file path with mapped responses to a consolidated JSON file.
    """

    os.makedirs(processed_dir, exist_ok=True)

    mapped_responses_dir = os.path.join(
        output_dir, "Consultation Paper", "Mapped Responses"
    )
    os.makedirs(mapped_responses_dir, exist_ok=True)

    with open(consultation_quest_json, "r", encoding="utf-8") as f:
        questions_data = json.load(f)
    consultation_questions = questions_data.get("consultation_questions", [])

    response_files = glob.glob(os.path.join(processed_dir, "*.json"))

    with ThreadPoolExecutor() as executor:
        futures = []
        for file_path in response_files:
            futures.append(
                executor.submit(
                    process_single_response_file,
                    file_path,
                    consultation_questions,
                    mapped_responses_dir,
                )
            )
        output_files = [f.result() for f in futures]

    aggregator = {}
    for q in consultation_questions:
        aggregator[q["id"]] = {
            "question": q["question"],
            "chapter_id": q.get("chapter_id", ""),
            "responses": [],
        }

    for out_file in output_files:
        with open(out_file, "r", encoding="utf-8") as of:
            data = json.load(of)
            for q in data["questions"]:
                qid = q["id"]
                for item in q.get("responses", []):
                    aggregator[qid]["responses"].append(
                        {
                            "respondent_name": item["respondent_name"],
                            "content": item["content"],
                        }
                    )

    consolidated_questions = []
    for q in consultation_questions:
        qid = q["id"]
        consolidated_questions.append(
            {
                "id": qid,
                "question": aggregator[qid]["question"],
                "chapter_id": aggregator[qid]["chapter_id"],
                "responses": aggregator[qid]["responses"],
            }
        )

    output_single_json = os.path.join(output_dir, "consultation_questions_mapping.json")
    with open(output_single_json, "w", encoding="utf-8") as outf:
        json.dump(
            {"questions": consolidated_questions}, outf, indent=2, ensure_ascii=False
        )
    return output_single_json
