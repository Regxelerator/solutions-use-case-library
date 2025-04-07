from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from agents import function_tool
from typing import Dict, Any

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@function_tool
async def upload_files_to_vector_store(
    Metadata_File_path: str, output_dir: str
) -> Dict[str, Any]:
    """
    Uploads files to a vector store based on the metadata provided in the metadata file.

    Args:
    Metadata_File_path (str): Path to the metadata JSON file containing file details.
    output_dir (str): Path to the directory containing processed files.

    Returns:
    Dict[str, Any]: A dictionary containing the vector store ID and the results of the upload process.
    """
    vector_store = client.vector_stores.create(
        name="vector_store_name",
        chunking_strategy={
            "type": "static",
            "static": {"max_chunk_size_tokens": 800, "chunk_overlap_tokens": 100},
        },
    )
    vector_store_id = vector_store.id

    with open(Metadata_File_path, "r", encoding="utf-8") as meta_file:
        metadata_list = json.load(meta_file)

    results = []

    Processed_Folder = os.path.join(output_dir, "Processed")
    for metadata in metadata_list:
        processed_file_name = metadata["processed_filename"]
        file_path = os.path.join(Processed_Folder, processed_file_name)

        if not os.path.exists(file_path):
            results.append(
                {"file_name": processed_file_name, "status": "File not found"}
            )
            continue

        with open(file_path, "rb") as file:
            upload_response = client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store_id, file=file
            )

        file_id = upload_response.id

        client.vector_stores.files.update(
            vector_store_id=vector_store_id,
            file_id=file_id,
            attributes={
                "file_name": processed_file_name,
                "organization": metadata["organization"],
                "title": metadata["title"],
                "year": metadata["year"],
            },
        )

        results.append(
            {"file_name": processed_file_name, "status": "Uploaded", "file_id": file_id}
        )
    result_upload = os.path.join(output_dir, "upload_results.json")
    with open(result_upload, "w", encoding="utf-8") as json_file:
        json.dump(
            {"vector_store_id": vector_store_id, "results": results},
            json_file,
            indent=4,
            ensure_ascii=False,
        )

    return {"vector_store_id": vector_store_id, "results": results}
