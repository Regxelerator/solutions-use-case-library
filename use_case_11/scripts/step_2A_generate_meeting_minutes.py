from __future__ import annotations
import re
import os
import json
from pathlib import Path
from typing import List

from utils.pdf_parser import extract_text_from_pdf
from llm.llm_engine import create_minutes_main_sections, _SECTION_MAP

ROOT_DIR = Path(__file__).resolve().parent.parent
TEST_INPUT_DIR  = ROOT_DIR / "input" / "test_dataset"

PDF_RGX = re.compile(r"Transcript_(\d{4})_(\d{2})\.pdf", re.I)
SECTION_NAMES = list(_SECTION_MAP.keys())

def generate_minutes_for_file(pdf_path: Path, meeting_date: str, model_name: str) -> None:
    if not PDF_RGX.match(pdf_path.name):
        print(f"[Skip] Filename not recognised pattern: {pdf_path.name}")
        return

    year, month, day = meeting_date.split("-")
    transcript_text = extract_text_from_pdf(str(pdf_path))

    sections: List[dict] = [{
        "section_name": "Introduction",
        "section_paragraphs": [
            "Before turning to its immediate policy decision, the Committee discussed financial market developments; the international economy; money, credit, demand and output; and supply, costs and prices."
        ]
    }]

    for sec in SECTION_NAMES:
        result_str = create_minutes_main_sections(transcript_text, sec, model_name)
        if result_str:
            sections.append(json.loads(result_str))

    out_obj = {"meeting_date": meeting_date, "sections": sections}
    out_path = Path("output/test_dataset") / f"Minutes_{year}_{month}_{day}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=2)

    print(f"✓ Draft of meeting minutes created: {out_path.name}")

def generate_minutes_dataset(model_name: str, meeting_date: str, dataset_dir: str | os.PathLike = TEST_INPUT_DIR):
    dataset_dir = Path(dataset_dir)
    for pdf in dataset_dir.glob("Transcript_*.pdf"):
        generate_minutes_for_file(pdf, meeting_date, model_name)