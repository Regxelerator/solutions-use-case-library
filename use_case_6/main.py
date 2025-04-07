import os
import sys
from scripts.step_1_segmenting_outsourcing_agreement import segment_outsourcing_agreement
from scripts.step_2_generate_embeddings import create_embeddings
from scripts.step_3_mapping_provisions_to_req import map_requirements_to_agreement
from scripts.step_4_perfom_compliance_assessment import performing_compliance_assessment
from scripts.step_5_consolidate_results import create_final_report


def main():
    """
    When this file is executed, files will be executed in the following sequence:

    1. step_1_segmenting_outsourcing_agreement.py
    2. step_2_generate_embeddings.py
    3. step_3_mapping_provisions_to_req.py
    4. step_4_perform_compliance_assessment.py
    5. step_5_consolidate_results.py

    """
    input_dir = os.path.join(os.getcwd(), "input")
    pdf_file = os.path.join(input_dir, "Outsourcing_Agreement.pdf")

    if not os.path.exists(pdf_file):
        print(f"Error: The file '{pdf_file}' does not exist. Exiting.")
        sys.exit(1)

    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    print("-------------Step 1: Starting segmenting the agreement file ---------------------\n")
    outsourcing_agreement_json_path = segment_outsourcing_agreement(pdf_file, output_dir)

    print("-------------------Step 2: Starting generating embeddings-----------------------------\n")
    requirements_json = os.path.join(input_dir, "Outsourcing_Requirements.json")
    if not os.path.exists(requirements_json):
        print(f"Error: The file '{requirements_json}' does not exist. Exiting.")
        sys.exit(1)
    agreement_embeddings_path, requirements_embeddings_file_path = create_embeddings(
        outsourcing_agreement_json_path, requirements_json, output_dir
    )

    print("---------------------Step 3: Starting mapping requirements----------------------\n")
    requirement_agreement_matches_file_path = map_requirements_to_agreement(
        agreement_embeddings_path, requirements_embeddings_file_path, output_dir
    )

    print("-------------Step 4: Performing compliance assessment----------------------\n")
    contract_compliance_assessment_file_path = performing_compliance_assessment(
        requirement_agreement_matches_file_path, output_dir
    )

    if contract_compliance_assessment_file_path is not None:
        print("-------------Step 5: Final output generating ----------------------\n")
        create_final_report(contract_compliance_assessment_file_path, output_dir)


if __name__ == "__main__":
    main()
