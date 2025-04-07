import os
import pandas as pd

from llm.llm_engine import (
    get_prompt_for_attendance_analysis,
    call_openai_for_analysis,
)

from utils.file_handler import read_from_file


def parse_pct(pct_str: str) -> float:
    """Parses a percentage string and converts it to a float.

    Args:
        pct_str (str): A string representing a percentage (e.g., "85.5%").

    Returns:
        float: The numerical value of the percentage, or 0.0 if parsing fails.
    """
    try:
        return float(pct_str.replace("%", ""))
    except ValueError:
        return 0.0


def analyze_board_meeting_attendance(json_file: str) -> tuple:
    """
    Analyzes board meeting attendance and position categories based on a given JSON file.

    :param json_file: Path to the JSON file containing consolidated board meeting data.
    :return: A tuple containing:
             - summary_df: DataFrame summarizing attendance of non-executive directors.
             - df_position_matrix: DataFrame showing position category breakdown by meeting.
             - analysis_response: AI-generated analysis of attendance patterns.
    """
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} not found.")
        return
    data = read_from_file(json_file)
    if data is None:
        print(f"Error: File {json_file} is empty")
        return

    meetings_data = data.get("meetings", [])
    unique_directors = set()
    for meeting in meetings_data:
        attendees = meeting.get("meeting_attendees", [])
        for attendee in attendees:
            name = attendee.get("full name", "").strip()
            position = attendee.get("position", "").lower()
            if "non-executive director" in position:
                unique_directors.add(name)

    unique_directors_list = sorted(unique_directors)
    rows = []
    for meeting in meetings_data:
        row_dict = {"Meeting Date": meeting.get("date_of_meeting", "Unknown Date")}
        for director in unique_directors_list:
            row_dict[director] = "No"
        attendees = meeting.get("meeting_attendees", [])
        for attendee in attendees:
            name = attendee.get("full name", "").strip()
            if name in row_dict:
                row_dict[name] = "Yes"
        rows.append(row_dict)

    df = pd.DataFrame(rows)
    print("Attendance DataFrame (Non-Executive Directors)")
    print(df, "\n")

    attendance_summary = []
    total_meetings = len(df)
    for director in unique_directors_list:
        attended_count = (df[director] == "Yes").sum()
        ratio_str = f"{attended_count}/{total_meetings}"
        attendance_pct_str = (
            f"{(attended_count / total_meetings) * 100:.2f}%"
            if total_meetings > 0
            else "N/A"
        )
        attendance_summary.append(
            {
                "Director": director,
                "Attendance Ratio": ratio_str,
                "Attendance %": attendance_pct_str,
            }
        )

    summary_df = pd.DataFrame(attendance_summary)

    summary_df["Numeric_Pct"] = summary_df["Attendance %"].apply(parse_pct)
    summary_df = summary_df.sort_values("Numeric_Pct", ascending=False).reset_index(
        drop=True
    )

    chair_identifier = "chair"
    chair_rows = summary_df[
        summary_df["Director"].str.lower().str.contains(chair_identifier)
    ]
    non_chair_rows = summary_df[
        ~summary_df["Director"].str.lower().str.contains(chair_identifier)
    ]
    summary_df = pd.concat([chair_rows, non_chair_rows], ignore_index=True)
    summary_df.drop("Numeric_Pct", axis=1, inplace=True)

    print("Attendance Summary - Board Directors (Non-Executive)")
    print(summary_df, "\n")

    position_categories = sorted(
        {
            attendee.get("position_category", "Unknown").strip()
            for meeting in meetings_data
            for attendee in meeting.get("meeting_attendees", [])
        }
    )
    matrix_rows = []
    for meeting in meetings_data:
        row_dict = {"Meeting Date": meeting.get("date_of_meeting", "Unknown Date")}
        for cat in position_categories:
            row_dict[cat] = "0 (0.00%)"
        attendees = meeting.get("meeting_attendees", [])
        total_attendees = len(attendees)
        cat_counts = {
            attendee.get("position_category", "Unknown").strip(): 0
            for attendee in attendees
        }
        for attendee in attendees:
            cat = attendee.get("position_category", "Unknown").strip()
            cat_counts[cat] += 1
        for cat, count in cat_counts.items():
            pct = (count / total_attendees) * 100 if total_attendees > 0 else 0
            row_dict[cat] = f"{count} ({pct:.2f}%)"
        matrix_rows.append(row_dict)

    df_position_matrix = pd.DataFrame(matrix_rows)
    print("Position Category Breakdown by Meeting")
    print(df_position_matrix.to_string(index=False), "\n")

    combined_text = "\n".join(meeting.get("full_text", "") for meeting in meetings_data)
    summary_table_str = summary_df.to_string(index=False)
    position_matrix_str = df_position_matrix.to_string(index=False)

    prompt = get_prompt_for_attendance_analysis(
        summary_table_str, position_matrix_str, combined_text
    )
    analysis_response = call_openai_for_analysis(prompt)

    print("Observations")
    print(analysis_response)
    return summary_df, df_position_matrix, analysis_response
