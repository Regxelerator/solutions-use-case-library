import json


def write_to_json_file(file_path: str, data: dict, indent: int = 4) -> None:
    """
    Writes data to a JSON file.

    Args:
        file_path (str): Path to the output JSON file.
        data (dict): Data to be written into the file.
        indent (int, optional): Number of spaces for indentation in JSON. Defaults to 4.
    Returns:
        None
    """
    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=indent)


def read_json_file(file_path: str) -> dict:
    """
    Reads and loads data from a JSON file.
    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file '{file_path}': {e}")
        return {}
