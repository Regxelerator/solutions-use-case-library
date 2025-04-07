import os
import json
from utils.pdf_parser import extract_pdf_to_markdown


def process_file(file_path: str) -> str:
    """
    Detects file type and processes it accordingly.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_pdf_to_markdown(file_path)
    raise ValueError(f"Unsupported file type: {ext}")


def check_file_exists(directory: str, filename: str) -> bool:
    """
    Check if a file exists in the given directory.

    Args:
    directory: The directory path.
    filename: The name of the file.

    Returns:
    True if the file exists, False otherwise.
    """
    file_path = os.path.join(directory, filename)
    print(f"Checking if file exists: {file_path}")
    print(os.path.exists(file_path))
    return os.path.exists(file_path)


def save_json(data: dict, output_path: str, filename: str) -> None | str:
    """
    Saves the given data as a JSON file.
    Args:
        data (dict): The extracted data to be saved.
        output_path (str): Directory where the file should be saved.
        filename (str): Name of the JSON file (without directory path).
    Returns:
         return the file path.
    """
    os.makedirs(output_path, exist_ok=True) 
    output_file = os.path.join(output_path, filename)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return output_file


def load_json(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
