from __future__ import annotations
import os
import json
import pathlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_CM = "gpt-4.1"
VECTOR_STORE_IDS = ["vs_68296a46156c8191bd04c1a9b42361fe"]
LOG_API = pathlib.Path("api_calls.jsonl")


def _log_api(payload: Dict[str, Any], response_obj: Any) -> None:
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
        import logging
        logging.exception("API-log failed: %s", e)


def _build_payload(combined_input: str) -> Dict[str, Any]:
    return {
        "model": MODEL_CM,
        "input": combined_input,
        "tool_choice": "required",
        "tools": [{
            "type": "file_search",
            "vector_store_ids": VECTOR_STORE_IDS,
            "max_num_results": 10
        }],
        "include": ["file_search_call.results"]
    }


def _extract_reply(resp: Any) -> str:
    reply_block = next(
        blk for blk in reversed(resp.output)
        if getattr(blk, "content", None)
    )
    return reply_block.content[0].text.strip()


def ask_follow_up_questions(
    chat_history: List[Dict[str, str]]
) -> Tuple[str, Any]:

    combined_input = "\n".join(m["content"] for m in chat_history)
    payload = _build_payload(combined_input)

    resp = client.responses.create(**payload)
    _log_api(payload, resp)

    return _extract_reply(resp), resp
