import fitz


def extract_pdf_to_markdown(pdf_path: str) -> str:
    """
    Converts a PDF file into Markdown format.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        return markdown_text(str): extracted text"
    """
    doc = fitz.open(pdf_path)
    markdown_text = ""
    for page in doc:
        markdown_text += page.get_text("text")
    return markdown_text
