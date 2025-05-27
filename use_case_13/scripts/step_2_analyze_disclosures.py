from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from utils.file_handler import ensure_dir
from llm.llm_engine import perform_comparative_analysis, perform_executive_summary, _prompt

def _load_mapping(path: Path | str) -> list[dict]:
    with open(path, encoding="utf-8") as fp:
        data = json.load(fp)
    return list(data.values()) if isinstance(data, dict) else data


def _build_index(items: Sequence[Mapping]) -> dict[str, dict]:
    return {
        i["rule_id"]: {
            "requirement": i["requirement"],
            "qnames": {c["qname"] for c in i.get("concepts", [])},
            "hierarchy_level": i.get("hierarchy_level"),
        }
        for i in items
    }


def _iter_entity_json(root: Path | str) -> Iterable[Path]:
    yield from Path(root).rglob("*.json")


def analyze(
    filings_dir: Path,
    mapping_path: Path,
    output_path: Path,
    exec_output_path: Path,
    call_log_path: Path,
) -> None:
    index = _build_index(_load_mapping(mapping_path))

    grouped: dict[str, list[dict]] = {rid: [] for rid in index}
    for p in _iter_entity_json(filings_dir):
        entity_id = p.stem
        with p.open("r", encoding="utf-8") as fp:
           data = json.load(fp)
        for rid, meta in index.items():
            disc = {q: data.get(q) for q in meta["qnames"]}
            if any(disc.values()):
                if "EntityRegistrantName" in data:
                    disc["EntityRegistrantName"] = data["EntityRegistrantName"]
                grouped[rid].append({"entity_id": entity_id, "disclosures": disc})

    results: dict[str, dict] = {}
    call_logs: list[dict] = []


    for rid, meta in index.items():
        ents = grouped[rid]
        if not ents:
            results[rid] = {
                "requirement": meta["requirement"],
                "hierarchy_level": meta["hierarchy_level"],
                "analysis": None,
            }
            continue
        ents_json = json.dumps(ents, indent=2, ensure_ascii=False)
        prompt = _prompt(rid, meta["requirement"], ents_json)
        analysis_json, raw = perform_comparative_analysis(
            rule_id=rid,
            requirements_text=meta["requirement"],
            entity_filings_json=ents_json,
        )
        results[rid] = {
            "requirement": meta["requirement"],
            "hierarchy_level": meta["hierarchy_level"],
            "analysis": analysis_json,
        }
        call_logs.append({
            "rule_id": rid,
            "call_type": "comparative",
            "input_payload": {"requirements": meta["requirement"], "entities": ents},
            "prompt": prompt,
            "raw_response": raw,
        })


    exec_summaries: dict[str, dict] = {}
    for rid, meta in index.items():
        if meta["hierarchy_level"] != 1:
            continue
        rel = [r for r in results if r == rid or r.startswith(f"{rid}.")]
        collected = {r: results[r]["analysis"] for r in rel if results[r]["analysis"] is not None}
        if not collected:
            continue
        collected_json = json.dumps(collected, indent=2, ensure_ascii=False)
        summary_json, raw_sum, sum_prompt = perform_executive_summary(
            top_rule_id=rid, grouped_analysis_json=collected_json
        )
        exec_summaries[rid] = summary_json
        results[rid]["executive_summary"] = summary_json
        call_logs.append({
            "rule_id": rid,
            "call_type": "executive_summary",
            "input_payload": {"comparative_analyses": collected},
            "prompt": sum_prompt,
            "raw_response": raw_sum,
        })

    ensure_dir(output_path.parent)
    json.dump(results, output_path.open("w", encoding="utf-8"), indent=2, ensure_ascii=False)
    ensure_dir(exec_output_path.parent)
    json.dump(exec_summaries, exec_output_path.open("w", encoding="utf-8"), indent=2, ensure_ascii=False)
    ensure_dir(call_log_path.parent)
    json.dump(call_logs, call_log_path.open("w", encoding="utf-8"), indent=2, ensure_ascii=False)


def main() -> None:
    ap = argparse.ArgumentParser(description="Step 2: analyses + summaries (minimal)")
    ap.add_argument("--filings-dir", type=Path, default=Path("output/entity_filings_json"))
    ap.add_argument("--mapping-path", type=Path, default=Path("input/taxonomy/cyd_2024_concept_mapping.json"))
    ap.add_argument("--output-path", type=Path, default=Path("output/analysis_results.json"))
    ap.add_argument("--exec-output-path", type=Path, default=Path("output/executive_summaries.json"))
    ap.add_argument("--call-log-path", type=Path, default=Path("logs/step2_llm_calls.json"))
    args = ap.parse_args()
    analyze(args.filings_dir, args.mapping_path, args.output_path, args.exec_output_path, args.call_log_path)

if __name__ == "__main__":
    main()