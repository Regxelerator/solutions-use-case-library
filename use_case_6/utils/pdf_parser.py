import PyPDF2


def convert_pdf_to_markdown(file_path: str) -> str:
    """Extracts text from a PDF file.

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