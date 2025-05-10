import PyPDF2
import fitz

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file using PyPDF2."""
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting text from PDF: {e}"


def extract_pdf_to_markdown(pdf_path: str) -> str:
    """
    Converts a PDF file into Markdown format using PyMuPDF.
    """
    md_text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            md_text += page.get_text("text") + "\n"
        return md_text.strip()
    except Exception as e:
        return f"Error converting PDF to markdown: {e}"
