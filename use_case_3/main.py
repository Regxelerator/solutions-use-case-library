from scripts.step_1_extract_meeting_minutes import extracting_meeting_minutes
from scripts.step_2_analyze_meeting_attendance import analyze_board_meeting_attendance
from scripts.step_3_evaluate_meeting_effectiveness import evaluating_meeting_effectiveness
from scripts.step_4_generate_meeting_analysis_memo import create_board_meeting_analysis_report
import os


def main():
    """
    When this file is executed, the code will run in the following sequence:

    1. extract_meeting_minutes.py
    2. analyze_meeting_attendance.py
    3. evaluate_meeting_effectiveness.py
    4. generate_meeting_analysis_memo.py

    """
    try:
        input_directory = os.path.join(os.getcwd(), "input")
        output_folder_path = os.path.join(os.getcwd(), "output")
        if not os.path.exists(input_directory):
            print(f"Warning: '{input_directory}' does not exist. Creating it now...")
            os.makedirs(input_directory, exist_ok=True)

        if not os.path.exists(output_folder_path):
            print(f"Warning: '{output_folder_path}' does not exist. Creating it now...")
            os.makedirs(output_folder_path, exist_ok=True)
    except Exception as e:
        print(f"Error handling folders: {e}")
        return None, None
    print(" -------------Step 1. Extracting Meeting Minutes ------------------ \n")
    consolidated_file_path = extracting_meeting_minutes(
        input_directory, output_folder_path
    )
    print("\n---------------Step 2. Analyzing Board Meeting Attendance-------------- \n")
    summary_df, df_position_matrix, analysis_response = (
        analyze_board_meeting_attendance(consolidated_file_path)
    )
    print("\n---------------Step 3. Evaluating Meeting Effectiveness -------------- \n")
    df_items_per_meeting, df_combined, analysis_output = (
        evaluating_meeting_effectiveness(consolidated_file_path)
    )
    print(
        "\n---------------Step 4. CREATING Board Meeting Analysis Report -------------- \n"
    )
    create_board_meeting_analysis_report(
        summary_df,
        df_position_matrix,
        analysis_response,
        df_items_per_meeting,
        df_combined,
        analysis_output,
        output_folder_path,
    )
    print("\n---------------- Report Generated Successfully--------------")


if __name__ == "__main__":
    main()
