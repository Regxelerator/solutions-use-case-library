from pathlib import Path
import json
from typing import Annotated, List, Dict
from agents.tool import function_tool

_CONTENT_FILE = Path(__file__).resolve().parents[1] / "content_masterlist.json"


@function_tool(            
    name_override="content_loader",   
    description_override=(
        "Return a list of dicts (one per entry in content_masterlist.json) containing the core metadata fields: "
        "filename, content_name, document_author, content_type, content_details."
    ),
)

def content_loader(
    filenames: Annotated[List[str], "List of filenames or URLs to retrieve"],
) -> List[Dict]:

    data = json.loads(_CONTENT_FILE.read_text(encoding="utf-8"))
    by_filename = {item["filename"]: item for item in data}

    results: List[Dict] = []
    for name in filenames:
        item = by_filename.get(name)
        if item:
            results.append(item)

    return results
