import sys
from content_management.directory_manager import DirectoryManager


def run_document_extraction_pipeline(
    ms_graph_client,
    source_site_id,
    source_drive_id,
    entity_name: str | None = None,
):

    output_drive_id = source_drive_id          

    directory_manager = DirectoryManager(
        ms_graph_client, source_drive_id, output_drive_id
    )

    directory_manager.extract_folder_and_files(source_drive_id, entity_name)
    directory_files_mappings = directory_manager.folder_file_map

    if not directory_files_mappings:
        print("Source directory files not found – aborting.")
        sys.exit(1)

    print("\nProcessing files …")
    if entity_name:
        directory_manager.move_files_and_folders_to_output_drive_by_entity(
            source_drive_id, entity_name, directory_files_mappings
        )
    else:
        directory_manager.move_files_and_folders_to_output_drive(
            source_drive_id, directory_files_mappings
        )
    print("Processing complete.")