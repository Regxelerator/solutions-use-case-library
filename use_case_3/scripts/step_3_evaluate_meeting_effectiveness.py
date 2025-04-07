import os
import pandas as pd

from llm.llm_engine import (
    get_prompt_for_meeting_effectiveness_analysis,
    call_openai_for_analysis,
)

from utils.file_handler import read_from_file


def evaluating_meeting_effectiveness(json_file: str):
    """
    json_file (str) : path to json file of consolidated board meeting data
    """
    if not os.path.exists(json_file):
        print(f"Error: File {json_file} not found.")
        return
    data = read_from_file(json_file)
    meetings_data = data["meetings"]
    if meetings_data is None:
        return

    meeting_item_counts = [
        {
            "Meeting Date": meeting.get("date_of_meeting", "Unknown Date"),
            "Agenda Item Count": len(meeting.get("agenda_items", [])),
        }
        for meeting in meetings_data
    ]
    df_items_per_meeting = pd.DataFrame(meeting_item_counts)

    category_order = [
        "Procedural & Administrative Items",
        "General Performance Reporting",
        "Strategy & Planning",
        "Risk & Control Function Oversight",
        "Other",
    ]

    all_categories = {
        item.get("agenda_item_category", "").strip()
        for meeting in meetings_data
        for item in meeting.get("agenda_items", [])
    }
    category_list = [cat for cat in category_order if cat in all_categories]

    rows = []
    for meeting in meetings_data:
        date_of_meeting = meeting.get("date_of_meeting", "Unknown Date")
        items = meeting.get("agenda_items", [])
        total_meeting_items = len(items)
        counts = {cat: 0 for cat in category_list}
        for item in items:
            category = item.get("agenda_item_category", "").strip()
            if category in counts:
                counts[category] += 1
        row_dict = {"Meeting Date": date_of_meeting}
        for cat in category_list:
            cat_count = counts[cat]
            pct = (cat_count / total_meeting_items * 100) if total_meeting_items else 0
            row_dict[cat] = f"{cat_count} ({pct:.1f}%)"
        rows.append(row_dict)
    df_by_category = pd.DataFrame(rows, columns=["Meeting Date"] + category_list)

    total_category_counts = {cat: 0 for cat in category_list}
    total_items_across_all = sum(
        len(meeting.get("agenda_items", [])) for meeting in meetings_data
    )

    for meeting in meetings_data:
        for item in meeting.get("agenda_items", []):
            category = item.get("agenda_item_category", "").strip()
            if category in total_category_counts:
                total_category_counts[category] += 1

    summary_row = {"Meeting Date": "All Meetings Combined"}
    for cat in category_list:
        cat_total = total_category_counts[cat]
        cat_pct = (
            (cat_total / total_items_across_all * 100) if total_items_across_all else 0
        )
        summary_row[cat] = f"{cat_total} ({cat_pct:.1f}%)"
    df_summary = pd.DataFrame([summary_row], columns=["Meeting Date"] + category_list)
    df_combined = pd.concat([df_by_category, df_summary], ignore_index=True)

    combined_minutes = "\n".join(
        meeting.get("full_text", "") for meeting in meetings_data
    )

    user_prompt = get_prompt_for_meeting_effectiveness_analysis(
        df_items_per_meeting, df_by_category, df_summary, combined_minutes
    )
    analysis_output = call_openai_for_analysis(user_prompt)

    return df_items_per_meeting, df_combined, analysis_output
