from typing import Optional, Dict, Set
import os
import json
from llm.llm_engine import (
    get_prompt_for_benchmarking_dimensions,
    get_prompt_for_unmapped_logical_unit,
    get_prompt_for_mapping_logical_units,
    get_openai_response,
)
from utils.file_handler import read_json_file, write_to_json_file


def is_not_applicable(summary: str) -> bool:
    """
    Checks if a logical unit's summary indicates it should be excluded from analysis.

    Args:
        summary (str): The summary text to evaluate

    Returns:
        bool: True if the summary is "not applicable" (case-insensitive), False otherwise
    """
    if not summary:
        return False
    normalized = summary.lower().strip().rstrip(".")
    return normalized == "not applicable"


def filtering_non_logical_units(processed_regulations_path: str):
    """
    Filters out non-applicable logical units from regulation JSON files.
    Args:
        processed_regulations_path (str): Path to the root directory containing regulation files
    """
    processed_dir = os.path.join(
        processed_regulations_path, "Regulations", "Processed Regulations"
    )
    json_files = [f for f in os.listdir(processed_dir) if f.lower().endswith(".json")]
    for filename in json_files:
        if "analysis_framework" in filename or "mapping" in filename:
            continue
        path = os.path.join(processed_dir, filename)
        data = read_json_file(path)
        original_response = data.get("response", [])
        if not original_response:
            continue

        new_response = []
        for unit in original_response:
            summary = unit.get("logical_unit_summary", "")
            if is_not_applicable(summary):
                continue
            new_response.append(unit)
        data["response"] = new_response
        write_to_json_file(path, data, indent=2)


def create_analysis_framework(processed_regulations_path: str) -> None:
    """
    Creates a benchmarking analysis framework by processing regulatory documents.
    Args:
        processed_regulations_path (str): Path to the root directory containing regulation files
    """
    processed_dir = os.path.join(
        processed_regulations_path, "Regulations", "Processed Regulations"
    )
    json_files = [
        f
        for f in os.listdir(processed_dir)
        if f.lower().endswith(".json")
        and "analysis_framework" not in f.lower()
        and "mapping" not in f.lower()
    ]

    full_input_sections = []
    for filename in json_files:
        path = os.path.join(processed_dir, filename)
        data = read_json_file(path)
        if "response" not in data:
            continue

        file_section = f"""
            File: 
            - {filename}
            Regulation Overview:
            - {data.get("regulation_overview", "")}
        """
        for logical_unit in data["response"]:
            file_section += (
                f"\nLogical Unit ID: {logical_unit.get('logical_unit_id', '')}"
                f"\nHeading: {logical_unit.get('logical_unit_heading', '')}"
                f"\nSummary: {logical_unit.get('logical_unit_summary', '')}"
            )

        full_input_sections.append(file_section)
    if not full_input_sections:
        print("No content found to build the analysis framework.")
        return

    combined_input = "\n".join(full_input_sections)
    prompt = get_prompt_for_benchmarking_dimensions(combined_input)
    analysis_framework_str = get_openai_response(prompt, model="o1")
    output_path = os.path.join(processed_dir, "benchmarking_analysis_framework.json")
    try:
        analysis_framework = json.loads(analysis_framework_str)
    except json.JSONDecodeError:
        print(f"LLM returned invalid JSON: {analysis_framework_str}")
        analysis_framework = {"error": "Invalid JSON from LLM"}

    output_data = {"analysis_framework": analysis_framework}
    write_to_json_file(output_path, output_data, indent=2)

    print(f"Analysis framework created successfully at: {output_path}")


def generate_initial_dimension_mapping(processed_regulations_path: str) -> None:
    """
    Creates the initial mapping between regulatory logical units and benchmarking dimensions.
    Args:
        processed_regulations_path (str): Path to the root directory containing processed regulation files
    """
    processed_dir = os.path.join(
        processed_regulations_path, "Regulations", "Processed Regulations"
    )
    framework_file_path = os.path.join(
        processed_dir, "benchmarking_analysis_framework.json"
    )
    if not os.path.isfile(framework_file_path):
        print("No Benchmark Analysis Framework JSON file found.")
        return

    framework_data = read_json_file(framework_file_path)
    if "analysis_framework" not in framework_data:
        print(
            "'analysis_framework' key not found in benchmarking_analysis_framework.json."
        )
        return

    try:
        if isinstance(framework_data["analysis_framework"], str):
            parsed_framework = json.loads(framework_data["analysis_framework"])
        else:
            parsed_framework = framework_data["analysis_framework"]

    except json.JSONDecodeError:
        print("Unable to parse the 'analysis_framework' field as valid JSON.")
        return

    if (
        "benchmarking_dimensions" not in parsed_framework
        or not parsed_framework["benchmarking_dimensions"]
    ):
        print(
            "'benchmarking_dimensions' key not found or empty in the parsed analysis framework."
        )
        return

    dimension_definitions = parsed_framework["benchmarking_dimensions"][0]
    if not isinstance(dimension_definitions, dict):
        print(
            "Expected a dictionary of dimension definitions under 'benchmarking_dimensions'."
        )
        return

    final_dimensions_mapping = {}
    for dimension_name in dimension_definitions.keys():
        final_dimensions_mapping[dimension_name] = {}

    json_files = [
        f
        for f in os.listdir(processed_dir)
        if f.lower().endswith(".json")
        and "analysis_framework" not in f.lower()
        and "mapping" not in f.lower()
    ]

    for json_file in json_files:
        path = os.path.join(processed_dir, json_file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "response" not in data:
            continue

        for lu in data["response"]:
            lu_id = lu.get("logical_unit_id", "")
            lu_heading = lu.get("logical_unit_heading", "")
            lu_summary = lu.get("logical_unit_summary", "")
            dimension_text = "\n".join(
                [f"{k}: {v}" for k, v in dimension_definitions.items()]
            )
            try:
                prompt = get_prompt_for_mapping_logical_units(
                    dimension_text, lu_id, lu_heading, lu_summary
                )
                content = get_openai_response(prompt, model="o3-mini")

                if "Error occurred" in content:
                    print(
                        f"Error calling the API for file '{json_file}', LU '{lu_id}': {content}"
                    )
                    continue

                print(f"Successfully processed LU '{lu_id}' for file '{json_file}'")

            except Exception as e:
                print(
                    f"An error occurred while processing file '{json_file}', LU '{lu_id}': {str(e)}"
                )
                continue

            try:
                dimension_json = json.loads(content)
            except json.JSONDecodeError:
                print(
                    f"Could not parse API response as JSON for file '{json_file}', LU '{lu_id}'."
                )
                continue

            bdm_array = dimension_json.get("benchmarking_dimensions_mapping", [])
            if not bdm_array or not isinstance(bdm_array, list):
                print(
                    f"Missing or invalid 'benchmarking_dimensions_mapping' for file '{json_file}', LU '{lu_id}'."
                )
                continue

            dimension_flags = bdm_array[0] if bdm_array else {}
            if not isinstance(dimension_flags, dict):
                print(
                    f"Expected a dictionary of dimension relevance flags, file '{json_file}', LU '{lu_id}'."
                )
                continue

            for dim_name, relevance in dimension_flags.items():
                if relevance == 1:
                    key_for_file = f"{json_file}_logical_units"
                    if key_for_file not in final_dimensions_mapping[dim_name]:
                        final_dimensions_mapping[dim_name][key_for_file] = []
                    final_dimensions_mapping[dim_name][key_for_file].append(lu_id)

    final_output = {"benchmarking_dimensions_mapping": [final_dimensions_mapping]}
    output_file_path = os.path.join(
        processed_dir, "benchmarking_analysis_framework_mapping.json"
    )
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    print(f"Initial mapping JSON created (by logical unit): {output_file_path}")


def get_unmapped_lids(processed_dir: str) -> Optional[Dict[str, Set[str]]]:
    """
    Identifies logical units that weren't mapped to any benchmarking dimensions.
    Args:
        processed_dir (str): Path to the directory containing processed regulation files
    Returns:
        dict: Contains:
            - "unmapped_reg1_lids": Set of unmapped logical unit IDs from regulation_1.json
            - "unmapped_reg2_lids": Set of unmapped logical unit IDs from regulation_2.json
            - "reg1_data": Full content of regulation_1.json (for reference)
            - "reg2_data": Full content of regulation_2.json (for reference)
        None: If required files are missing or invalid
    """
    base_path = processed_dir
    mapping_file = os.path.join(
        base_path, "benchmarking_analysis_framework_mapping.json"
    )

    if not os.path.isfile(mapping_file):
        print("Mapping file not found. Cannot check unmapped LIDs.")
        return None

    mapping_data = read_json_file(mapping_file)
    dimension_mappings = mapping_data["benchmarking_dimensions_mapping"][0]
    mapped_reg1_lids = set()
    mapped_reg2_lids = set()
    for _, dim_data in dimension_mappings.items():
        reg1_units = dim_data.get("regulation_1.json_logical_units", [])
        reg2_units = dim_data.get("regulation_2.json_logical_units", [])
        mapped_reg1_lids.update(str(lid) for lid in reg1_units)
        mapped_reg2_lids.update(str(lid) for lid in reg2_units)

    reg1_file_path = os.path.join(base_path, "regulation_1.json")
    reg2_file_path = os.path.join(base_path, "regulation_2.json")

    if not (os.path.isfile(reg1_file_path) and os.path.isfile(reg2_file_path)):
        print("One or both regulation_X.json files are missing.")
        return None

    reg1_data = read_json_file(reg1_file_path)
    reg2_data = read_json_file(reg2_file_path)

    all_reg1_lids = {str(item["logical_unit_id"]) for item in reg1_data["response"]}
    all_reg2_lids = {str(item["logical_unit_id"]) for item in reg2_data["response"]}

    unmapped_reg1_lids = all_reg1_lids - mapped_reg1_lids
    unmapped_reg2_lids = all_reg2_lids - mapped_reg2_lids
    return {
        "unmapped_reg1_lids": unmapped_reg1_lids,
        "unmapped_reg2_lids": unmapped_reg2_lids,
        "reg1_data": reg1_data,
        "reg2_data": reg2_data,
    }


def map_unmapped_logical_units(
    dimension_mappings: dict,
    unmapped_reg1_info: list,
    unmapped_reg2_info: list,
    dimension_overview_text: str,
) -> dict:
    """
    Maps unmapped logical units to benchmarking dimensions.

    Args:
        dimension_mappings (dict): Current dimension mappings structure.
        unmapped_reg1_info (list): List of (lu_id, heading, summary) tuples from regulation 1.
        unmapped_reg2_info (list): List of (lu_id, heading, summary) tuples from regulation 2.
        dimension_overview_text (str): Overview of existing dimensions.

    Returns:
        dict: Contains "new_or_updated_dimensions" list with new/expanded dimension mappings.
    """

    new_or_updated_dimensions = []

    def map_single_lu(
        lu_id: str, lu_heading: str, lu_summary: str, regulation_tag: str
    ) -> dict:
        """
        Maps a single logical unit to dimensions using LLM.

        Args:
            lu_id (str): Logical unit ID.
            lu_heading (str): Heading text of the logical unit.
            lu_summary (str): Summary content of the logical unit.
            regulation_tag (str): Indicates which regulation the LU belongs to.

        Returns:
            dict: Contains new or updated dimensions for this LU, or empty dict on error.
        """

        prompt = get_prompt_for_unmapped_logical_unit(
            dimension_overview_text, regulation_tag, lu_id, lu_heading, lu_summary
        )
        raw_content = get_openai_response(prompt.strip(), model="o3-mini")

        if "Error occurred" in raw_content:
            print(f"Error calling LLM for LU '{lu_id}': {raw_content}")
            return {}

        try:
            dimension_json = json.loads(raw_content)
            print(f"LLM response for LU {lu_id}: {dimension_json}")
        except json.JSONDecodeError:
            print(f"Could not parse the model's response as JSON for LU '{lu_id}'.")
            return {}

        bdm_list = dimension_json.get("benchmarking_dimensions_mapping", [])
        if not bdm_list or not isinstance(bdm_list, list):
            print(
                f"Missing or invalid 'benchmarking_dimensions_mapping' in LLM response for LU '{lu_id}'."
            )
            return {}

        new_or_updated_block = []

        dimension_map = bdm_list[0] if bdm_list else {}
        if not isinstance(dimension_map, dict):
            print(f"Invalid dimension_map for LU '{lu_id}'. Expected a dict.")
            return {}

        for dim_name, label_desc_str in dimension_map.items():
            label_desc_str = label_desc_str.strip()

            if ":" in label_desc_str:
                dim_label, dim_desc = label_desc_str.split(":", 1)
                dim_label = dim_label.strip()
                dim_desc = dim_desc.strip()
            else:
                dim_label = label_desc_str
                dim_desc = ""

            dim_data = {
                "dimension_label": dim_label,
                "dimension_description": dim_desc,
                "regulation_1.json_logical_units": [],
                "regulation_2.json_logical_units": [],
            }

            if regulation_tag == "regulation_1.json_logical_units":
                dim_data["regulation_1.json_logical_units"].append(lu_id)
            else:
                dim_data["regulation_2.json_logical_units"].append(lu_id)

            new_or_updated_block.append({dim_name: dim_data})

        return {"new_or_updated_dimensions": new_or_updated_block}

    for lu_id, lu_heading, lu_summary in unmapped_reg1_info:
        single_result = map_single_lu(
            lu_id=lu_id,
            lu_heading=lu_heading,
            lu_summary=lu_summary,
            regulation_tag="regulation_1.json_logical_units",
        )
        if single_result and "new_or_updated_dimensions" in single_result:
            new_or_updated_dimensions.extend(single_result["new_or_updated_dimensions"])

    for lu_id, lu_heading, lu_summary in unmapped_reg2_info:
        single_result = map_single_lu(
            lu_id=lu_id,
            lu_heading=lu_heading,
            lu_summary=lu_summary,
            regulation_tag="regulation_2.json_logical_units",
        )
        if single_result and "new_or_updated_dimensions" in single_result:
            new_or_updated_dimensions.extend(single_result["new_or_updated_dimensions"])

    return {"new_or_updated_dimensions": new_or_updated_dimensions}


def merge_new_mappings(
    existing_dimensions: dict, new_additions: dict, processed_dir: str
) -> dict:
    """
    Merges new dimension mappings with existing ones and updates the framework.

    Args:
        existing_dimensions (dict): Current dimension mappings structure.
        new_additions (dict): New dimensions/mappings to incorporate.
        processed_dir (str): Directory path for framework updates.

    Returns:
        dict: Updated dimension mappings with merged content.
    """

    if "new_or_updated_dimensions" not in new_additions:
        return existing_dimensions

    updates = new_additions["new_or_updated_dimensions"]
    newly_created_dimensions = {}

    for dim_obj in updates:
        for dim_name, dim_data in dim_obj.items():
            if dim_name not in existing_dimensions:
                existing_dimensions[dim_name] = {
                    "dimension_label": dim_data.get("dimension_label", dim_name),
                    "dimension_description": dim_data.get("dimension_description", ""),
                    "regulation_1.json_logical_units": [],
                    "regulation_2.json_logical_units": [],
                }
                newly_created_dimensions[dim_name] = {
                    "dimension_label": existing_dimensions[dim_name]["dimension_label"],
                    "dimension_description": existing_dimensions[dim_name][
                        "dimension_description"
                    ],
                }

            if "dimension_label" in dim_data:
                existing_dimensions[dim_name]["dimension_label"] = dim_data[
                    "dimension_label"
                ]
            if "dimension_description" in dim_data:
                existing_dimensions[dim_name]["dimension_description"] = dim_data[
                    "dimension_description"
                ]

            old_reg1_list = existing_dimensions[dim_name].get(
                "regulation_1.json_logical_units", []
            )
            new_reg1_list = dim_data.get("regulation_1.json_logical_units", [])
            old_reg1_set = {x for x in old_reg1_list if isinstance(x, str)}
            new_reg1_set = {x for x in new_reg1_list if isinstance(x, str)}
            merged_reg1_set = old_reg1_set.union(new_reg1_set)
            existing_dimensions[dim_name]["regulation_1.json_logical_units"] = list(
                merged_reg1_set
            )

            old_reg2_list = existing_dimensions[dim_name].get(
                "regulation_2.json_logical_units", []
            )
            new_reg2_list = dim_data.get("regulation_2.json_logical_units", [])
            old_reg2_set = {x for x in old_reg2_list if isinstance(x, str)}
            new_reg2_set = {x for x in new_reg2_list if isinstance(x, str)}
            merged_reg2_set = old_reg2_set.union(new_reg2_set)
            existing_dimensions[dim_name]["regulation_2.json_logical_units"] = list(
                merged_reg2_set
            )

    if newly_created_dimensions:
        update_analysis_framework_with_new_dims(processed_dir, newly_created_dimensions)

    return existing_dimensions


def update_analysis_framework_with_new_dims(processed_dir: str, new_dims: dict) -> None:
    """
    Updates the benchmarking framework JSON file with newly created dimensions.

    Args:
        processed_dir (str): Path to directory containing framework file
        new_dims (dict): New dimensions to add
    """
    framework_file_path = os.path.join(
        processed_dir, "benchmarking_analysis_framework.json"
    )

    with open(framework_file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    analysis_framework_str = raw_data.get("analysis_framework", "")
    try:
        analysis_data = json.loads(analysis_framework_str)
    except json.JSONDecodeError:
        print("Error: Failed to parse framework JSON structure")
        return

    dims_list = analysis_data.get("benchmarking_dimensions", [])
    if not dims_list:
        dims_list = [{}]
    existing_dim_dict = dims_list[0]

    for dim_key, dim_vals in new_dims.items():
        if dim_key not in existing_dim_dict:
            label = dim_vals.get("dimension_label", dim_key)
            desc = dim_vals.get("dimension_description", "")
            combined_str = f"{label}: {desc}".strip(": ")
            existing_dim_dict[dim_key] = combined_str

    dims_list[0] = existing_dim_dict
    analysis_data["benchmarking_dimensions"] = dims_list

    raw_data["analysis_framework"] = json.dumps(
        analysis_data, ensure_ascii=False, indent=2
    )

    with open(framework_file_path, "w", encoding="utf-8") as out_f:
        json.dump(raw_data, out_f, ensure_ascii=False, indent=2)


def agentic_mapping_loop(input_dir: str) -> None:
    """
    Executes an iterative loop to map all unmapped logical units to dimensions.
    Args:
        input_dir (str): Path to root directory containing regulation files
    """
    processed_dir = os.path.join(input_dir, "Regulations", "Processed Regulations")
    mapping_file_path = os.path.join(
        processed_dir, "benchmarking_analysis_framework_mapping.json"
    )
    framework_file_path = os.path.join(
        processed_dir, "benchmarking_analysis_framework.json"
    )
    raw_framework = read_json_file(framework_file_path)
    analysis_framework_str = raw_framework.get("analysis_framework", "")
    try:
        if isinstance(analysis_framework_str, str):
            analysis_framework_data = json.loads(analysis_framework_str)
        else:
            analysis_framework_data = analysis_framework_str

    except json.JSONDecodeError:
        print("Error: Invalid framework JSON structure")
        return

    if not isinstance(analysis_framework_data, dict):
        print("Error: Framework data must be a dictionary")
        return

    dims_list = analysis_framework_data.get("benchmarking_dimensions", [])
    if not dims_list or not isinstance(dims_list, list):
        print("Error: Missing or invalid benchmarking dimensions")
        return

    dimension_definitions = dims_list[0] if len(dims_list) > 0 else {}
    if not isinstance(dimension_definitions, dict):
        print("Error: Dimension definitions must be a dictionary")
        return

    dimension_overview_entries = [
        f"{dim_label}: {dim_description}"
        for dim_label, dim_description in dimension_definitions.items()
    ]
    dimension_overview_text = "\n".join(dimension_overview_entries)

    while True:
        if not os.path.isfile(mapping_file_path):
            print("Error: Missing mapping file - run initial mapping first")
            return

        results = get_unmapped_lids(processed_dir)
        if not results:
            print("Error: Failed to retrieve unmapped units")
            return

        unmapped_reg1 = results["unmapped_reg1_lids"]
        unmapped_reg2 = results["unmapped_reg2_lids"]
        if not unmapped_reg1 and not unmapped_reg2:
            print("Completion: All logical units mapped")
            break

        reg1_data, reg2_data = results["reg1_data"], results["reg2_data"]
        unmapped_reg1_info = [
            (
                str(item["logical_unit_id"]),
                item["logical_unit_heading"],
                item["logical_unit_summary"],
            )
            for item in reg1_data["response"]
            if str(item["logical_unit_id"]) in unmapped_reg1
        ]
        unmapped_reg2_info = [
            (
                str(item["logical_unit_id"]),
                item["logical_unit_heading"],
                item["logical_unit_summary"],
            )
            for item in reg2_data["response"]
            if str(item["logical_unit_id"]) in unmapped_reg2
        ]
        with open(mapping_file_path, "r", encoding="utf-8") as f:
            full_mapping = json.load(f)
        dimension_mappings = full_mapping.get("benchmarking_dimensions_mapping", [{}])[
            0
        ]

        new_assignments = map_unmapped_logical_units(
            dimension_mappings=dimension_mappings,
            unmapped_reg1_info=unmapped_reg1_info,
            unmapped_reg2_info=unmapped_reg2_info,
            dimension_overview_text=dimension_overview_text,
        )

        if not new_assignments or "new_or_updated_dimensions" not in new_assignments:
            print("Warning: No new mappings generated - stopping iteration")
            break

        updated_mappings = merge_new_mappings(
            dimension_mappings, new_assignments, processed_dir
        )
        full_mapping["benchmarking_dimensions_mapping"][0] = updated_mappings
        write_to_json_file(mapping_file_path, full_mapping)


def defining_bench_mark_dimensions(input_dir: str) -> None:
    """
    Main workflow for defining benchmarking dimensions and mappings.
    Args:
        input_dir (str): Path to root directory containing regulation files
    Returns:
        str: Path to final mapping file
    """
    filtering_non_logical_units(input_dir)
    create_analysis_framework(input_dir)
    generate_initial_dimension_mapping(input_dir)
    agentic_mapping_loop(input_dir)
