import os
from utils.pdf_parser import (
    extract_text_from_docx,
    extract_text_from_pdf,
    identify_file_type,
)

from llm.llm_engine import (
    call_openai_for_json_extraction,
    call_openai_for_position_category,
    call_openai_for_agenda_item_category,
    get_prompt_for_meeting_metadata_extraction,
    get_prompt_for_agenda_item_extraction,
)


def extracting_meeting_minutes(folder_path: str, output_file_path: str) -> str:
    """
    Extracting and standardizing meetings minutes .

    Params:
        file_path (str): Path to the input directory.
        output_file_path (str) : path to json file save consolidated board meeting data
    return:
         output_file_path(str): path to consolidated board meeting data
    """
    folder_path = os.path.join(folder_path, "Board_Meeting_Minutes")
    if not os.path.exists(folder_path):
        print(f"{folder_path} does not exist")
        return
    consolidated_data = {"meetings": []}

    for filename in os.listdir(folder_path):
        if filename.startswith("~$"):
            continue

        file_path = os.path.join(folder_path, filename)
        print(f"{filename} -file inputed from input directory")
        if os.path.isfile(file_path):
            file_type = identify_file_type(file_path)

            extracted_text = (
                extract_text_from_docx(file_path)
                if file_type == "docx"
                else extract_text_from_pdf(file_path)
            )

            data_meeting = call_openai_for_json_extraction(
                extracted_text, get_prompt_for_meeting_metadata_extraction()
            )

            if "meeting_attendees" in data_meeting:
                for attendee in data_meeting["meeting_attendees"]:
                    attendee["position_category"] = call_openai_for_position_category(
                        attendee.get("position", "")
                    )

            data_agenda = call_openai_for_json_extraction(
                extracted_text, get_prompt_for_agenda_item_extraction()
            )

            if "agenda_items" in data_agenda:
                for item in data_agenda["agenda_items"]:
                    item["agenda_item_category"] = call_openai_for_agenda_item_category(
                        item.get("agenda_item", ""), item.get("agenda_item_summary", "")
                    )

            meeting_data = {
                "file_name": filename,
                "full_text": extracted_text,
                "date_of_meeting": data_meeting.get("date_of_meeting", ""),
                "duration_of_meeting": data_meeting.get("duration_of_meeting", ""),
                "meeting_attendees": data_meeting.get("meeting_attendees", []),
                "agenda_items": data_agenda.get("agenda_items", []),
            }
            consolidated_data["meetings"].append(meeting_data)

    output_file_path = os.path.join(output_file_path, "consolidated_data.json")
    return output_file_path
