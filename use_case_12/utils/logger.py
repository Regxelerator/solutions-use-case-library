from __future__ import annotations

import json
import pathlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict

LOG_API = pathlib.Path("api_calls.jsonl")

def log_api(payload: Dict[str, Any], response_obj: Any) -> None:

    try:
        entry = {
            "timestamp": datetime.now(timezone.utc)
                         .isoformat(timespec="seconds") + "Z",
            "request":  payload,
            "response": json.loads(response_obj.json())
        }
        LOG_API.parent.mkdir(parents=True, exist_ok=True)
        with LOG_API.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:               
        logging.exception("API-log failed: %s", e)