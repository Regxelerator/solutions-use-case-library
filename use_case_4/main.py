import os
from scripts.step_1a_capture_consultation_info import analyze_consultation_paper
from utils.file_handler import check_file_exists
from scripts.step_1b_segment_consultation_paper import segmenting_consultation_paper
from scripts.step_1c_extract_map_consultation_questions import extracting_and_mapping_questions
from scripts.step_2a_segment_consultation_responses import segmenting_consultation_response
from scripts.step_2b_map_responses_to_questions import map_consultation_responses_to_questions
from scripts.step_3_analyze_consultation_responses import analyzing_consultation_responses
from scripts.step_4_generate_consultation_feedback_reports import consolidating_the_results


def main():
    """
    When this file is executed, the code will run in the following sequence:
    1. step_1a_capture_consultation_info.py
    2. step_1b_segment_consultation_paper.py
    3. step_1c_extract_map_consultation_questions.py
    4. step_2a_segment_consultation_responses.py
    5. step_2b_map_responses_to_questions.py
    6. step_3_analyze_consultation_responses.py
    7. step_4_generate_consultation_feedback_reports.py

    """
    consultation_pdf = "Consultation_Paper/Consultation_Paper.pdf"
    current_dir = os.getcwd()
    input_dir = os.path.join(current_dir, "input")
    output_dir = os.path.join(current_dir, "output")
    consultation_pdf_path = os.path.join(input_dir, consultation_pdf)

    pdf_file_exist = check_file_exists(input_dir, consultation_pdf)

    if not pdf_file_exist:
        print(
            "\n -------------- Consultation Paper Pdf does not exists -----------------"
        )
        return 

    print("\n ----- Step 1: Analyze and Extract Consultation Paper ----- ")
    consult_paper_info_json = analyze_consultation_paper(
        consultation_pdf_path, output_dir
    )

    print("\n ----- Step 2: Segment Consultation Paper ----- ")
    segmented_json_file = segmenting_consultation_paper(
        consultation_pdf_path, output_dir
    )

    if not segmented_json_file:
        print("\n ----- Skipping next steps - Segmented JSON does not exists ----- ")

    print("\n ----- Step 3: Extracting and Mapping Questions ----- ")
    consultation_quest_json = extracting_and_mapping_questions(
        segmented_json_file, output_dir
    )

    print("\n ----- Step 4: Segmenting Consultation Response ----- ")
    segmented_response_dir = segmenting_consultation_response(input_dir, output_dir)

    print("\n ----- Step 5: Mapping Questions ----- ")
    mapped_responses_json = map_consultation_responses_to_questions(
        segmented_response_dir, output_dir, consultation_quest_json
    )

    print(
        "\n ----- Step 6: Analyzing Consultation Responses and Mapping Questions ----- "
    )
    executive_summary_json, consult_quest_summary_json = (
        analyzing_consultation_responses(
            consult_paper_info_json,
            mapped_responses_json,
            consultation_quest_json,
            segmented_json_file,
            output_dir,
        )
    )

    print("\n ----- Step 7: Consolidating Consultation Results ----- ")
    consolidating_the_results(
        consult_quest_summary_json,
        consult_paper_info_json,
        executive_summary_json,
        consultation_quest_json,
        segmented_json_file,
        output_dir,
    )


if __name__ == "__main__":
    main()
