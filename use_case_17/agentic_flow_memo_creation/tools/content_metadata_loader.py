from pathlib import Path
import json
from typing import List, Dict

from agents.tool import function_tool

_CONTENT_FILE = Path(__file__).resolve().parents[1] / "content_masterlist.json"

_RETURN_FIELDS = [
    "filename",
    "content_name",
    "document_author",
    "content_type",
    "content_details",
]

@function_tool(
    name_override="content_loader",
    description_override=(
        "Given a list of filenames/URLs from a section's content list, return "
        "the corresponding content objects from content_masterlist.json. "
        "Items not found are skipped."
    ),
)

def content_metadata_loader() -> List[Dict]:
    data = json.loads(_CONTENT_FILE.read_text(encoding="utf-8"))

    return [{k: item.get(k, "") for k in _RETURN_FIELDS} for item in data]