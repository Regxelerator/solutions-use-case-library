import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any, Union
from utils.file_handler import write_to_json_file
from openai import OpenAI
from agents import function_tool


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_vector_store_id(file_path: str) -> Union[str, None]:
    """
    Loads the vector store ID from a given JSON file.

    Args:
    - file_path (str): Path to the JSON file containing the vector store ID.

    Returns:
    - str: The vector store ID if found, else None.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            vector_store_id = data.get("vector_store_id")
            if vector_store_id:
                return vector_store_id
            else:
                raise ValueError("vector_store_id not found in the file.")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from file: {file_path}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


async def list_files(vector_store_id: str) -> List[str]:
    """
    Retrieves the list of files from the vector store.

    Args:
    - vector_store_id (str): The ID of the vector store.

    Returns:
    - List[str]: A list of file names stored in the vector store.
    """
    vector_store_files = client.vector_stores.files.list(
        vector_store_id=vector_store_id
    )
    files = [
        file.attributes.get("file_name", "Unknown") for file in vector_store_files.data
    ]
    return files


Score_Threshold = 0.80


@function_tool
async def search_file(output_dir: str) -> Dict[str, Any]:
    """
    Performs a semantic search on files in the vector store based on a query.

    Args:
    - output_dir (str): Directory where the search results and upload metadata are stored.

    Returns:
    - Dict[str, Any]: A dictionary containing the consolidated search results.
    """
    result_upload = os.path.join(output_dir, "upload_results.json")
    vector_store_id = load_vector_store_id(result_upload)

    if not vector_store_id:
        return {
            "error": "No vector store ID found. Ensure Step 2 has completed successfully."
        }

    file_names = await list_files(vector_store_id)

    if not file_names:
        return {"error": "No files found in vector store."}

    results = []
    counter = 1

    for file_name in file_names:
        search_results = client.vector_stores.search(
            vector_store_id="vector_store_id",
            query="AI supervision in financial services",
            max_num_results=20,
            filters={"type": "eq", "key": "file_name", "value": file_name},
        )

        def extract_data(response, apply_filter=False):
            extracted = []
            for item in response.data:
                try:
                    score = float(item.score)
                except (ValueError, TypeError):
                    continue

                if not apply_filter or score >= Score_Threshold:
                    extracted.append(
                        {
                            "file_name": item.attributes.get("file_name", "Unknown"),
                            "organization": item.attributes.get(
                                "organization", "Unknown"
                            ),
                            "title": item.attributes.get("title", "Unknown"),
                            "year": item.attributes.get("year", "Unknown"),
                            "content": [content.text for content in item.content],
                            "file_id": item.file_id,
                            "score": score,
                        }
                    )
            return extracted

        filtered_results = extract_data(search_results, apply_filter=True)

        filtered_results_with_ids = []
        for chunk in filtered_results:
            chunk_with_id = {**chunk, "ID": f"{counter:03d}"}
            filtered_results_with_ids.append(chunk_with_id)
            counter += 1

        results.append(
            {
                "file_name": file_name,
                "filtered_search_results": filtered_results_with_ids,
            }
        )

    consolidated_results = {"consolidated_results": results}
    search_result = os.path.join(output_dir, "search_results.json")
    write_to_json_file(search_result, consolidated_results, indent=4)
    return consolidated_results
