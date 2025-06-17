import os
import json
from pathlib import Path
from typing import Dict, Any

from content_management.content_extraction_manager import ContentManager
from services.llm_client import LLMClientFactory


class MetadataManager:
    """
    Pull basic file-system metadata from SharePoint, enrich it with LLM-extracted
    document metadata, and return a consolidated dict.
    """

    def __init__(self, graph_client: Any, output_drive_id: str) -> None:
        self.graph             = graph_client
        self.content_extractor = ContentManager(graph_client, output_drive_id)
        self.output_drive_id   = output_drive_id
        self.llm_factory       = LLMClientFactory()


    def extract_metadata_with_openai(self, text_content: str) -> Dict[str, Any]:
        """
        Given raw document text, call the LLM with the prompt in
        `prompts/PROMPT_METADATA_EXTRACTION.txt` and map the JSON response down
        to six canonical fields.
        """
        try:
            prompt_path = Path(__file__).parent.parent / "prompts" / "PROMPT_METADATA_EXTRACTION.txt"
            with open(prompt_path, encoding="utf-8") as fp:
                system_prompt = fp.read().strip()

            required_fields = [
                "document_name",
                "document_author",
                "document_publication_date",
                "document_type",
                "document_toc",
                "document_summary",
            ]

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": text_content},
            ]
            resp = self.llm_factory.chat_completion("document_metadata", messages)

            if isinstance(resp, str):
                resp = json.loads(resp)
            if not isinstance(resp, dict):
                raise ValueError("LLM returned non-JSON metadata.")

            return {field: resp.get(field) for field in required_fields}
        except Exception:
            return {k: None for k in (
                "document_name",
                "document_author",
                "document_publication_date",
                "document_type",
                "document_toc",
                "document_summary",
            )}


    @staticmethod
    def get_metadata(file_obj) -> Dict[str, Any]:
        """
        Extract a minimal set of file attributes coming directly from Graph.
        """
        try:
            name      = file_obj.get("name")
            extension = os.path.splitext(name)[1].lstrip(".").lower() if name else "unknown"
            return {
                "name":                   name,
                "extension":              extension,
                "size":                   file_obj.get("size"),
                "createdDateTime":        file_obj.get("createdDateTime"),
                "lastModifiedDateTime":   file_obj.get("lastModifiedDateTime"),
                "lastModifiedBy":         file_obj.get("lastModifiedBy", {}).get("user", {}).get("displayName"),
                "webUrl":                 file_obj.get("webUrl"),
                "mimeType":               file_obj.get("file", {}).get("mimeType"),
                "id":                     file_obj.get("id"),
            }
        except Exception as exc:
            print(f"Error extracting basic metadata: {exc}")
            return {}