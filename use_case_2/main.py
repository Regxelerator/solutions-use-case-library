import os
import sys
from scripts.step_1_extract_ads import extracting_text_and_visuals
from scripts.step_2_compliance_check import performing_compliance_check
from scripts.step_3_generate_report import create_excel_from_json


def main():
    """
    When this file is executed, the code will run in the following sequence:
    1. step_1_extract_ads.py
    2. step_2_compliance_check.py --> can be replaced or enhanced  by ( step_2b_advanced_scoring.py)
    3. step_3_generate_report.py

    """
    current_directory = os.getcwd()
    input_dir = os.path.join(current_directory, "input")
    output_dir = os.path.join(current_directory, "output")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    promotions_dir = os.path.join(input_dir, "Promotions")
    if not os.path.exists(promotions_dir) or not os.listdir(promotions_dir):
        print(
            " 'Promotions' directory within input directory is missing or empty. Cannot proceed......."
        )
        os.makedirs(promotions_dir, exist_ok=True)
        sys.exit(1)
    else:
        print(
            "Step1------------------extracting text and visual information------------\n"
        )
        promotion_descriptions_json = extracting_text_and_visuals(
            promotions_dir, output_dir
        )
        if promotion_descriptions_json:
            print("Step2------------------performing compliance check--------\n")
            promotion_evaluations_json = performing_compliance_check(
                promotion_descriptions_json, input_dir, output_dir
            )
            print("Step3------------------creating excel report--------\n")
            if promotion_evaluations_json:
                create_excel_from_json(promotion_evaluations_json, output_dir)
        else:
            print(
                "Failed to extract text and visual information from input files. Exiting......."
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
