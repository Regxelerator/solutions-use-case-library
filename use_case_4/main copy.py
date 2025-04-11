import os
import argparse
from scripts.step_1a_capture_consultation_info import analyze_consultation_paper
from utils.file_handler import check_file_exists
from scripts.step_1b_segment_consultation_paper import segmenting_consultation_paper
from scripts.step_1c_extract_map_consultation_questions import extracting_and_mapping_questions
from scripts.step_2a_segment_consultation_responses import segmenting_consultation_response
from scripts.step_2b_map_responses_to_questions import map_consultation_responses_to_questions
from scripts.step_3_analyze_consultation_responses import analyzing_consultation_responses
from scripts.step_4_generate_consultation_feedback_reports import consolidating_the_results
from utils.file_handler import load_json  # Adjust as needed

def run_final_step(output_dir):
    consult_quest_summary_json = load_json(os.path.join(output_dir, "consult_quest_summary.json"))
    consult_paper_info_json = load_json(os.path.join(output_dir, "consult_paper_info.json"))
    executive_summary_json = load_json(os.path.join(output_dir, "executive_summary.json"))
    consultation_quest_json = load_json(os.path.join(output_dir, "consultation_quest.json"))
    segmented_json_file = os.path.join(output_dir, "segmented_consultation.json")
    
    print("\n ----- Final Step: Consolidating Consultation Results ----- ")
    consolidating_the_results(
        consult_quest_summary_json,
        consult_paper_info_json,
        executive_summary_json,
        consultation_quest_json,
        segmented_json_file,
        output_dir,
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--final_only",
        action="store_true",
        help="Run only the final step (requires prior output files to be available)"
    )
    args = parser.parse_args()
    
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "output")
    
    if args.final_only:
        run_final_step(output_dir)
    else:
        # The full pipeline code (steps 1 to 7) would normally go here.
        # For brevity, you might call a function like run_full_pipeline(output_dir)
        print("Running the complete consultation process…")
        # run_full_pipeline(output_dir)

if __name__ == "__main__":
    main()