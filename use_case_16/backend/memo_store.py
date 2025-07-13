from pathlib import Path
import json
import uuid

MEMO_FILE = Path(__file__).parent.parent / "memo_sections.json"


def _load() -> list[dict]:
    if MEMO_FILE.exists():
        return json.loads(MEMO_FILE.read_text(encoding="utf-8") or "[]")
    return []


def _save(data: list[dict]) -> None:
    MEMO_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_sections() -> list[dict]:
    return _load()


def create_section(title: str) -> dict:
    data = _load()
    sec = {
        "id": str(uuid.uuid4()),
        "title": title,
        "order": len(data),
        "status": "Draft",
        "content": "",
        "sources": [],
        "history": [],
    }
    data.append(sec)
    _save(data)
    return sec


def patch_section(sec_id: str, patch: dict) -> bool:
    data = _load()
    for s in data:
        if s["id"] == sec_id:
            s.update(patch)
            _save(data)
            return True
    return False


def delete_section(sec_id: str) -> bool:
    data = _load()
    new = [s for s in data if s["id"] != sec_id]
    if len(new) == len(data):
        return False
    _save(new)
    return True


def reorder_sections(new_order: list[str]) -> None:
    data = _load()
    id_map = {s["id"]: s for s in data}
    ordered = [id_map[i] for i in new_order if i in id_map]
    _save(ordered)
