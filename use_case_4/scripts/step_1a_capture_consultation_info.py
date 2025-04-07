from utils.file_handler import process_file, save_json
from llm.llm_engine import (
    openai_chat_request,
    get_prompt_to_generate_consultation_summary,
)


def analyze_consultation_paper(consultation_pdf: str, output_path: str) -> str:
    """
    Extracts text from a consultation paper PDF, processes it using an LLM,
    and saves the extracted information as a JSON file.
    Args:
        consultation_pdf (str): Path to the input PDF file.
        output_path (str): Directory to save the extracted JSON data.
    Returns:
        return extracted data with JSON file.
    """

    markdown_text = process_file(consultation_pdf)
    prompt = get_prompt_to_generate_consultation_summary(markdown_text)
    response = openai_chat_request(prompt)
    extracted_json_data = (
        response if isinstance(response, dict) else {"response": response}
    )
    json_file_path = save_json(
        extracted_json_data, output_path, "consultation_paper_information.json"
    )
    return json_file_path
