import json
import uuid
from pathlib import Path

MASTERLIST = Path(__file__).parent.parent / "content_masterlist.json"


def _load() -> list[dict]:
    if MASTERLIST.exists():
        return json.loads(MASTERLIST.read_text(encoding="utf-8") or "[]")
    return []


def _save(data: list[dict]) -> None:
    MASTERLIST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_to_masterlist(filename: str, content: str, metadata: dict | None = None) -> str:
    entry_id = str(uuid.uuid4())
    record: dict = {
        "id": entry_id,
        "filename": filename,
        "content": content,
    }
    if metadata:
        record.update(metadata)
    data = _load()
    data.append(record)
    _save(data)
    return entry_id


def remove_from_masterlist(entry_id: str) -> bool:
    data = _load()
    new_data = [d for d in data if d.get("id") != entry_id]
    if len(new_data) == len(data):
        return False
    _save(new_data)
    return True


def get_content(entry_id: str) -> str | None:
    for rec in _load():
        if rec["id"] == entry_id:
            return rec.get("content")
    return None

MASTERLIST = Path(__file__).parent.parent / "content_masterlist.json"
print("MASTERLIST →", MASTERLIST.resolve())  