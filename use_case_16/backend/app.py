from pathlib import Path
from io import BytesIO
import asyncio

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .extractors import extract_text_from_file
from .url_fetch import fetch_and_extract
from .content_store import (
    append_to_masterlist,
    remove_from_masterlist,
    get_content,
    _load as load_masterlist,
)
from .memo_store import (
    list_sections,
    create_section,
    patch_section,
    delete_section,
    reorder_sections,
)

from .preset_store import (
    list_presets as _list_presets,
    get_preset as _get_preset,
    update_preset as _update_preset,
)

from .llm import (
    extract_metadata,
    get_completion,
    _truncate_text,
    MAX_TOKENS,
    PRESET_MODEL,
)

from .converters import md_to_docx, md_to_pdf

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Briefing Memo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_system_prompt(mode: str, preset_key: str | None, custom_prompt: str | None) -> str:

    custom_prompt = (custom_prompt or "").strip()

    if (preset_key or "").lower() == "custom":
        if len(custom_prompt) < 20:
            raise HTTPException(400, "Custom instructions must be at least 20 characters")
        return custom_prompt

    default_key = "summary" if mode == "generate" else "shorter"
    key = preset_key or default_key
    preset = _get_preset(mode, key)
    if not preset:
        raise HTTPException(400, f"Preset not found: {key}")

    base = preset["prompt"].rstrip()
    if custom_prompt:
        base = f"{base}\n\n**Additional guidance:**\n{custom_prompt}"
    return base


@app.get("/api/masterlist")
async def list_masterlist():
    entries = load_masterlist()
    for e in entries:
        e.pop("content", None)
    return {"entries": entries}


@app.delete("/api/masterlist/{entry_id}", status_code=204)
async def delete_entry(entry_id: str):
    if not remove_from_masterlist(entry_id):
        raise HTTPException(404, "Entry not found")


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    try:
        dest = UPLOAD_DIR / file.filename
        dest.write_bytes(await file.read())
        text = extract_text_from_file(dest)
        metadata = await extract_metadata(text)
        if not metadata:
            raise ValueError("LLM returned empty metadata")
        entry_id = append_to_masterlist(file.filename, text, metadata)
        return {"id": entry_id, "metadata": metadata}
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc


@app.post("/api/url")
async def url_upload(payload: dict):
    url = payload.get("url")
    if not url:
        raise HTTPException(400, "url is required")
    try:
        filename, text = fetch_and_extract(url)
        metadata = await extract_metadata(text)
        if not metadata:
            raise ValueError("LLM returned empty metadata")
        entry_id = append_to_masterlist(url, text, metadata)
        return {"id": entry_id, "metadata": metadata}
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc


@app.get("/api/memo")
async def get_memo():
    return {"sections": list_sections()}


@app.post("/api/memo/section")
async def add_section(payload: dict):
    title = payload.get("title", "").strip()
    if not title:
        raise HTTPException(400, "title required")
    return create_section(title)


@app.patch("/api/memo/section/{sec_id}")
async def update_section(sec_id: str, payload: dict):
    if not patch_section(sec_id, payload):
        raise HTTPException(404, "section not found")
    return {"ok": True}


@app.delete("/api/memo/section/{sec_id}", status_code=204)
async def remove_section(sec_id: str):
    if not delete_section(sec_id):
        raise HTTPException(404, "section not found")


@app.post("/api/memo/reorder")
async def reorder(payload: dict):
    reorder_sections(payload.get("order", []))
    return {"ok": True}


@app.post("/api/memo/section/{sec_id}/generate")
async def generate_content(sec_id: str, payload: dict):
    source_ids: list[str] = payload.get("source_ids", [])
    if not source_ids:
        raise HTTPException(400, "source_ids required")

    raw_snippets = "\n\n".join(get_content(cid) or "" for cid in source_ids)
    snippets = _truncate_text(raw_snippets, MAX_TOKENS, PRESET_MODEL)

    system_prompt = _resolve_system_prompt(
        "generate",
        payload.get("preset"),
        payload.get("custom_prompt"),
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"\n===\n{snippets}\n==="},
    ]

    patch_section(sec_id, {"status": "Generating"})
    text = await get_completion(messages)
    patch_section(sec_id, {"content": text, "status": "Draft"})
    return {"content": text}


@app.post("/api/memo/section/{sec_id}/edit")
async def edit_content(sec_id: str, payload: dict):
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(400, "text is required")

    system_prompt = _resolve_system_prompt(
        "edit",
        payload.get("preset"),
        payload.get("custom_prompt"),
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    patch_section(sec_id, {"status": "Editing"})
    new_text = await get_completion(messages)
    patch_section(sec_id, {"content": new_text, "status": "Draft"})
    return {"content": new_text}


@app.post("/api/memo/export")
async def export_memo(payload: dict):
    fmt: str = payload.get("format", "markdown").lower()
    title: str = payload.get("title", "memo")
    order: list[str] = payload.get("section_order", [])
    include_ids: set[str] = set(payload.get("include_ids", []))

    sections = list_sections()
    id_map = {s["id"]: s for s in sections}

    ordered = [id_map[i] for i in order if i in id_map] or sections
    included = [s for s in ordered if (s["id"] in include_ids) or not include_ids]

    markdown = "\n\n".join(f"## {s['title']}\n\n{s['content']}" for s in included)

    if fmt == "markdown":
        blob = markdown.encode("utf-8")
        media_type = "text/markdown"

    elif fmt == "docx":
        blob = await asyncio.to_thread(md_to_docx, markdown)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    elif fmt == "pdf":
        blob = await asyncio.to_thread(md_to_pdf, markdown)
        media_type = "application/pdf"

    else:
        raise HTTPException(400, f"Unsupported format: {fmt}")

    filename_safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in title.strip()) or "memo"
    filename = f"{filename_safe}.{ 'md' if fmt == 'markdown' else fmt }"

    return StreamingResponse(
        BytesIO(blob),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/presets")
async def list_presets(mode: str = "generate"):
    return _list_presets(mode)


@app.put("/api/presets/{preset_key}")
async def update_preset(preset_key: str, payload: dict):
    mode: str = payload.get("mode", "generate")
    prompt: str | None = payload.get("prompt")
    label: str | None = payload.get("label")

    if prompt is None and label is None:
        raise HTTPException(400, "prompt or label required")

    if not _update_preset(mode, preset_key, prompt=prompt, label=label):
        raise HTTPException(404, "preset not found")

    return {"ok": True}