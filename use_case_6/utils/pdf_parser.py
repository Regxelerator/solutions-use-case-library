import pymupdf4llm

def convert_pdf_to_markdown(pdf_path: str) -> str:
    """
    Extracts text from a PDF and converts it to Markdown format.
    
    Parameters:
    pdf_path (str): The file path of the PDF document.
    
    Returns:
    str: The extracted text in Markdown format.
    """
    markdown_text = pymupdf4llm.to_markdown(pdf_path)
    return markdown_text