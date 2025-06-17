import os
import tempfile
import shutil
from multiprocessing import Pool
from processors.parser import DocumentParser


class DocumentProcessorAndParser:
    """
    Class to handle file processing and extraction for the sharepoint.
    Convert them into markdown and get structured output from the LLMs.
    """

    def __init__(self, ms_graph_client, source_drive_id):
        self.source_drive_id = source_drive_id
        self.temp_input_dir = tempfile.mkdtemp()
        self.output_dir = self.setup_output_directory()
        self.ms_graph_client = ms_graph_client
        self.max_processes = 4
        print(
            f"Created temporary directory for SharePoint files: {self.temp_input_dir}"
        )

    def setup_output_directory(self):
        current_directory = os.getcwd()
        output_dir = os.path.join(current_directory, "output")
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory: {output_dir}")
        return output_dir

    def list_files(self):
        """
        Retrieve the list of files recursively from SharePoint.
        """
        items = self.ms_graph_client.list_all_files_recursive(self.source_drive_id)
        if not items:
            print("No files found in the SharePoint library.")
            return []
        return items

    def download_and_process_folder(self, folder_items, folder_path):
        """
        Download files from SharePoint and process them.
        """
        for item in folder_items:
            if "file" in item:
                file_name = item["name"]
                relative_folder = item.get("folder_path", "")

                if relative_folder:
                    local_folder_path = os.path.join(
                        self.temp_input_dir, relative_folder
                    )
                    os.makedirs(local_folder_path, exist_ok=True)
                    local_file_path = os.path.join(local_folder_path, file_name)
                else:
                    local_file_path = os.path.join(self.temp_input_dir, file_name)

                print(
                    f"Downloading: {relative_folder + '/' if relative_folder else ''}{file_name}"
                )
                file_content = self.ms_graph_client.download_file(
                    self.source_drive_id, item["id"]
                )
                if file_content:
                    with open(local_file_path, "wb") as f:
                        f.write(file_content)

        print(f"\nProcessing files in folder: {folder_path}")
        doc_processor = DocumentParser(self.temp_input_dir, self.output_dir)
        doc_processor.process_all_files()

    def group_files_by_folder(self, items):
        """
        Group files by their folder path.
        """
        folder_dict = {}
        for item in items:
            folder_path = item.get("folder_path", "root")
            folder_dict.setdefault(folder_path, []).append(item)
        print(f"Grouped files into {len(folder_dict)} folders.")
        return folder_dict

    def process_folders_in_parallel(self, folder_dict):
        """
        Process each folder in a separate process.
        """
        args = [
            (folder_items, folder_path)
            for folder_path, folder_items in folder_dict.items()
        ]
        with Pool(processes=self.max_processes) as pool:
            pool.starmap(self.download_and_process_folder, args)

    def clean_up(self):
        """
        Remove temporary files after processing.
        """
        print(f"\n Cleaning up temporary files from {self.temp_input_dir}...")
        shutil.rmtree(self.temp_input_dir)
        print("Cleanup completed.")

    def run(self):
        """
        Orchestrates the entire process: listing, downloading, processing, and cleanup.
        """
        try:
            items = self.list_files()
            if not items:
                return
            folder_dict = self.group_files_by_folder(items)
            self.process_folders_in_parallel(folder_dict)
        finally:
            self.clean_up()
