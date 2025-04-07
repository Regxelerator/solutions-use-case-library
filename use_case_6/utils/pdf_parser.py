import fitz  # PyMuPDF


def convert_pdf_to_markdown(pdf_path: str) -> str:
    """
    Extracts the content of a PDF file and converts it to a simple Markdown format.

    Parameters:
    pdf_path (str): The file path of the PDF document.

    Returns:
    str: The extracted text in Markdown format.
    """
    doc = fitz.open(pdf_path)
    markdown_text = ""

    # Extract text from all pages
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        markdown_text += text + "\n\n---\n\n"
    return markdown_text
