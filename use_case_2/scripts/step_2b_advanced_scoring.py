import os
import json
import math
import re
from utils.file_handler import read_json_file, write_to_json_file
from llm.llm_engine import (
    call_openai_with_logprobs,
    get_prompt_for_score_with_justification,
)


def compute_compliance_scoring(
    promotion_descriptions_json: list, input_dir: str, output_dir: str
) -> str:
    """
    Computes the compliance scores

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

    principle_chunks = [principles[i : i + 1] for i in range(0, len(principles), 1)]

    promotions_evaluations = []

    for promotion in promotions_data:
        promotion_evaluation = dict(promotion)
        evaluation_results = []

        for chunk in principle_chunks:
            if not chunk:
                continue

            principle_dict = chunk[0]
            principle_id = principle_dict.get("principle_id", "unknown")

            chunk_string = json.dumps(chunk, indent=2)
            promotion_string = json.dumps(promotion, indent=2)
            prompt = get_prompt_for_score_with_justification(
                chunk_string, promotion_string
            )

            response = call_openai_with_logprobs(prompt)

            if not response:
                continue

            api_response = response.choices[0].message.content

            composite_score = 0.0
            choice_logprobs = response.choices[0].logprobs
            if choice_logprobs and choice_logprobs.content:
                first_token_logprobs = choice_logprobs.content[0]
                top_logprobs_for_first_token = first_token_logprobs.top_logprobs

                for logprob_entry in top_logprobs_for_first_token:
                    token_str = logprob_entry.token
                    token_logprob = logprob_entry.logprob

                    probability = math.exp(token_logprob)

                    try:
                        token_int = int(token_str)
                    except ValueError:
                        token_int = 0

                    composite_score += token_int * probability

            justification_match = re.split(
                r"Justification:s*", api_response, maxsplit=1
            )
            if len(justification_match) == 2:
                justification = justification_match[1].strip()
            else:
                justification = "No justification found."

            score_str = f"{round(composite_score, 2)}"

            result_item = {
                "principle_id": principle_id,
                "score": score_str,
                "justification": justification,
            }
            evaluation_results.append(result_item)

        promotion_evaluation["evaluation_result"] = evaluation_results
        promotions_evaluations.append(promotion_evaluation)

    write_to_json_file(promotion_evaluations_file, promotions_evaluations, indent=2)
    return promotion_evaluations_file
