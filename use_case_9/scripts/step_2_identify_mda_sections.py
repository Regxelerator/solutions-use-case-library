import os
from llm.llm_engine import determine_html_section_markers


def read_limited_html_chars(html_path: str, limit: int = 200000) -> str:
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()[:limit]


def identify_mda_sections(mda_section_output_dir: str) -> None:
    html_files = [
        f for f in os.listdir(mda_section_output_dir) if f.lower().endswith(".html")
    ]
    html_files.sort()
    for idx, filename in enumerate(html_files, start=1):
        html_path = os.path.join(mda_section_output_dir, filename)
        model_response_file = os.path.join(
            mda_section_output_dir, f"mda_sections_annual_report_{idx}.json"
        )
        if not os.path.isfile(html_path):
            print(f"{filename} HTML File not found: {html_path}")
            continue
        try:
            limited_html = read_limited_html_chars(html_path)
            section_markers, raw_response = determine_html_section_markers(limited_html)
            with open(model_response_file, "w", encoding="utf-8") as f:
                f.write(raw_response)
            print(f"Processed {filename} -> {model_response_file}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
