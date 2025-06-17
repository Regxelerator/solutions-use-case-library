from processors.validation_processor import ValidationProcessor
from pathlib import Path
import os, traceback
from utils.helpers import log_to_csv


def run_validation_pipeline(ms_graph_client, entity_name: str | None = None) -> None:
    """Run the document-completeness pipeline."""
    print("\n" + "=" * 80)
    print(
        f"Starting document validation"
        f"{' for entity: ' + entity_name if entity_name else ''}"
    )
    print("=" * 80)

    output_site_id = ms_graph_client.get_site_id(
        hostname=os.getenv("HOSTNAME"), site_name=os.getenv("SITE_PATH_1")
    )
    output_drive_id = ms_graph_client.get_drive_id(
        output_site_id, drive_name=os.getenv("LIBRARY_NAME_SITE_PATH_1")
    )

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    local_doclist_path = output_dir / "document_list.json"

    bp = ValidationProcessor(ms_graph_client, output_drive_id)

    mappings = bp.extract_target_folder_and_files(entity_name)
    if not mappings:
        print("No valid documents found.")
        return
    print(
        f"✓ Found {sum(len(docs) for docs in mappings.values())} documents "
        f"across {len(mappings)} entities"
    )

    entity_doclists: dict[str, list] = {}
    full_doc_list: list = []

    for folder, file_map in mappings.items():
        doc_list = bp.convert_file_map_to_doc_list({folder: file_map})
        entity_doclists[folder] = doc_list
        full_doc_list.extend(doc_list)
        bp.upload_json_to_sharepoint(folder, "document_list.json", doc_list)

    bp.write_json_file(local_doclist_path, full_doc_list)
    print("✓ document_list.json saved locally and uploaded per entity")

    requirements = bp.load_document_requirements()
    if not requirements:
        print("Error: document_requirements.json missing or empty.")
        return

    for folder, doc_list in entity_doclists.items():
        print(f"\n[3] Running document validation for: {folder}")
        try:
            result = bp.validate_document_list(requirements, doc_list)
            log_to_csv(f"DOCUMENT CHECKLIST LLM OUTPUT ({folder}):\n{result}")

            review_dir   = output_dir / "result"
            review_dir.mkdir(parents=True, exist_ok=True)
            review_json  = review_dir / f"{folder.replace(' ', '_')}_document_checklist.json"
            bp.write_json_file(review_json, result)

            review_docx = review_json.with_suffix(".docx")
            bp.json_to_word(review_json, review_docx)

            print("✓ Document validation check completed")
        except Exception as exc:
            print(f"\nError processing '{folder}': {exc}")
            traceback.print_exc()