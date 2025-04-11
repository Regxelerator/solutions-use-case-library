import os
import math
from utils.file_handler import load_json_file, write_to_json_file
from llm.llm_engine import (
    get_prompt_for_contract_summary,
    get_prompt_for_compliance_assessment,
    get_prompt_for_compliance_score,
    get_response_from_openai,
    get_compliance_score_from_openai,
)


def performing_compliance_assessment(req_agree_match_file_path: str, output_dir: str):
    """
    Loads matched requirement-agreement data and performs compliance assessment.

    Args:
        req_agree_match_file_path (str): Path to the JSON file containing requirement-agreement matches.
        output_dir (str): Path to the directory where the results will be saved.

    Returns:
         str or None:
            The function returns the path of the output JSON file containing the assessment results.
            If an error occurs and the process is stopped, it returns `None`.
    """

    requirements_data = load_json_file(req_agree_match_file_path)
    updated_data = []

    for req_obj in requirements_data:
        requirement_id = req_obj.get("id", "")
        requirement_label = req_obj.get("requirement_label", "")
        requirement_description = req_obj.get("requirement_description", "")
        matches = req_obj.get("matches", [])

        matches_text = ""
        for match_item in matches:
            lu_id = match_item.get("logical_unit_id", "")
            lu_content = match_item.get("logical_unit_content_full", "")
            matches_text += f"LOGICAL UNIT ID: {lu_id} CONTENT:{lu_content}-----"

    
        try:
            prompt1 = get_prompt_for_contract_summary(
                requirement_description, matches_text
            )
            response_step1 = get_response_from_openai(prompt1, "o3-mini")
            contract_contents = response_step1.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during contract summary generation: {e}")
            return None

        try:
            prompt2 = get_prompt_for_compliance_assessment(
                requirement_description, contract_contents
            )
            response_step2 = get_response_from_openai(prompt2, "o1")
            compliance_assessment = response_step2.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during compliance assessment generation: {e}")
            return None

        try:
            prompt3 = get_prompt_for_compliance_score(
                requirement_description, compliance_assessment
            )
            response_step3 = get_compliance_score_from_openai(prompt3, model="gpt-4o")
            raw_api_response = response_step3.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during compliance score generation: {e}")
            return None

        compliance_score_numeric = 0.0

        choice_logprobs = response_step3.choices[0].logprobs
        if choice_logprobs and choice_logprobs.content:
            first_token_data = choice_logprobs.content[0]
            top_logprobs_for_first_token = first_token_data.top_logprobs

            sum_val = 0.0
            sum_prob = 0.0

            for logprob_entry in top_logprobs_for_first_token:
                token_str = logprob_entry.token
                token_logprob = logprob_entry.logprob

                probability = math.exp(token_logprob)
                try:
                    possible_int = int(token_str)
                    if 0 <= possible_int <= 10:
                        sum_val += possible_int * probability
                        sum_prob += probability
                except ValueError:
                    pass

            if sum_prob > 0:
                compliance_score_numeric = sum_val / sum_prob
            else:
                try:
                    fallback_val = int(raw_api_response)
                    if fallback_val < 0 or fallback_val > 10:
                        fallback_val = 0
                    compliance_score_numeric = float(fallback_val)
                except ValueError:
                    compliance_score_numeric = 0.0
        else:
            try:
                fallback_val = int(raw_api_response)
                if 0 <= fallback_val <= 10:
                    compliance_score_numeric = float(fallback_val)
                else:
                    compliance_score_numeric = 0.0
            except ValueError:
                compliance_score_numeric = 0.0

        compliance_score_final = round(compliance_score_numeric, 2)

        new_req_obj = dict(req_obj)
        new_req_obj["contract_contents"] = contract_contents
        new_req_obj["compliance_assessment"] = compliance_assessment
        new_req_obj["compliance_score"] = compliance_score_final

        updated_data.append(new_req_obj)
    contract_assessment_file_path = os.path.join(
        output_dir, "Results_Outsourcing_Contract_Assessment.json"
    )
    write_to_json_file(contract_assessment_file_path, updated_data, indent=4)
    return contract_assessment_file_path
