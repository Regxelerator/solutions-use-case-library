import os
import json
import io
import shutil
from typing import Any, Optional, Tuple, Dict
from docx import Document
from odf.opendocument import load
from odf.text import P
from odf import teletype
from io import BytesIO
import pandas as pd
import pytesseract
from utils.utils import (
    extract_images_from_pdf_content,
    analyze_image_with_openai,
    is_scanned_pdf,
    tesseract_exists,
)
import fitz
from PIL import Image
import base64
from pptx import Presentation
from collections import OrderedDict


class ContentManager:
    def __init__(self, graph_client: Any, artifacts_drive_id: str) -> None:
        """
        Initializes the ContentExtractor with a Microsoft Graph API client.

        Args:
            graph_client: The Microsoft Graph API client
            artifacts_drive_id: The ID of the SharePoint drive where artifacts will be stored
        """
        self.graph = graph_client
        self.headers = graph_client.headers
        self.artifacts_drive_id = artifacts_drive_id

    def get_file_content(
        self, drive_id: str, file_id: str, mime_type: str
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Downloads file content and extracts text based on file type.

        Args:
            drive_id: The ID of the SharePoint drive
            file_id: The ID of the file to process
            mime_type: The MIME type of the file

        Returns:
            Tuple[Optional[bytes], Optional[str]]: Raw content and extracted text
        """
        try:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/content"
            response = self.graph.get(url)
            response.raise_for_status()
            content = response.content
            extracted_text = self._extract_text_from_content(content, mime_type)
            return content, extracted_text
        except Exception as e:
            print(f"Error processing file {file_id}: {e}")
            return None, None

    def _extract_text_from_content(
        self, content: bytes, mime_type: str
    ) -> Optional[str]:
        """
        Extracts text from file content based on MIME type.
        """
        try:
            if (
                mime_type
                == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            ):
                return self._extract_text_from_pptx(content)
            if mime_type == "application/pdf":
                return self._extract_pdf_text(content)
            elif (
                mime_type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                return self._extract_docx_text(content)
            elif mime_type in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel",
                "application/vnd.ms-excel.sheet.macroEnabled.12",
            ]:
                return self._extract_excel_text(content)
            elif mime_type == "application/vnd.oasis.opendocument.text":
                return self._extract_odt_text(content)
            elif mime_type.startswith("image/"):
                image = Image.open(io.BytesIO(content))
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                encoded_image_base64 = base64.b64encode(buffered.getvalue()).decode(
                    "utf-8"
                )
                img_metadata = analyze_image_with_openai(encoded_image_base64)
                return (
                    img_metadata.get("image_description", "")
                    if img_metadata and isinstance(img_metadata, dict)
                    else None
                )
            else:
                print(
                    f"This file type is not handle for text extraction--->{mime_type}"
                )
                return None
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None

    def _extract_odt_text(self, content: bytes) -> Optional[str]:
        """
        Extracts text from an ODT file.
        """
        try:
            doc = load(BytesIO(content))
            paragraphs = doc.getElementsByType(P)
            text = "\n".join([teletype.extractText(p) for p in paragraphs])
            return text.strip()
        except Exception as e:
            print(f"Error extracting ODT text: {e}")
            return None

    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from both text-based and scanned PDFs using PyMuPDF and pytesseract, applying OCR only when the page has image content."""
        full_text = []
        doc = fitz.open(stream=content, filetype="pdf")
        scanable, r = is_scanned_pdf(content)
        for page in doc:
            text = page.get_text("text").strip()
            if text:
                full_text.append(text)
            elif tesseract_exists() and scanable:
                if page.get_images() or len(page.get_drawings()) > 0:
                    pix = page.get_pixmap(dpi=300)
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    ocr_text = ""
                    try:
                        ocr_text = pytesseract.image_to_string(img).strip()
                    except pytesseract.TesseractNotFoundError:
                        ocr_text = ""
                    finally:
                        pass
                    if ocr_text:
                        full_text.append(ocr_text)
                else:
                    continue

        return "\n".join(full_text)

    def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX content."""
        doc = Document(io.BytesIO(content))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _extract_excel_text(self, content: bytes) -> str:
        """Extract text from Excel content."""
        df = pd.read_excel(io.BytesIO(content))
        return df.to_string()

    def _extract_image_text(self, content: bytes) -> str:
        """Extract text from image content using OCR."""
        image = Image.open(io.BytesIO(content))
        text = ""
        if tesseract_exists():
            try:
                text = pytesseract.image_to_string(image)
            except pytesseract.TesseractNotFoundError:
                text = ""
            finally:
                pass
        return text

    def _extract_text_from_pptx(self, content_bytes: bytes) -> Optional[str]:
        try:
            pptx_file = BytesIO(content_bytes)
            presentation = Presentation(pptx_file)
            all_text = ""
            for slide in presentation.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        all_text += shape.text + "\n"
            return all_text
        except Exception as e:
            print(f"Error extracting text from pptx: {e}")
            return ""

    def get_text_content(self, file_obj: Dict[str, Any]) -> Optional[str]:
        """
        Gets text content from a file object.

        Args:
            file_obj: Dictionary containing file information

        Returns:
            Optional[str]: Extracted text content or None if extraction fails
        """
        try:
            drive_id = file_obj.get("parentReference", {}).get("driveId")
            file_id = file_obj.get("id")
            mime_type = file_obj.get("file", {}).get("mimeType")
            if not all([drive_id, file_id, mime_type]):
                return None
            content, text_content = self.get_file_content(drive_id, file_id, mime_type)
            return content, text_content
        except Exception as e:
            print(f"Error getting text content: {e}")
            return None

    def process_and_upload_file(
        self, artifacts_drive_id, drive_id, source_file_id, target_folder_id, metadata
    ):
        """
        Process a file and write a **single** combined `content.json`
        (metadata + content).  The JSON order is
        1) file_name 2) all metadata fields except “name” 3) text.
        """
        try:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{source_file_id}/content"
            response = self.graph.get(url)
            file_content = response.content

            mime_type = metadata.get("mimeType")
            content_data: Dict[str, Any] = {}
            text = metadata.get("content_text")

            if mime_type and not mime_type.startswith("image/"):
                if not text:
                    text = self._extract_text_from_content(file_content, mime_type)
                content_data = {"file_name": metadata.get("name"), "text": text}
            elif mime_type and mime_type.startswith("image/"):
                content_data = {
                    "file_name": metadata.get("name"),
                    "text": metadata.get("img_text"),
                }
                sub_id = self.graph.create_subfolder(artifacts_drive_id, target_folder_id, "images")
                self.graph.upload_file_to_folder(artifacts_drive_id, sub_id, metadata["name"], file_content)

            for k in ("content_text", "subfolderPath", "subfolder"):
                metadata.pop(k, None)
            file_name_value = metadata.pop("name", None)  

            combined = OrderedDict()
            combined["file_name"] = file_name_value or content_data.get("file_name")
            combined.update(metadata)                
            combined["text"] = content_data.get("text")

            combined_bytes = json.dumps(combined, indent=2).encode("utf-8")
            content_file_id = self.graph.upload_file_to_folder(
                artifacts_drive_id, target_folder_id, "content.json", combined_bytes
            )

            if (
                (not metadata.get("is_pdf_scanned", False))
                and mime_type
                and mime_type.startswith("application/pdf")
            ):
                temp_dir, img_count, img_meta = extract_images_from_pdf_content(file_content)
                if img_meta:
                    self.graph.upload_file_to_folder(
                        artifacts_drive_id,
                        target_folder_id,
                        "images.json",
                        json.dumps(img_meta, indent=2).encode("utf-8"),
                    )
                try:
                    if img_count:
                        sub_id = self.graph.create_subfolder(artifacts_drive_id, target_folder_id, "images")
                        for img_name in os.listdir(temp_dir):
                            with open(os.path.join(temp_dir, img_name), "rb") as fh:
                                self.graph.upload_file_to_folder(artifacts_drive_id, sub_id, img_name, fh.read())
                finally:
                    shutil.rmtree(temp_dir)

            return {"content_file_id": content_file_id}
        except Exception as exc:
            print(f"Error processing and uploading file: {exc}")
            raise
