from __future__ import annotations
from pathlib import Path
import json
import io
import contextlib
import re
import sys
import fitz              
import pymupdf4llm       

sys.path.append(str(Path(__file__).resolve().parent.parent)) 
from utils.file_handler import write_to_file  

BASE_DIR        = Path(__file__).resolve().parent.parent
INPUT_DIR       = BASE_DIR / "input" / "training_dataset"
TRANSCRIPTS_DIR = INPUT_DIR / "transcripts"
MINUTES_DIR     = INPUT_DIR / "minutes"
OUTPUT_DIR      = BASE_DIR / "output" / "training_dataset"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GLOSSARY_PATH        = BASE_DIR / "input" / "other_input" / "glossary.json"
SYSTEM_MSG_PATH      = BASE_DIR / "input" / "other_input" / "system_message.json"
SECTION_INSTR_PATH   = BASE_DIR / "input" / "other_input" / "section_specific_instructions.json"
OUTPUT_JSONL_PATH    = BASE_DIR / "output" / "training_data.jsonl"
OUTPUT_JSONL_PATH.parent.mkdir(exist_ok=True)

TRANSCRIPT_RGX = re.compile(r"Transcript_(\d{4})_(\d{2})\.pdf")
MINUTES_RGX    = re.compile(r"Minutes_(\d{4})_(\d{2})\.pdf")

SECTION_NAMES = [
    "Financial markets",
    "The international economy",
    "Money, credit, demand and output",
    "Supply, costs and prices",
    "The immediate policy decision",
]
PARA_START_RGX = re.compile(r"(?:^|\n\n)(\d{1,3})\s")
STRIP_NUM_RGX  = re.compile(r"^\s*\d+\s*[\.\)]?\s*")
RULE_RGX       = re.compile(r"-{3,}")

def _pdf_text(path: Path) -> str:
    doc = fitz.open(path)
    return "\n".join(page.get_text("text") for page in doc)

def _minutes_md(path: Path) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        md = pymupdf4llm.to_markdown(str(path))
    return md

def _slice_sections(md: str):
    blocks: list[dict] = []
    for i, name in enumerate(SECTION_NAMES):
        start_m = re.search(fr"\*\*{re.escape(name)}\*\*", md)
        if not start_m:
            continue
        start = start_m.end()
        next_m = (
            re.search(fr"\*\*{re.escape(SECTION_NAMES[i+1])}\*\*", md[start:])
            if i + 1 < len(SECTION_NAMES) else None
        )
        end = start + next_m.start() if next_m else len(md)
        blocks.append({"section_name": name, "raw": md[start:end].strip()})
    return blocks

def _numbered_split(text: str, expected: int):
    matches = list(PARA_START_RGX.finditer(text))
    paras: list[str] = []
    current, last_start = expected, None
    for m in matches:
        num = int(m.group(1))
        if num != current + 1:
            continue
        if last_start is not None:
            paras.append(text[last_start:m.start()].strip())
        last_start = m.start()
        current += 1
    if last_start is not None:
        paras.append(text[last_start:].strip())
    return paras, current

def process_transcripts() -> int:
    count = 0
    for pdf in TRANSCRIPTS_DIR.glob("Transcript_*.pdf"):
        m = TRANSCRIPT_RGX.match(pdf.name)
        if not m:
            continue
        out_path = OUTPUT_DIR / pdf.with_suffix(".json").name
        write_to_file(
            str(out_path),
            {
                "meeting_date": f"{m.group(1)}-{m.group(2)}",
                "meeting_transcript": _pdf_text(pdf),
            },
        )
        print(f"✓ Transcript extracted: {out_path.name}")
        count += 1
    return count

def process_minutes() -> int:
    count = 0
    for pdf in MINUTES_DIR.glob("Minutes_*.pdf"):
        m = MINUTES_RGX.match(pdf.name)
        if not m:
            continue
        md          = _minutes_md(pdf)
        blocks      = _slice_sections(md)
        clean_sections, running_no = [], 1  
        for blk in blocks:
            raw = RULE_RGX.sub("", blk["raw"])
            numbered, running_no = _numbered_split(raw, running_no)
            clean_sections.append(
                {
                    "section_name": blk["section_name"],
                    "section_paragraphs": [STRIP_NUM_RGX.sub("", p, 1) for p in numbered],
                }
            )
        out_path = OUTPUT_DIR / pdf.with_suffix(".json").name  
        write_to_file(
            str(out_path),
            {
                "meeting_date": f"{m.group(1)}-{m.group(2)}",
                "sections": clean_sections,
            },
        )
        print(f"✓ Minutes extracted and segmented: {out_path.name}")
        count += 1
    return count

def _load_static_assets() -> tuple[str, str, dict[str, list[str]]]:
    with open(GLOSSARY_PATH, encoding="utf-8") as f:
        glossary = json.load(f)
    glossary_text = "\n".join(f"{item['Term']}: {item['Definition / Description']}" for item in glossary)

    with open(SYSTEM_MSG_PATH, encoding="utf-8") as f:
        base_system_prompt = json.load(f)["prompt"]

    with open(SECTION_INSTR_PATH, encoding="utf-8") as f:
        section_map = {e["section_name"]: e["section_instructions"] for e in json.load(f)}

    return glossary_text, base_system_prompt, section_map

def _load_meeting_json(folder: Path, prefix: str) -> dict[str, dict]:
    """Load *.json files whose filename starts with *prefix*; key by meeting_date."""
    records: dict[str, dict] = {}
    for fp in folder.glob(f"{prefix}*.json"):
        with open(fp, encoding="utf-8") as f:
            content = json.load(f)
        records[content["meeting_date"]] = content
    return records

def build_training_jsonl() -> int:
    glossary_text, base_prompt, section_instr = _load_static_assets()
    minutes_data     = _load_meeting_json(OUTPUT_DIR, "Minutes_")
    transcripts_data = _load_meeting_json(OUTPUT_DIR, "Transcript_")

    training_examples: list[dict] = []

    for date, transcript_entry in transcripts_data.items():
        minutes_entry = minutes_data.get(date)
        if not minutes_entry or "sections" not in minutes_entry:
            continue  
        full_transcript = transcript_entry.get("meeting_transcript", "")
        for section in minutes_entry["sections"]:
            name   = section["section_name"]
            paras  = section["section_paragraphs"]

            sys_msg  = (
                "## GENERAL INSTRUCTIONS\n" + base_prompt.strip() + "\n\n" +
                "## SECTION-SPECIFIC INSTRUCTIONS\n" + "\n".join(section_instr.get(name, [])) + "\n\n" +
                "## GLOSSARY\n" + glossary_text
            )
            user_msg = (
                f"**Section**: {name}\n\n" +
                f"**Transcript**:\n{full_transcript}"
            )

            assist_payload = json.dumps({"section_name": name, "section_paragraphs": paras}, ensure_ascii=False)
            training_examples.append({
                "messages": [
                    {"role": "system",    "content": sys_msg},
                    {"role": "user",      "content": user_msg},
                    {"role": "assistant", "content": assist_payload},
                ]
            })

    with open(OUTPUT_JSONL_PATH, "w", encoding="utf-8") as f_out:
        for ex in training_examples:
            json.dump(ex, f_out, ensure_ascii=False)
            f_out.write("\n")
    print(f"✓ training  file created with {len(training_examples)} examples: {OUTPUT_JSONL_PATH.name}  ")
    return len(training_examples)

def create_training_dataset() -> None:
    processed = process_transcripts() + process_minutes()
    if processed == 0:
        print("No PDFs processed - skipping JSONL build.")
        return
    build_training_jsonl()