import hashlib
import os
import uuid
import json
from typing import Dict, Any
from content_management.content_extraction_manager import ContentManager
from pathlib import Path
from services.llm_client import LLMClientFactory


class MetadataManager:
    def __init__(self, graph_client: Any, artifacts_drive_id: str) -> None:
        """
        Initializes the MetadataExtractor with a Microsoft Graph API client.

        Args:
            graph_client: The Microsoft Graph API client
            artifacts_drive_id: The ID of the SharePoint drive where artifacts will be stored
        """
        self.graph = graph_client
        self.content_extractor = ContentManager(graph_client, artifacts_drive_id)
        self.artifacts_drive_id = artifacts_drive_id
        self.folder_file_map: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.llm_factory = LLMClientFactory()

    @staticmethod
    def generate_uuid_from_filename(document_name: str) -> uuid.UUID:
        """
        Generates a UUID from a filename. It always remains same because of hashing.
        Returns:
        """
        hash_object = hashlib.sha256(document_name.encode())
        hex_digest = hash_object.hexdigest()
        generated_uuid = uuid.UUID(hex_digest[:32])
        return generated_uuid

    def extract_metadata_with_openai(self, text_content: str) -> Dict[str, Any]:
        """
        Extracts metadata from document text using OpenAI API with specific prompt.

        Args:
            text_content: The extracted text content from the document

        Returns:
            Dict containing extracted metadata
        """
        try:
            prompt_path = Path(__file__).parent.parent.joinpath(
                "prompts", "PROMPT_METADATA_EXTRACTION.txt"
            )
            with open(prompt_path, "r", encoding="utf-8") as p_file:
                _DOCUMENT_PROMPT_SYSTEM = p_file.read().strip()

            if not _DOCUMENT_PROMPT_SYSTEM:
                raise Exception("DOCUMENT META DATA PROMPT NOT FOUND")

            required_fields = [
                "document_name",
                "document_author",
                "document_publication_date",
                "document_type",
                "document_toc",
                "document_summary",
            ]
            messages = [
                {"role": "system", "content": _DOCUMENT_PROMPT_SYSTEM},
                {"role": "user", "content": text_content},
            ]
            response = self.llm_factory.chat_completion(
                "document_meta_data_model", messages
            )
            if isinstance(response, str):
                response = json.loads(response)
            if isinstance(response, dict):
                return {field: response.get(field, None) for field in required_fields}
            raise ValueError("Document Metadata Extraction Response is not JSON.")
        except Exception:
            return {
                "document_name": None,
                "document_author": None,
                "document_publication_date": None,
                "document_type": None,
                "document_toc": None,
                "document_summary": None,
            }

    def get_metadata(self, file_obj) -> Dict[str, Any]:
        """
        Extracts metadata for a given file.
        """
        try:
            name = file_obj.get("name", None)
            extension = (
                os.path.splitext(name)[1].lstrip(".").lower() if name else "unknown"
            )
            metadata = {
                "name": name,
                "extension": extension,
                "size": file_obj.get("size"),
                "createdDateTime": file_obj.get("createdDateTime"),
                "lastModifiedDateTime": file_obj.get("lastModifiedDateTime"),
                "lastModifiedBy": file_obj.get("lastModifiedBy", {})
                .get("user", {})
                .get("displayName"),
                "webUrl": file_obj.get("webUrl"),
                "mimeType": file_obj.get("file", {}).get("mimeType"),
                "id": file_obj.get("id"),
            }
            return metadata
        except Exception as e:
            print(f"Error extracting metadata for file: {e}")
            return {}
