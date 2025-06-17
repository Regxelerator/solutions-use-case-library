import hashlib
import uuid
from typing import Dict, Any

from content_management.content_extraction_manager import ContentManager
from content_management.metadata_manager import MetadataManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from tqdm import tqdm

from utils.utils import is_scanned_pdf

class DirectoryManager:

    EXTRACTED_SUFFIX = " - Extracted Documents"

    def _target_root_name(self, entity: str) -> str:
        return f"{entity}{self.EXTRACTED_SUFFIX}"

    def __init__(
        self, graph_client: Any, drive_id: str, output_drive_id: str = None
    ) -> None:
        """
        Initializes the Directory Manager with a Microsoft Graph API client.
        Args:
            graph_client: The Microsoft Graph API client
            drive_id: The ID of the SharePoint drive where folders stored
        """
        self.graph = graph_client
        self.drive_id = drive_id
        self.output_drive_id = output_drive_id
        self.content_extractor = ContentManager(graph_client, output_drive_id)
        self.folder_file_map: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.meta_data_obj = MetadataManager(
            self.graph, output_drive_id=self.output_drive_id
        )

    @staticmethod
    def generate_uuid_from_filename(document_name: str) -> uuid.UUID:
        hash_object = hashlib.sha256(document_name.encode())
        hex_digest = hash_object.hexdigest()
        generated_uuid = uuid.UUID(hex_digest[:32])
        return generated_uuid

    def get_source_folder_children(self, _drive_id: str, _folder_name: str):
        try:
            folder_url = (
                f"https://graph.microsoft.com/v1.0/drives/{_drive_id}/root:/{_folder_name}:/children"
            )
            res_folder = self.graph.get(folder_url)
            res_folder.raise_for_status()
            folder_contents = res_folder.json().get("value", [])
            if not folder_contents:
                print(f"Folder '{_folder_name}' is empty. Skipping")
                return {}
        except Exception as exc:
            raise Exception(exc)

    def process_folder_recursive(self, folder_id, folder_name, _folder_file_mappings):
        """
        Recursively processes a folder and returns a mixed mapping:
        {
            "file_uuid": {...},        # for files
            "Subfolder": { ... }       # for subfolders
        }
        """
        try:
            folder_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{folder_id}/children"
            res_folder = self.graph.get(folder_url)
            res_folder.raise_for_status()
            folder_contents = res_folder.json().get("value", [])
            for child in folder_contents:
                if child.get("folder"):
                    subfolder_name = child["name"]
                    subfolder_id = child["id"]
                    subfolder_map = self.process_folder_recursive(
                        subfolder_id, subfolder_name, _folder_file_mappings
                    )
                    if subfolder_map and isinstance(subfolder_map, dict):
                        for _doc_key, _doc_value in subfolder_map.items():
                            sub_file = _folder_file_mappings.get(_doc_key)
                            if sub_file:
                                sub_file["subfolderPath"] = folder_url
                                sub_file["subfolder"] = True
                else:
                    file_uuid = str(
                        self.generate_uuid_from_filename(child.get("name"))
                    )
                    meta_data = self.meta_data_obj.get_metadata(child)
                    bytes_content, text_content = (
                        self.content_extractor.get_text_content(child)
                    )
                    openai_metadata = (
                        self.meta_data_obj.extract_metadata_with_openai(text_content)
                        if text_content
                        else {
                            "document_name": None,
                            "document_author": None,
                            "document_publication_date": None,
                            "document_type": None,
                            "document_toc": None,
                            "document_summary": None,
                        }
                    )
                    meta_data.update(openai_metadata)
                    if meta_data.get("mimeType", "").startswith("image/"):
                        meta_data["img_text"] = text_content
                    if meta_data.get("mimeType", "").startswith("application/pdf"):
                        meta_data["is_pdf_scanned"], _ = is_scanned_pdf(bytes_content)

                    meta_data["content_text"] = text_content or None
                    _folder_file_mappings[file_uuid] = meta_data
            return _folder_file_mappings
        except Exception as e:
            print(f"Exception processing folder '{folder_name}': {e}")
            return {}

    def extract_folder_and_files(self, drive_id: str, entity_name=None) -> None:
        """
        Retrieves all first-level folders and their files from the given drive in parallel,
        processes them, and builds a combined folder-file metadata mapping.
        """
        try:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
            res = self.graph.get(url)
            res.raise_for_status()
            items = res.json().get("value", [])

            lock = threading.Lock()
            combined_folder_file_map: Dict[str, Dict[str, Any]] = {}
            folder_file_mappings: Dict[str, Dict[str, Any]] = {}
            if entity_name:
                entity_folder = next(
                    (
                        item
                        for item in items
                        if item.get("name") == entity_name and item.get("folder")
                    ),
                    None,
                )
                if not entity_folder:
                    print(f"Could not find folder '{entity_name}'")
                    return
                nested_map = self.process_folder_recursive(
                    entity_folder["id"], entity_folder["name"], folder_file_mappings
                )
                with lock:
                    combined_folder_file_map[entity_folder["name"]] = nested_map
            else:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = {
                        executor.submit(
                            self.process_folder_recursive,
                            item["id"],
                            item["name"],
                            folder_file_mappings,
                        ): item["name"]
                        for item in items
                        if item.get("folder")
                    }
                    for future in tqdm(
                        as_completed(futures),
                        total=len(futures),
                        ncols=100,
                        bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} {unit} • ETA: {remaining} • {rate_fmt}",
                        desc="\n Processing",
                        unit="folder",
                    ):
                        folder_name = futures[future]
                        try:
                            result_map = future.result()
                            with lock:
                                combined_folder_file_map[folder_name] = result_map
                        except Exception as e:
                            print(f"Error processing folder '{folder_name}': {e}")

            self.folder_file_map = combined_folder_file_map
        except Exception as e:
            raise Exception(f"Exception reading drive folders: {e}")

    def move_files_and_folders_to_output_drive(
        self, drive_id: str, folder_file_mapping=None
    ):
        """
        Retrieves a specific entity folder and its files from the given drive,
        processes them, and uploads metadata and content to the outputs drive.
        Args:
            folder_file_mapping: meta folder file mapping.
            drive_id: The ID of the source drive
            entity_name: The name of the entity folder to process
        """
        try:
            if folder_file_mapping is None:
                folder_file_mapping = {}

            def process_document(entity, doc_id, doc_info, folder_id):
                try:
                    meta_data = doc_info or {}
                    subfolder_id = self.graph.create_subfolder(
                        self.output_drive_id, folder_id, doc_id
                    )
                    mime_type = meta_data.get("mimeType")
                    text_content = None
                    if (
                        meta_data
                        and mime_type
                        and mime_type.startswith("image/")
                        and meta_data.get("document_summary")
                    ):
                        text_content = meta_data["document_summary"]
                    else:
                        text_content = meta_data.get("content_text", None)

                    metadata = meta_data.copy()
                    self.content_extractor.process_and_upload_file(
                        self.output_drive_id,
                        drive_id=drive_id,
                        source_file_id=meta_data.get("id"),
                        target_folder_id=subfolder_id,
                        metadata=metadata,
                    )
                    return True
                except Exception as e:
                    print(
                        f"Error processing document {meta_data.get('name')} (ID: {doc_id}): {str(e)}"
                    )
                    return False

            with ThreadPoolExecutor(max_workers=4) as executor:
                document_executors = {}
                for entity, documents in folder_file_mapping.items():
                    target_root = self._target_root_name(entity)
                    folder_id = self.graph.create_root_folder(
                        self.output_drive_id, target_root
                    )
                    for doc_id, doc_info in documents.items():
                        future = executor.submit(
                            process_document, entity, doc_id, doc_info, folder_id
                        )
                        document_executors[future] = (entity, doc_id)

                for future in tqdm(
                    as_completed(document_executors),
                    total=len(document_executors),
                    desc="\n Processing document ",
                ):
                    entity, doc_id = document_executors[future]
                    try:
                        result = future.result()
                        if not result:
                            print(f"\n Failed to process document in {entity}")
                    except Exception as e:
                        print(f"\n Error processing document in {entity}: {e}")

            return folder_file_mapping
        except Exception as e:
            print(f"Exception processing folder '{entity}': {e}")
            return {}

    def move_files_and_folders_to_output_drive_by_entity(
        self, drive_id: str, entity_name: str, folder_file_mapping=None
    ) -> Dict[Any, Any]:
        """
        Retrieves a specific entity folder and its files from the given drive,
        processes them, and uploads metadata and content to the outputs drive.
        Args:
            folder_file_mapping: meta folder file mapping.
            drive_id: The ID of the source drive
            entity_name: The name of the entity folder to process
        """
        try:
            if folder_file_mapping is None:
                folder_file_mapping = {}

            def process_document(entity, doc_id, doc_info, folder_id):
                try:
                    meta_data = doc_info or {}
                    subfolder_id = self.graph.create_subfolder(
                        self.output_drive_id, folder_id, doc_id
                    )
                    mime_type = meta_data.get("mimeType")
                    text_content = None
                    if (
                        meta_data
                        and mime_type
                        and mime_type.startswith("image/")
                        and meta_data.get("document_summary")
                    ):
                        text_content = meta_data["document_summary"]
                    else:
                        text_content = meta_data.get("content_text", None)


                    metadata = meta_data.copy()
                    self.content_extractor.process_and_upload_file(
                        self.output_drive_id,
                        drive_id=drive_id,
                        source_file_id=meta_data.get("id"),
                        target_folder_id=subfolder_id,
                        metadata=metadata,
                    )
                    return True
                except Exception as e:
                    print(
                        f"Error processing document {meta_data.get('name')} (ID: {doc_id}): {str(e)}"
                    )
                    return False

            with ThreadPoolExecutor(max_workers=4) as executor:
                document_executors = {}
                for entity, documents in folder_file_mapping.items():
                    target_root = self._target_root_name(entity)
                    folder_id = self.graph.create_root_folder(
                        self.output_drive_id, target_root
                    )
                    for doc_id, doc_info in documents.items():
                        future = executor.submit(
                            process_document, entity, doc_id, doc_info, folder_id
                        )
                        document_executors[future] = (entity, doc_id)

                for future in tqdm(
                    as_completed(document_executors),
                    total=len(document_executors),
                    desc="\n Processing document ",
                ):
                    entity, doc_id = document_executors[future]
                    try:
                        result = future.result()
                        if not result:
                            print(f"\n Failed to process document in {entity}")
                    except Exception as e:
                        print(f"\n Error processing document in {entity}: {e}")

            return folder_file_mapping
        except Exception as e:
            print(f"Exception processing folder '{entity}': {e}")
            return {}