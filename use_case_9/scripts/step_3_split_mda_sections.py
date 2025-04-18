import os
import json
import re
from pathlib import Path
from difflib import SequenceMatcher
from bs4 import BeautifulSoup


def clean_text(text):
    text = text.replace("&#160;", " ")
    text = text.replace("\xa0", " ")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    return re.sub(r"\s+", " ", text).strip().lower()


def convert_anchor_to_div_id(anchor):
    match = re.search(r"#(?:page=)?(\d+)", anchor)
    if match:
        return f"page{match.group(1)}-div"
    return None


def fuzzy_match(a, b, threshold=0.6):
    return SequenceMatcher(None, a, b).ratio() >= threshold


def get_div_raw_html(html_content, div_id):
    pattern = r'(<div\s+id\s*=\s*"' + re.escape(div_id) + r'"[^>]*>.*?</div>)'
    m = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def extract_p_tags(raw_div_html):
    pattern = r"(<p\b[^>]*>.*?</p>)"
    return re.findall(pattern, raw_div_html, re.DOTALL | re.IGNORECASE)


def find_matching_line(raw_div_html, section_title, verbose=False):
    p_tags = extract_p_tags(raw_div_html)
    cleaned_section_title = clean_text(section_title)

    for p in p_tags:
        text = BeautifulSoup(p, "html.parser").get_text()
        if fuzzy_match(clean_text(text), cleaned_section_title, threshold=0.6):
            if verbose:
                print(f"Matched '{section_title}' with p tag:\n{p}")
            return p
    return None


def generate_mappings(html_path, model_sections, verbose=False):
    raw_html = Path(html_path).read_text(encoding="utf-8")
    mappings = []
    for section in model_sections:
        html_anchor = section.get("html_anchor")
        section_title = section.get("section_title")
        if not html_anchor or not section_title:
            continue
        div_id = convert_anchor_to_div_id(html_anchor)
        raw_div_html = get_div_raw_html(raw_html, div_id)
        if raw_div_html:
            matched_line = find_matching_line(raw_div_html, section_title, verbose)
            if matched_line:
                mappings.append(
                    {
                        "html_anchor": html_anchor,
                        "div_id": div_id,
                        "section_title": section_title,
                        "matched_line": matched_line,
                    }
                )
            else:
                print(f"No match found in div {div_id} for title '{section_title}'")
        else:
            print(f"Div not found for anchor {html_anchor}")
    return mappings, raw_html


def add_start_indexes(mappings, full_html):
    for mapping in mappings:
        marker = mapping.get("matched_line", "")
        start_idx = full_html.find(marker)
        if start_idx == -1:
            print(f"[WARNING] Marker not found for anchor {mapping.get('html_anchor')}")
        mapping["start_index"] = start_idx
    return mappings


def segment_html(full_html, mappings):
    valid_mappings = [m for m in mappings if m.get("start_index", -1) != -1]
    valid_mappings.sort(key=lambda m: m["start_index"])

    sections = []
    num = len(valid_mappings)
    for i, mapping in enumerate(valid_mappings):
        section_title = mapping.get("section_title")
        html_anchor = mapping.get("html_anchor")
        start_idx = mapping["start_index"]
        if i < num - 1:
            end_idx = valid_mappings[i + 1]["start_index"]
        else:
            end_idx = len(full_html)
        section_text = full_html[start_idx:end_idx].strip()
        sections.append(
            {
                "section_title": section_title,
                "html_anchor": html_anchor,
                "section_text": section_text,
            }
        )
    return sections


def clean_section_texts(sections):
    """Clean the section_text HTML, keeping only the text content along with section title and html anchor."""
    clean_sections = []
    for section in sections:
        raw_html = section.get("section_text", "")
        text_only = BeautifulSoup(raw_html, "html.parser").get_text(
            separator=" ", strip=True
        )
        clean_sections.append(
            {
                "section_title": section.get("section_title"),
                "html_anchor": section.get("html_anchor"),
                "section_text": text_only,
            }
        )
    return clean_sections


def split_mda_sections_into_chapters(mda_section_output_dir: str):
    """
    Split MDA sections into chapters.
    Args:
        mda_section_output_dir: Path to the output directory of the MDA sections.

    Returns:
    """
    html_files = sorted(
        [f for f in os.listdir(mda_section_output_dir) if f.lower().endswith(".html")]
    )
    if not html_files:
        print("No HTML files found in the directory.")
        return

    for idx, html_filename in enumerate(html_files, start=1):
        html_path = os.path.join(mda_section_output_dir, html_filename)
        model_response_path = os.path.join(
            mda_section_output_dir, f"mda_sections_annual_report_{idx}.json"
        )
        segmented_output_path = os.path.join(
            mda_section_output_dir, f"mda_sections_segmented_annual_report_{idx}.json"
        )

        if not os.path.isfile(model_response_path):
            print(
                f"Model response JSON not found for index {idx}: {model_response_path}"
            )
            continue

        try:
            with open(model_response_path, "r", encoding="utf-8") as f:
                model_sections = json.load(f)

            mappings, full_html = generate_mappings(
                html_path, model_sections, verbose=True
            )
            mappings = add_start_indexes(mappings, full_html)
            sections = segment_html(full_html, mappings)
            clean_sections = clean_section_texts(sections)
            with open(segmented_output_path, "w", encoding="utf-8") as fp:
                json.dump(clean_sections, fp, indent=2, ensure_ascii=False)
            print(f"Segmented and cleaned sections saved to {segmented_output_path}")
        except Exception as e:
            print(f"Error processing index {idx} for file {html_filename}: {e}")
