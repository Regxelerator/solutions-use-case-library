import pymupdf4llm


def extract_pdf_to_markdown(pdf_path: str) -> str:
    """
    Extracts text from a PDF and converts it to Markdown format.
    """
    return pymupdf4llm.to_markdown(pdf_path)
