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
    _load as load_masterlist,
)
from .memo_store import (
    list_sections,
    create_section,
    patch_section,
    delete_section,
    reorder_sections,
)
from .llm import (
    extract_metadata
)
from .converters import md_to_docx, md_to_pdf
from .agentic_flow import run_agentic_generate

import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = Path(__file__).resolve().parents[2] / "server.log"

_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=2_000_000,   
    backupCount=3,        
    encoding="utf-8",
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s: %(message)s",
    handlers=[_handler, logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Briefing Memo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/api/memo/agentic")
async def generate_memo_agentic(payload: dict):
    """
    Trigger the end‑to‑end agent workflow.
    Payload → { "instruction": "<free‑text prompt>" }
    """
    instruction = payload.get("instruction", "").strip()
    if not instruction:
        raise HTTPException(400, "instruction required")

    logger.info("Agentic memo generation started: %s", instruction.replace("\n", " ")[:200])

    try:
        sections = await run_agentic_generate(instruction)
        logger.info("Agentic memo generation finished – %d sections drafted", len(sections))
        return {"sections": sections}

    except Exception:
        logger.exception("Agentic memo generation FAILED")
        raise HTTPException(500, "Memo generation failed – see server.log for details")


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



