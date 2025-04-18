from pathlib import Path
from typing import Any
import json

def load_json(path: str) -> Any:
    """
    Loads and parses a JSON file from the given path.

    Args:
        path (str): Path to the JSON file.

    Returns:
        Any: The parsed JSON data.
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(data, path: str) -> None:
    """
    Saves the given data to a JSON file at the specified path.

    Args:
        data (Any): Data to be saved (must be JSON serializable).
        path (str): Path where the JSON file will be saved.

    Returns:
        None
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
