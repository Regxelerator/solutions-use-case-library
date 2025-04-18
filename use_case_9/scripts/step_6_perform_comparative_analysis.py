# scripts/step_6_comparative_analysis.py

import os
import json
from time import sleep
from pathlib import Path
from llm.llm_engine import perform_comparative_analysis

def comparative_analysis(output_root_dir: str) -> None:

    year_dirs = sorted([
        d for d in os.listdir(output_root_dir)
        if os.path.isdir(os.path.join(output_root_dir, d, "interim_outputs"))
    ])
    if len(year_dirs) < 2:
        print("Need at least two years of data to compare.")
        return

    indices_per_year = []
    for year in year_dirs:
        interim = os.path.join(output_root_dir, year, "interim_outputs")
        files = [
            f for f in os.listdir(interim)
            if f.startswith("synthesis_annual_report_") and f.endswith(".json")
        ]
        idxs = {f.replace("synthesis_annual_report_", "").replace(".json", "") for f in files}
        indices_per_year.append(idxs)

    common_idxs = set.intersection(*indices_per_year)
    if not common_idxs:
        print("No common report indices found across years.")
        return

    comp_dir = os.path.join(output_root_dir, "comparative_analysis")
    os.makedirs(comp_dir, exist_ok=True)

    for idx in sorted(common_idxs, key=lambda x: int(x)):
        combined = {}
        for year in year_dirs:
            path = os.path.join(output_root_dir, year, "interim_outputs",
                                 f"synthesis_annual_report_{idx}.json")
            try:
                combined[year] = json.loads(Path(path).read_text(encoding="utf-8"))
            except Exception as e:
                print(f"Error loading {path}: {e}")
                combined = None
                break
        if combined is None:
            continue

        print(f"\nComparing report #{idx} for years {', '.join(year_dirs)}")
        try:
            payload = json.dumps(combined, ensure_ascii=False, indent=2)
            parsed, raw = perform_comparative_analysis(payload)
            result = parsed if parsed is not None else raw

            out_path = os.path.join(
                comp_dir,
                f"comparative_analysis_annual_report_{idx}.json"
            )
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"Saved comparative analysis → {out_path}")
        except Exception as e:
            print(f"Error during comparative analysis for index {idx}: {e}")

        sleep(0.2)


if __name__ == "__main__":
    base_output = os.path.join(os.getcwd(), "output")
    comparative_analysis(base_output)