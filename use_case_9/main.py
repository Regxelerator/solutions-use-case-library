import os
from scripts.step_1_convert_to_html import convert_save_pdf_to_html
from scripts.step_2_identify_mda_sections import identify_mda_sections
from scripts.step_3_split_mda_sections import split_mda_sections_into_chapters
from scripts.step_4_filter_mda_sections import filter_mda_sections
from scripts.step_5_synthesize_information import synthesize_annual_report_information
from scripts.step_6_perform_comparative_analysis import comparative_analysis
from scripts.step_7_document_results import generate_risk_comparative_report


def main():
    """
    When this file is executed, the code will run in the following sequence:

    For each year (e.g. 2023, 2024):
        1. Convert PDFs to HTML (for all years first)
        2. Identify MDA-Sections (for all years)
        3. Split MDA-Sections (for all years)
        4. Filter MDA-Sections (for all years)
    """
    PDFTOHTML_PATH = r"REPLACE BY ACTUAL PATH"

    if not os.path.exists(PDFTOHTML_PATH):
        raise FileNotFoundError(f"The path {PDFTOHTML_PATH} does not exist.")

    input_dir = os.path.join(os.getcwd(), "input")
    annual_reports_dir = os.path.join(input_dir, "annual_reports")
    if not os.path.exists(input_dir) or not os.path.isdir(annual_reports_dir):
        raise FileNotFoundError(
            f"Input directory '{input_dir}' not found. Please ensure it exists and contains the annual reports."
        )

    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    year_folders = [
        d for d in os.listdir(annual_reports_dir)
        if os.path.isdir(os.path.join(annual_reports_dir, d))
    ]

    print("======= STEP 1: CONVERTING PDF TO HTML =======\n")
    for year in year_folders:
        year_input_dir = os.path.join(annual_reports_dir, year)
        year_output_dir = os.path.join(output_dir, year)
        interim_output_dir = os.path.join(year_output_dir, "interim_outputs")
        os.makedirs(interim_output_dir, exist_ok=True)

        print(f"--- Year {year} ---")
        convert_save_pdf_to_html(PDFTOHTML_PATH, year_input_dir, interim_output_dir)

    print("======= STEP 2: IDENTIFYING MDA SECTIONS =======\n")
    for year in year_folders:
        interim_output_dir = os.path.join(output_dir, year, "interim_outputs")
        print(f"--- Year {year} ---")
        identify_mda_sections(interim_output_dir)

    print("======= STEP 3: SPLITTING MDA SECTIONS =======\n")
    for year in year_folders:
        interim_output_dir = os.path.join(output_dir, year, "interim_outputs")
        print(f"--- Year {year} ---")
        split_mda_sections_into_chapters(interim_output_dir)

    print("======= STEP 4: FILTERING MDA SECTIONS =======\n")
    for year in year_folders:
        interim_output_dir = os.path.join(output_dir, year, "interim_outputs")
        print(f"--- Year {year} ---")
        filter_mda_sections(interim_output_dir)
        
    print("======= STEP 5: ANALYZING MDA SECTIONS =======\n")
    for year in year_folders:
        interim_output_dir = os.path.join(output_dir, year, "interim_outputs")
        print(f"--- Year {year} ---")
        synthesize_annual_report_information(interim_output_dir)
        
    print("======= STEP 6: COMPARATIVE ANALYSIS =======")
    comparative_analysis(output_dir)
    
    print("======= STEP 7: DOCUMENT RESULTS =======")
    final_doc_path = os.path.join(output_dir, "Comparative_Risk_Analysis_Report.docx")
    generate_risk_comparative_report(output_dir, final_doc_path)


if __name__ == "__main__":
    main()
