import os
import json
from time import sleep
from pathlib import Path
from llm.llm_engine import extract_information, synthesize_information


def synthesize_annual_report_information(mda_section_output_dir: str) -> None:
    filtered_files = sorted([
        f for f in os.listdir(mda_section_output_dir)
        if f.startswith("mda_sections_filtered_annual_report_") and f.endswith(".json")
    ])

    if not filtered_files:
        print("No filtered annual report files found.")
        return

    for fname in filtered_files:
        idx_str = fname.replace("mda_sections_filtered_annual_report_", "").replace(".json", "").strip()
        sections_path = os.path.join(mda_section_output_dir, fname)

        risk_output_fname = f"risk_information_annual_report_{idx_str}.json"
        risk_output_path = os.path.join(mda_section_output_dir, risk_output_fname)
        print(f"\nExtracting risk info from {sections_path}")

        try:
            sections = json.loads(Path(sections_path).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error loading {sections_path}: {e}")
            continue

        risk_results = []
        for sec in sections:
            title = sec.get("section_title", "untitled")
            text = sec.get("section_text", "")
            if not text:
                print(f"  Skipping '{title}' (no text).")
                continue

            print(f"  • Section: {title}")
            try:
                parsed, _raw = extract_information(text)
                risk_results.append({
                    "section_title": title,
                    "synthesis": parsed if parsed is not None else _raw
                })
            except Exception as e:
                print(f"    Error on '{title}': {e}")
            sleep(0.2)

        with open(risk_output_path, "w", encoding="utf-8") as f:
            json.dump(risk_results, f, indent=2, ensure_ascii=False)
        print(f"Risk information saved → {risk_output_path}")

        synthesis_output_fname = f"synthesis_annual_report_{idx_str}.json"
        synthesis_output_path = os.path.join(mda_section_output_dir, synthesis_output_fname)
        print(f"Synthesizing from {risk_output_fname}")

        try:
            risk_json_str = Path(risk_output_path).read_text(encoding="utf-8")
            synth_parsed, _synth_raw = synthesize_information(risk_json_str)
            output = synth_parsed

            with open(synthesis_output_path, "w", encoding="utf-8") as f_syn:
                json.dump(output, f_syn, indent=2, ensure_ascii=False)

            print(f"Synthesis saved → {synthesis_output_path}")
        except Exception as e:
            print(f"Error during synthesis for {risk_output_fname}: {e}")