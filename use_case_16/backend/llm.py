import json
import os
import re
import datetime
import asyncio
from pathlib import Path
import openai

try:
    import tiktoken
except ImportError:
    tiktoken = None

PROMPT_FILE = Path(__file__).parent / "prompts" / "PROMPT_METADATA_EXTRACTION.txt"
SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8").strip()

openai.api_key = os.getenv("OPENAI_API_KEY")

METADATA_MODEL = os.getenv("OPENAI_METADATA_MODEL", "gpt-4o-mini")
PRESET_MODEL = os.getenv("OPENAI_PRESET_MODEL", "gpt-4o")

MAX_METADATA_TOKENS = 100_000
MAX_COMPLETION_TOKENS = 100_000         

LOG_PATH = Path(__file__).parent / "llm_calls.jsonl"
_LOG_LOCK = asyncio.Lock()

async def _log_llm_call(model: str, messages: list[dict], response: str) -> None:
    entry = {
        "ts": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "model": model,
        "messages": messages,
        "response": response,
    }
    json_line = json.dumps(entry, ensure_ascii=False) + "\n"
    async with _LOG_LOCK:
        await asyncio.to_thread(LOG_PATH.open("a", encoding="utf-8").write, json_line)


def _parse(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\{.*}", content, re.S)
        return json.loads(m.group(0)) if m else {}


def _truncate_text(text: str, max_tokens: int, model: str) -> str:
    if tiktoken:
        try:
            enc = tiktoken.encoding_for_model(model)
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(text)
        return enc.decode(tokens[:max_tokens])
    return text[: max_tokens * 4]


def _wrap_inputs(parts: list[str]) -> str:
    return "\n\n".join(f"<INPUT {i}>{p}</INPUT {i}>" for i, p in enumerate(parts, 1))


async def extract_metadata(text: str) -> dict:
    client = openai.AsyncOpenAI()
    truncated = _truncate_text(text, MAX_METADATA_TOKENS, METADATA_MODEL)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _wrap_inputs([truncated])},
    ]

    resp = await client.chat.completions.create(
        model=METADATA_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    result_text = resp.choices[0].message.content
    await _log_llm_call(METADATA_MODEL, messages, result_text)
    return _parse(result_text)

def _prepare_messages(messages: list[dict]) -> list[dict]:
    sys_msgs = [m for m in messages if m["role"] != "user"]
    user_contents = [m["content"] for m in messages if m["role"] == "user"]
    if not user_contents:
        return messages
    sys_msgs.append({"role": "user", "content": _wrap_inputs(user_contents)})
    return sys_msgs

async def get_completion(messages: list[dict], temperature: float = 0.2) -> str:
    client = openai.AsyncOpenAI()

    prepared = _prepare_messages(messages)

    if prepared and prepared[-1]["role"] == "user":                      
        prepared[-1]["content"] = _truncate_text(                        
            prepared[-1]["content"], MAX_COMPLETION_TOKENS, PRESET_MODEL 
        )                                                                

    resp = await client.chat.completions.create(
        model=PRESET_MODEL,
        messages=prepared,
        temperature=temperature,
    )
    result_text = resp.choices[0].message.content
    await _log_llm_call(PRESET_MODEL, prepared, result_text)
    return result_text