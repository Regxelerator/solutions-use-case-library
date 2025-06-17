import os
import requests
import base64
from PIL import Image
import io
import fitz
import json
import tempfile
from docx import Document
import pandas as pd
from pathlib import Path
from typing import Union, Dict
from odf.opendocument import load
from odf.text import P, H
from services.llm_client import LLMClientFactory
from odf import teletype
from pymupdf4llm import to_markdown as pdf_to_md
import pytesseract
import shutil
import platform


def _load_prompt(txt_name: str) -> str:
    """
    Small helper: read a prompt template that lives in prompts/<txt_name>.
    Raises FileNotFoundError if the file is missing.
    """
    prompt_path = Path(__file__).parent.parent / "prompts" / txt_name
    with open(prompt_path, encoding="utf-8") as fp:
        return fp.read().strip()


def write_into_markdown_file(
    file_path: str, text: str, encoding: str = "utf-8"
) -> bool:
    """
    Writes the given text to a file, handling potential errors.

    Args:
        file_path (str): The name of the file to write to.
        text (str): The text to write to the file.
        encoding (str, optional): The character encoding to use. Defaults to "utf-8".

    Returns:
        bool: True if the write was successful, False otherwise.
    """
    try:
        with open(file_path, "w", encoding=encoding) as file:
            file.write(text)
        return True
    except (OSError, IOError) as e:
        print(f"Error writing to file {file_path}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while writing to {file_path}: {e}")
        return False


def extract_images_from_pdf_content(pdf_data):
    """extract images from pdf content"""
    temp_dir = tempfile.mkdtemp()
    if not pdf_data:
        return temp_dir, 0, {}
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        image_count = 0
        image_metadata_dict = {}

        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            images = page.get_images(full=True)

            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]

                image_name = f"page_{page_number + 1}_image_{img_index + 1}.png"
                image_path = os.path.join(temp_dir, image_name)

                image = Image.open(io.BytesIO(image_data))
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format="PNG")
                img_byte_arr = img_byte_arr.getvalue()
                encoded_img = base64.b64encode(img_byte_arr).decode("utf-8")

                img_metadata = analyze_image_with_openai(encoded_img)
                if img_metadata:
                    img_name = img_metadata.get("image_name", "").strip().lower()
                    if img_name in [
                        "NOT RELEVANT",
                        "",
                        "unknown",
                        "not_relevant",
                        "untitled",
                        "untitled_image",
                        "not relevant",
                    ]:
                        img_metadata["image_name"] = "Not Relevant"
                        img_metadata["image_description"] = "Not Relevant"
                    img_index_suffix = img_index + 1
                    image_metadata_dict.update(
                        {
                            f"image_name_{img_index_suffix}": img_metadata.pop(
                                "image_name", "Not Relevant"
                            ),
                            f"image_description_{img_index_suffix}": img_metadata.pop(
                                "image_description", "Not Relevant"
                            ),
                        }
                    )
                image.save(image_path)
                image_count += 1
        return temp_dir, image_count, image_metadata_dict
    except Exception as e:
        print(f"Error in extract_images_from_pdf_content: {str(e)}")
        return temp_dir, 0, {}


def analyze_image_with_openai(image_base64: str) -> Union[str, None, Dict[str, str]]:
    """
    Analyzes an image using OpenAI's GPT-4 Vision model.

    Args:
        image_base64 (str): Base64 encoded image data
    Returns:
        str: The model's response to the image analysis

    Raises:
        ValueError: If OpenAI API key is not set in environment variables
        Exception: If there's an error in the API call or response processing
    """
    prompt_path = Path(__file__).parent.parent.joinpath(
        "prompts", "PROMPT_IMAGE_EXTRACTION_REGULAR.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as file:
        _IMAGE_ANALYSIS_PROMPT_SYSTEM = file.read().strip()

    if not _IMAGE_ANALYSIS_PROMPT_SYSTEM:
        print("IMAGE ANALYSIS PROMPT NOT FOUND")
        return None
    _IMAGE_ANALYSIS_PROMPT_SYSTEM = _IMAGE_ANALYSIS_PROMPT_SYSTEM.replace(
        "{image_data}", image_base64
    )
    try:
        messages = [
            {"role": "system", "content": _IMAGE_ANALYSIS_PROMPT_SYSTEM},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    }
                ],
            },
        ]
        response = LLMClientFactory().chat_completion("image_analysis_regular", messages)
        if isinstance(response, str):
            response = json.loads(response)
        if isinstance(response, dict):
            return response
        else:
            raise ValueError(f"Image analysis response not is valid: {response}.")
    except Exception:
        return None


def extract_text_from_docx(file_path):
    """
    Extracts text from a DOCX file using python-docx.

    Args:
        file_path (str): Path to the .docx file

    Returns:
        str: Extracted plain text

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file has no readable content
        Exception: For other unexpected errors
    """
    try:
        doc = Document(file_path)
        text = [para.text for para in doc.paragraphs if para.text.strip()]
        print("extract text from docx")
        if not text:
            print("No readable text found in the DOCX file.")
            return ""

        return "\n".join(text)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX file: {str(e)}")


def extract_text_from_odt(file_path):
    """
    Extracts text from an ODT file using the odfpy library.

    Args:
        file_path (str): Path to the .odt file

    Returns:
        str: Extracted plain text

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file cannot be parsed or has no text content
        Exception: For any other unexpected errors
    """
    try:
        text_doc = load(file_path)
        all_text = []

        for element in text_doc.getElementsByType(P) + text_doc.getElementsByType(H):
            para_text = teletype.extractText(element)
            if para_text.strip():
                all_text.append(para_text)

        if not all_text:
            raise ValueError("No text content found in the ODT file.")

        return "\n".join(all_text)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Failed to extract text from ODT file: {str(e)}")


def extract_text_from_excel(file_path):
    try:
        df_list = pd.read_excel(file_path, sheet_name=None)
        combined = ""
        for sheet_name, df in df_list.items():
            combined += f"## {sheet_name}\n\n"
            combined += df.to_markdown(index=False) + "\n\n"
        return combined
    except Exception as e:
        return f"Error reading Excel file: {str(e)}"


def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def convert_pdf_to_markdown(pdf_path):
    """
    Converts a PDF to markdown-style text using pymupdf4llm.
    Falls back to OCR using PyMuPDF + pytesseract if needed.
    """
    try:
        markdown = pdf_to_md(pdf_path)
        if markdown.strip():
            return markdown
        else:
            raise ValueError()
    except Exception:
        try:
            with open(pdf_path, "rb") as f:
                content_bytes = f.read()
            scanable, r = is_scanned_pdf(content_bytes)
            full_text = []
            doc = fitz.open(pdf_path)
            for i in range(len(doc)):
                page = doc.load_page(i)
                text = page.get_text()
                if text and text.strip():
                    full_text.append(text)
                elif (
                    tesseract_exists()
                    and scanable
                    and (page.get_images() or page.get_drawings())
                ):
                    ocr_text = ""
                    pix = page.get_pixmap(dpi=300)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    try:
                        ocr_text = pytesseract.image_to_string(img)
                        full_text.append(ocr_text)
                    except pytesseract.TesseractNotFoundError:
                        ocr_text = ""
                    finally:
                        pass
            return "\n".join(full_text)
        except Exception:
            return ""


def download_and_convert_to_markdown(ms_graph_client, drive_id, file_id, ext) -> str:
    """
    Downloads a file from a SharePoint/Graph URL and converts it to Markdown-like text.
    Supports: PDF, DOCX, XLSX, TXT

    Args:
        access_token (str): Microsoft Graph access token

    Returns:
        str: Markdown-style converted text
    """
    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
            response = ms_graph_client.download_file(drive_id, file_id)
            if response.status_code != 200:
                print(
                    f"Error downloading file to extract content for segmentation: {response.url}"
                )
                return ""
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name
        if ext == "pdf":
            return convert_pdf_to_markdown(tmp_file_path)
        elif ext in ["doc", "docx"]:
            text = extract_text_from_docx(tmp_file_path)
            return text
        elif ext == "odt":
            return extract_text_from_odt(tmp_file_path)
        elif ext == "xlsx":
            return extract_text_from_excel(tmp_file_path)
        elif ext == "txt":
            return extract_text_from_txt(tmp_file_path)
        else:
            print(f"This {ext} extension is not handle for markdown extraction")
            return ""
    except Exception as e:
        print("\nError in download_and_convert_to_markdown:", e)
        return ""
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


def extract_text_from_image_with_openai(image_base64: str) -> str:
    """
    Extracts text from an image using OpenAI's GPT-4 Vision model.

    Args:
        image_base64 (str): Base64 encoded image data
    Returns:
        str: The extracted text from the image
    """
    try:
        prompt_path = Path(__file__).parent.parent.joinpath(
            "prompts", "PROMPT_IMAGE_EXTRACTION_OCR.txt"
        )
        if not prompt_path.exists():
            print(f"Prompt file not found at: {prompt_path}")
            return ""

        with open(prompt_path, "r", encoding="utf-8") as file:
            _IMAGE_ANALYSIS_PROMPT_SYSTEM = file.read().strip()

        if not _IMAGE_ANALYSIS_PROMPT_SYSTEM:
            print("IMAGE ANALYSIS PROMPT NOT FOUND")
            return ""

        _IMAGE_ANALYSIS_PROMPT_SYSTEM = _IMAGE_ANALYSIS_PROMPT_SYSTEM.replace(
            "{image_data}", image_base64
        )
        messages = [{"role": "system", "content": _IMAGE_ANALYSIS_PROMPT_SYSTEM}]
        response = LLMClientFactory().chat_completion(
            "image_text_extraction", messages
        )
        return response.strip() if response else ""
    except Exception:
        return ""


def is_scanned_pdf(pdf_stream, text_threshold=0.3):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    total_pages = len(doc)
    text_pages = 0

    for page in doc:
        text = page.get_text().strip()
        if text:
            text_pages += 1

    text_ratio = text_pages / total_pages if total_pages > 0 else 0
    return text_ratio < text_threshold, text_ratio


def tesseract_exists():
    """Check if tesseract is in PATH or at default Windows location"""
    if shutil.which("tesseract"):
        return True
    if platform.system() == "Windows":
        return os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    return False
