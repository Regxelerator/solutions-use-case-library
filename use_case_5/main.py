import os
from scripts.step_1_extract_and_segment_regulations import (
    extracting_and_segmenting_regulations,
)
from scripts.step_2_define_benchmarking_dimensions import defining_bench_mark_dimensions
from scripts.step_3_perform_comparative_analysis import performing_comparative_analysis
from scripts.step_4_generate_benchmarking_report import generating_benchmarking_report


def main():
    """
    When this file is executed, files will be executed in the following sequence:

    1. step_1_extract_and_segment_regulations.py
    2. step_2_define_benchmarking_dimensions.py
    3. step_3_perform_comparative_analysis.py
    4. step_4_generate_benchmarking_report.py

    """
    input_dir = os.path.join(os.getcwd(), "input")
    print(
        "\n-------------- Step1: Extracting And Segmenting Regulations -----------------"
    )
    extracting_and_segmenting_regulations(input_dir)

    print("\n --------------Step 2: Defining Benchmark Dimensions -----------------")
    defining_bench_mark_dimensions(input_dir)

    print("\n --------------Step 3: Performing Comparative Analysis -----------------")
    final_analysis_output_path = performing_comparative_analysis(input_dir)

    print("\n --------------Step 4: Generating Benchmark Report -----------------")
    generating_benchmarking_report(input_dir, final_analysis_output_path)


if __name__ == "__main__":
    main()
