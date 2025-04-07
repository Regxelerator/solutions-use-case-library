from agents import function_tool
import os
import pymupdf4llm
from typing import Dict


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
    Processed_Folder = os.path.join("output", output_dir)
    os.makedirs(Processed_Folder, exist_ok=True)

    pdf_path = os.path.join(input_dir, pdf_file)
    markdown_text = pymupdf4llm.to_markdown(pdf_path)
    if not os.path.exists(input_dir):
        raise FileNotFoundError(
            f"Input directory '{input_dir}' not found. Please ensure it exists and contains the required files."
        )

    new_file_path = os.path.join(Processed_Folder, pdf_file.replace(".pdf", ".md"))

    with open(new_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_text)

    return {"file_name": pdf_file, "content": markdown_text}
