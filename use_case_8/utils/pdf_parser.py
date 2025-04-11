from agents import function_tool
import os
from typing import Dict
import PyPDF2


def convert_pdf_to_markdown(file_path: str) -> str:
    """Extract text from a PDF file.

    :param file_path: Path to the PDF file.
    :return: Extracted text as a string or an error message.
    """
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


@function_tool
async def content_extraction(pdf_file: str, input_dir: str) -> Dict[str, str]:
    """
    Extracts the content from a PDF file and saves it as a Markdown (.md) file.

    Args:
    pdf_file (str): The name of the PDF file to be processed.
    input_dir (str): The directory containing the PDF file.

    Returns:
    dict: A dictionary containing the original PDF file name and the extracted content.
    """

    output_dir = os.path.join(os.getcwd(), "output")
    processed_folder = os.path.join("output", output_dir)
    os.makedirs(processed_folder, exist_ok=True)

    pdf_path = os.path.join(input_dir, pdf_file)
    markdown_text = convert_pdf_to_markdown(pdf_path)
    if not os.path.exists(input_dir):
        raise FileNotFoundError(
            f"Input directory '{input_dir}' not found. Please ensure it exists and contains the required files."
        )

    new_file_path = os.path.join(processed_folder, pdf_file.replace(".pdf", ".md"))

    with open(new_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_text)

    return {"file_name": pdf_file, "content": markdown_text}
