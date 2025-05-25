import argparse
import json
import logging
from pathlib import Path
from collections import OrderedDict
from xml.etree import ElementTree as ET

from utils.file_handler import ensure_dir, iter_xml_files

def load_concept_mapping(path: Path | str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_entity_registrant_name(root) -> str | None:

    for elem in root.iter():
        tag = elem.tag
        if "}" in tag:
            localname = tag.split("}", 1)[1]
        else:
            localname = tag
        if localname == "EntityRegistrantName":
            return elem.text
    return None

def extract_concept_values(xml_path: Path, concepts) -> dict:
    concept_by_local = {qname.split(":")[1]: qname for qname in concepts if ":" in qname}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    record = {qname: None for qname in concepts}
    for elem in root.iter():
        tag = elem.tag
        if "}" in tag:
            localname = tag.split("}", 1)[1]
        else:
            localname = tag
        if localname in concept_by_local:
            qname = concept_by_local[localname]
            record[qname] = elem.text
    entity_name = extract_entity_registrant_name(root)
    ordered_record = OrderedDict()
    ordered_record["EntityRegistrantName"] = entity_name
    ordered_record.update(record)
    return ordered_record

def convert(input_dir: Path, output_dir: Path, mapping_path: Path):
    mapping = load_concept_mapping(mapping_path)

    if isinstance(mapping, list):
        mapping_iter = mapping
    else:                    
        mapping_iter = mapping.values()

    concepts = []
    for req in mapping_iter:          
        concepts.extend([concept["qname"] for concept in req.get("concepts", [])])
    concepts = list(sorted(set(concepts)))
    logging.info("Loaded %d CYD concepts from mapping", len(concepts))
    xml_paths = list(iter_xml_files(input_dir))
    if not xml_paths:
        logging.warning("No XML files found under %s", input_dir)
    for xml_path in xml_paths:
        rel_path = xml_path.relative_to(input_dir)
        json_path = output_dir / rel_path.with_suffix('.json')
        ensure_dir(json_path.parent)
        logging.info("Converting %s -> %s", xml_path, json_path)
        record = extract_concept_values(xml_path, concepts)
        with json_path.open('w', encoding='utf-8') as fp:
            json.dump(record, fp, indent=2, ensure_ascii=False)
            fp.write('\n')

def main():
    parser = argparse.ArgumentParser(
        description="Step 1: Convert XBRL instance XML files to JSON by matching concept tag names."
    )
    parser.add_argument(
        "--input-dir", type=Path,
        default=Path("input/entity_filings"),
        help="Directory containing XBRL .xml files",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("output/entity_filings_json"),
        help="Directory to write JSON files",
    )
    parser.add_argument(
        "--mapping-path", type=Path,
        default=Path("input/taxonomy/cyd_2024_concept_mapping.json"),
        help="Path to mapping file",
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s | %(message)s",
    )
    convert(args.input_dir, args.output_dir, args.mapping_path)

if __name__ == "__main__":
    main()