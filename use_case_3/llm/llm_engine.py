from dotenv import load_dotenv
import openai
import pandas as pd
import json
import os


load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_prompt_for_meeting_metadata_extraction():
    """
    Returns the prompt for extracting metadata from board meeting minutes.
    """
    return """
    You are provided with Board meeting minutes. Your task is to extract information on the meeting's agenda items and to store the information in a structured JSON format with the keys as specified below.

    # Steps

    1. Identify Meeting Date: Locate and extract the meeting date in the format YYYY-MM-DD.
    2. Determine Duration: Find the duration of the meeting measured in minutes. If not disclosed, use "Not disclosed".
    3. Extract Meeting Chair Information: Identify the meeting chair and extract the first name, last name, and position.
    4. Extract Attendee Information: Gather a list of meeting attendees, extracting each person's first name, last name, and position. Add in brackets (Chair) for the meeting chair.

    # Output Format

    The output should be a structured JSON string with the following keys:
    - 'date_of_meeting': String in "YYYY-MM-DD" format.
    - 'duration_of_meeting': String for duration in minutes or "Not disclosed".
    - 'meeting_attendees': A list of objects, each containing 'full name' and 'position'.
    """


def get_prompt_for_position_classification(position):
    """
    Returns the prompt for classifying meeting attendees based on their position.
    """
    return f"""
    You are provided with the position of a board meeting attendee. Your task is to assign one of the following seven categories to the attendee based on his/her position: 
    - Board director (non-executive)
    - Board director (executive)
    - Senior management (CEO)
    - Senior management (Control function holder)
    - Senior management (Business)
    - Senior management (Other)
    - Other staff

    Your response only consists of the category label. You must strictly only use one of the seven labels provided.

    Attendee position: {position}
    """


def get_prompt_for_agenda_item_extraction():
    """
    Returns the prompt for extracting agenda items and structuring them in JSON format.
    """
    return """
    You are provided with Board meeting minutes. Your task is to extract information on the meeting's agenda items and to store the information in a structured JSON format with the keys as specified below.

    # Steps

    1. Identify Agenda Items: List all agenda items mentioned in the meeting minutes.
    2. Summarize Agenda Items: Prepare a one-sentence summary of the nature and purpose of the agenda item.
    3. Assign Order Numbers: For each agenda item, determine its sequential order.
    4. Non-Board Member Association: Associate the relevant non-board members with each agenda item, including their full names.

    # Output Format

    The output should be a structured JSON string (list or object) with the following keys for each agenda item:
    - 'agenda_item': String for the name of the agenda item.
    - 'agenda_item_summary': String for the summary of the agenda item.
    - 'order_number': Integer for the order of the agenda item.
    - 'non_board_members': A list of objects, each containing:
      - 'full_name': String for the member's full name.
    """


def get_prompt_for_agenda_item_classification(agenda_item, agenda_item_summary):
    """
    Returns the prompt for categorizing an agenda item into predefined categories.
    """
    return f"""
    You are provided with the name and summary of a board meeting agenda item. Your task is to assign one of the following five categories to the agenda item: 
    - Procedural & Administrative Items
    - Strategy & Planning
    - General Performance Reporting
    - Risk & Control Function Oversight
    - Other

    Your response only consists of the category label. You must strictly only use one of the five labels provided.

    # Input

    Agenda item name: {agenda_item}
    Agenda item summary: {agenda_item_summary}
    """


def get_prompt_for_attendance_analysis(
    summary_table_str, position_matrix_str, combined_text
):
    """Generates the prompt for attendance analysis based on provided data."""
    return f"""
    You are provided with detailed meeting minutes as well as the output from a meeting attendance. Based on the information provided, you are to prepare an analysis to highlight key attendance patterns. Your analysis should focus on the following two aspects.

    1. Board director attendance
    * Summarize the overall attendance patterns
    * If applicable, highlight whether directors attended meetings in person, remotely or used a hybrid approach
    * In case of low attendance, examine factors that have contributed to low attendance of individual board directors such as board director departures, specialized roles that require only partial presence, or other explicit reasons for apologies provided they are documented in the minutes

    2. Attendance of executive and other key position holders
    * Highlight overall patterns of the attendance of other staff, in terms of volume and nature of (key) position holders in attendance
    * Highlight the degree to which key position holders with responsibilities for risk, compliance and other oversight functions across the second and third line of defence have been in attendance

    # Additional guidance
    * Exclusively rely on the information provided in the detailed minutes and the analysis results
    * Refrain from drawing conclusions which are not supported by the available information
    * Present your conclusion in a professional, objective language
    * Ensure that your conclusions are mutually exclusive and do not duplicate information

    # Output

    * Return your conclusions in the form of succinct bullet points in Markdown (no nested bullets)
    * Group the bullet points under the two dimensions: "Board Director Attendance" and "Attendance of Executive and Key Position Holders"

    # Input

    Director attendance rate analysis: {summary_table_str}
    Position Category Breakdown: {position_matrix_str}
    Board meeting minutes: {combined_text}
    """


def get_prompt_for_meeting_effectiveness_analysis(
    df_items_per_meeting: pd.DataFrame,
    df_by_category: pd.DataFrame,
    df_summary: pd.DataFrame,
    combined_minutes: str,
) -> str:
    """Generates a structured prompt for analyzing board meeting effectiveness.

    Args:
        df_items_per_meeting (pd.DataFrame): DataFrame with number of agenda items per meeting.
        df_by_category (pd.DataFrame): DataFrame categorizing agenda items per meeting.
        df_summary (pd.DataFrame): DataFrame summarizing category distribution across all meetings.
        combined_minutes (str): Full text of board meeting minutes.

    Returns:
        str: Formatted prompt for OpenAI analysis.
    """
    return f"""
    You are provided with a set of board meeting minutes and the results of preliminary analysis on the meetings' agenda items. Your task is to further analyse the information through the lens of board meeting effectiveness with a focus on the following aspects.

    1. Decision- and action-orientation: Assess the degree to which the minutes indicate that agreements were reached during the meetings.
    2. Follow-up: Identify any evidence of effective follow-up on actions discussed in the meetings.
    3. Discussion effectiveness: Evaluate whether there is evidence of effective discussion taking place prior to making decisions.
    4. Balance in contributions: Examine the evidence regarding the balance of contributions from meeting participants, specifically board directors, and determine if any directors appear to have a particularly dominant role.

    # Instructions
    1. Read through the meeting minutes and the existing analysis results.
    2. Identify references to decisions made, actions taken, or agreements reached during the meetings.
    3. Note any mentions of follow-up actions and their status.
    4. Look for indications of discussions preceding decisions, including variety in perspectives and constructive exchanges.
    5. Analyze how contributions are noted, paying attention to the frequency and nature of input from different participants, and identify any individual who dominates the conversation.

    # Additional guidance
    * Exclusively rely on the information provided in the detailed minutes and the analysis results.
    * Refrain from drawing conclusions which are not supported by the available information.
    * Present your conclusion in a professional, objective language.
    * Ensure that your conclusions are mutually exclusive and do not duplicate information.

    # Output format
    * Return your conclusions in the form of succinct bullet points in Markdown (no nested bullets).
    * Group the bullet points under the four review dimensions: Decision- and action-orientation, Follow-up of actions, Discussion effectiveness, Balance in contributions.

    # Input

    Agenda Items (Number of Items per Meeting): {df_items_per_meeting.to_string(index=False)}

    Breakdown by Category (Count and %) per Meeting: {df_by_category.to_string(index=False)}

    Category Share Across All Meetings: {df_summary.to_string(index=False)}

    Meeting Minutes: {combined_minutes}
    """


def call_openai_for_json_extraction(content, user_message):
    try:
        print("---------- Making a request to OpenAI for json extraction -----")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": user_message + "\n\n# Input\n" + content}
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        response_content = response.choices[0].message.content
        return json.loads(response_content)
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON"}
    except openai.APIError as e:
        return {"error": "OpenAI API error", "details": str(e)}
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}


def call_openai_for_position_category(
    position: str,
) -> dict[str, str] | str | dict[str, str]:
    """
    Calls the OpenAI API to classify a given position into a relevant category.

    :param position: The job title or position name that needs classification.
    :return: The category assigned to the position based on AI classification, or an error message if an exception occurs.
    """
    try:
        print("Make a request to OpenAI for position category extraction")
        prompt = get_prompt_for_position_classification(position)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        return {"error": "OpenAI API error", "details": str(e)}
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}


def call_openai_for_agenda_item_category(
    agenda_item_name: str, agenda_item_summary: str
) -> dict[str, str] | str:
    """
    Calls the OpenAI API to classify an agenda item based on its name and summary.

    :param agenda_item_name: The name/title of the agenda item.
    :param agenda_item_summary: A brief summary describing the agenda item.
    :return: The category assigned to the agenda item based on AI classification, or an error message if an exception occurs.
    """
    try:
        print("Make a request to OpenAI for agenda item category extraction")
        prompt = get_prompt_for_agenda_item_classification(
            agenda_item_name, agenda_item_summary
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        return {"error": "OpenAI API error", "details": str(e)}
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}


def call_openai_for_analysis(user_message: str) -> str:
    """Calls OpenAI for analysis and handles API errors.

    Args:
        user_message (str): The message to send to OpenAI for analysis.

    Returns:
        str: The response from OpenAI or an error message if an exception occurs.
    """
    try:
        print("Make a request to OpenAI for analysis")
        response = client.chat.completions.create(
            model="o1",
            messages=[{"role": "user", "content": user_message}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in OpenAI API call: {str(e)}"
