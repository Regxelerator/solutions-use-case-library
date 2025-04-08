import os
import json
from utils.file_handler import read_json_file, write_to_json_file
from llm.llm_engine import get_openai_resp, get_prompt_for_compliance_assessment


def performing_compliance_check(
    promotion_descriptions_json: str, input_dir: str, output_dir: str
) -> str:
    """
    Performs compliance checks on a list of promotion descriptions.

    Parameters:
    - promotion_descriptions_json (list): A list of promotion description dictionaries (from Step 1).
    - input_dir (str): Directory containing the evaluation criteria JSON.
    - output_dir (str): Directory where the output 'promotion_evaluations.json' will be saved.

    Returns:
    - str: path to 'promotion_evaluations.json' file.
    """

    principles_path = os.path.join(input_dir, "evaluation_criteria.json")
    if not os.path.exists(principles_path):
        print(f"[ERROR] File not found: {principles_path}")
        return None
    promotion_evaluations_file = os.path.join(output_dir, "promotion_evaluations.json")

    promotions_data = read_json_file(promotion_descriptions_json)
    principles_data = read_json_file(principles_path)
    principles = principles_data.get("principles", [])

    principle_chunks = [principles[i : i + 3] for i in range(0, len(principles), 3)]

    promotions_evaluations = []

    for promotion in promotions_data:
        promotion_evaluation = dict(promotion)
        evaluation_results = []

        for chunk in principle_chunks:
            chunk_string = json.dumps(chunk, indent=2)
            promotion_string = json.dumps(promotion, indent=2)

            prompt = get_prompt_for_compliance_assessment(
                chunk_string, promotion_string
            )
            parsed_response = get_openai_resp(prompt)

            if isinstance(parsed_response, dict):
                for k, v in parsed_response.items():
                    result_item = {
                        "principle_id": k,
                        "score": v.get("score"),
                        "justification": v.get("justification"),
                    }
                    evaluation_results.append(result_item)
            elif isinstance(parsed_response, list):
                for item in parsed_response:
                    evaluation_results.append(
                        {
                            "principle_id": item.get("principle_id"),
                            "score": item.get("score"),
                            "justification": item.get("justification"),
                        }
                    )

        promotion_evaluation["evaluation_result"] = evaluation_results
        promotions_evaluations.append(promotion_evaluation)
    write_to_json_file(promotion_evaluations_file, promotions_evaluations, indent=2)
    return promotion_evaluations_file
