import json
import os

def write_to_file(file_path: str, data):
    """
    Writes the given data to a file in JSON format.
    :param file_path: Path of the output file.
    :param data: Data to be written to the file.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")


def read_from_file(file_path: str):
    """
    Reads data from a JSON file and returns it.
    :param file_path: Path of the JSON file to read.
    :return: Parsed JSON data if successful, None if an error occurs.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return None


def check_file_exists(directory: str, filename: str) -> str:
    """Check if a file exists in the given directory and return the full path."""
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Error: The file '{filename}' was not found in the '{directory}' directory."
        )
    return file_path