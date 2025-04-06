import os
from agents import Runner, trace
from utils.file_handler import write_to_json_file
from llm.llm_engine import Preprocessing_Agent


async def agent_for_file_processing(input_dir: str, output_dir: str) -> str:
    """
    This function processes PDF files in the input directory, generates metadata json file

    Args:
    input_dir (str): Path to the input directory containing PDF files.
    output_dir (str): Path to the output directory where processed metadata is stored.

    Returns:
    str: The file path to the generated metadata JSON file.
    """
    processed_folder = os.path.join(output_dir, "Processed")
    os.makedirs(processed_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)
    processed_files = set(
        f.replace(".md", ".pdf")
        for f in os.listdir(processed_folder)
        if f.endswith(".md")
    )
    pdf_files = [
        f
        for f in os.listdir(input_dir)
        if f.endswith(".pdf") and f not in processed_files
    ]
    metadata_list = []

    for pdf_file in pdf_files:
        with trace("Step 1: Document Pre-Processing"):
            result = await Runner.run(
                Preprocessing_Agent,
                [
                    {
                        "role": "user",
                        "content": f"Process the document: {pdf_file}",
                        "arguments": {"pdf_file": pdf_file, "input_dir": input_dir},
                    }
                ],
            )

            if result.final_output is not None:
                metadata = result.final_output
                new_file_name = pdf_file.replace(".pdf", ".md")
                metadata_dict = metadata.dict()
                metadata_dict["original_filename"] = pdf_file
                metadata_dict["processed_filename"] = new_file_name
                metadata_list.append(metadata_dict)

    meta_data_file = "metadata.json"
    metadata_path = os.path.join(processed_folder, meta_data_file)
    write_to_json_file(metadata_path, metadata_list, indent=4)
    return metadata_path
