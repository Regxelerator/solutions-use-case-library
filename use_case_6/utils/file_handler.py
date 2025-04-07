from typing import Any, List, Dict



def load_json_file(file_path: str) -> Any:
    """
    Loads a JSON file and returns its contents.

    param file_path (str): Path to the JSON file.
    return: Parsed JSON content as a dictionary or list.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        print("Failed to decode with utf-8, trying utf-16.")
        try:
            with open(file_path, "r", encoding="utf-16") as file:
                return json.load(file)
        except Exception as e:
            print(f"Failed to decode JSON with utf-16: {e}")
            return None
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(
            f"Error: Failed to decode JSON in '{file_path}'. Ensure it's correctly formatted."
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None


import json
import sys


def write_to_json_file(file_path: str, data: List[Any] | Dict, indent: int = 4) -> None:
    """
    Writes data to a JSON file.

    Args:
        file_path (str): Path to the output JSON file.
        data (dict): Data to be written into the file.
        indent (int, optional): Number of spaces for indentation in JSON. Defaults to 4.

    Returns:
        None
    """
    try:
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=indent)
        print(f"Data successfully written to {file_path}")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        sys.exit(1)
