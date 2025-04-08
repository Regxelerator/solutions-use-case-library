import re
import os
import json
from llm.llm_engine import (
    get_prompt_to_prepare_comparative_analysis,
    get_prompt_for_non_core_dimensions,
    get_openai_response,
)
from utils.file_handler import write_to_json_file, read_json_file


def identify_non_core_dimensions(mapped_dimensions):
    """
    Identifies non-core benchmarking dimensions based on the provided mapping of dimensions.

    Args:
        mapped_dimensions (dict): The mapping of benchmarking dimensions with associated regulatory content.

    Returns:
        list: A list of non-core dimension keys if identified, otherwise an empty list.
    """
    prompt = get_prompt_for_non_core_dimensions(mapped_dimensions)

    content = get_openai_response(prompt, model="o3-mini")

    if "Error" in content:
        return []

    try:
        parsed_response = json.loads(content)
    except json.JSONDecodeError:
        print(
            "Could not parse the response for non-core dimension identification. Returning empty list."
        )
        return []

    non_core_dims = parsed_response.get("non_core_dimensions", [])

    if not isinstance(non_core_dims, list):
        print("Response format not as expected. Returning empty list.")
        return []

    return non_core_dims


def render_logical_units(logical_units: list[dict[str, str]]) -> str:
    """
    Renders the content of logical units into a formatted string.

    Args:
        logical_units (list): A list of dictionaries, each containing the following keys:
            - logical_unit_id (str): The unique identifier of the logical unit.
            - logical_unit_heading (str): The heading or title of the logical unit.
            - logical_unit_content (list): A list of content or details associated with the logical unit.

    Returns:
        str: A formatted string where each logical unit is represented with its ID,
             heading, and content in a structured format.
    """

    lines = []
    for lu in logical_units:
        lu_id = lu.get("logical_unit_id", "")
        lu_heading = lu.get("logical_unit_heading", "")
        lu_content = lu.get("logical_unit_content", [])
        content_str = "\n".join(lu_content)
        lines.append(
            f"  - Logical Unit ID: {lu_id} Heading: {lu_heading}  Content: {content_str}"
        )
    return "\n".join(lines)


def read_regulation_overview(data_dict: dict) -> str:
    """
    Extracts the 'regulation_overview' from the provided dictionary.


    Args:
        data_dict (dict): A dictionary containing regulation-related data.


    Returns:
        str: The value associated with the 'regulation_overview' key if found,
             or an empty string if the key does not exist in the dictionary.
    """
    return data_dict.get("regulation_overview", "")


def performing_comparative_analysis(input_dir: str) -> str | None:
    """
    Performs a comparative analysis on regulatory data stored in the specified input directory.
    Args:
        input_dir (str): The path to the directory containing the regulatory data files.
    Returns:
        str : path to the directory where benchmarking analysis will be stored
    """
    regulations_base_dir = os.path.join(
        input_dir, "Regulations", "Processed Regulations"
    )
    mapping_file_path = os.path.join(
        regulations_base_dir, "benchmarking_analysis_framework_mapping.json"
    )
    analysis_framework_path = os.path.join(
        regulations_base_dir, "benchmarking_analysis_framework.json"
    )
    mapped_dimensions_output_path = os.path.join(
        regulations_base_dir, "mapped_benchmarking_dimensions.json"
    )
    final_analysis_output_path = os.path.join(input_dir, "benchmarking_analysis.json")

    if not os.path.isfile(mapping_file_path):
        print(f"File '{mapping_file_path}' not found.")
        return
    if not os.path.isfile(analysis_framework_path):
        print(f"File '{analysis_framework_path}' not found.")
        return

    regulation_files = [
        f
        for f in os.listdir(regulations_base_dir)
        if "regulation" in f.lower() and f.lower().endswith(".json")
    ]
    if not regulation_files:
        print("No regulation JSON files found.")
        return

    mapping_data = read_json_file(mapping_file_path)
    raw_pretty_dims_data = read_json_file(analysis_framework_path)

    analysis_framework_str = raw_pretty_dims_data.get("analysis_framework", "")
    if isinstance(analysis_framework_str, str):
        try:
            analysis_framework_data = json.loads(analysis_framework_str)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in framework")
            return None
    elif isinstance(analysis_framework_str, dict):
        analysis_framework_data = analysis_framework_str
    else:
        print("Error: Unexpected framework format")
        return None

    if "benchmarking_dimensions_mapping" not in mapping_data:
        print("Benchmarking dimensions key missing in mapping JSON.")
        return
    if "benchmarking_dimensions" not in analysis_framework_data:
        print("Benchmarking dimensions key missing in parsed analysis framework JSON.")
        return

    reg_data_dict = {}
    for file_name in regulation_files:
        match = re.search(r"regulation_(\d+).json", file_name, re.IGNORECASE)
        if match:
            reg_number = match.group(1)
            file_path = os.path.join(regulations_base_dir, file_name)
            data = read_json_file(file_path)
            if "response" not in data:
                print(f"No 'response' key in {file_name}.")
                return
            reg_data_dict[reg_number] = data

    if not reg_data_dict:
        print("No valid regulation data loaded.")
        return

    mapping_list = mapping_data["benchmarking_dimensions_mapping"]
    if not mapping_list or not isinstance(mapping_list, list):
        print("Benchmarking dimensions mapping is not a non-empty list.")
        return
    mapping_dict = mapping_list[0]

    dims_list = analysis_framework_data["benchmarking_dimensions"]
    if not dims_list or not isinstance(dims_list, list):
        print("Benchmarking dimensions is not a non-empty list.")
        return
    dimension_names_dict = dims_list[0]

    lu_dicts = {}
    for reg_number, reg_data in reg_data_dict.items():
        lu_dicts[reg_number] = {
            str(item["logical_unit_id"]): item for item in reg_data["response"]
        }

    output = {}
    for dimension_key, dimension_mapping_info in mapping_dict.items():
        dimension_output = {
            "dimension_name": dimension_names_dict.get(dimension_key, "")
        }
        for reg_number in lu_dicts:
            reg_key = f"regulation_{reg_number}.json_logical_units"
            lu_ids = dimension_mapping_info.get(reg_key, [])
            collected_units = []
            for lu_id in lu_ids:
                lu_id_str = str(lu_id)
                if lu_id_str in lu_dicts[reg_number]:
                    unit = lu_dicts[reg_number][lu_id_str]
                    collected_units.append(
                        {
                            "logical_unit_id": unit.get("logical_unit_id"),
                            "logical_unit_heading": unit.get("logical_unit_heading"),
                            "logical_unit_content": unit.get(
                                "logical_unit_content", []
                            ),
                        }
                    )
            dimension_output[reg_key] = collected_units
        output[dimension_key] = dimension_output

    write_to_json_file(mapped_dimensions_output_path, output, indent=2)

    print(f"Created mapping output: {mapped_dimensions_output_path}")

    if not os.path.isfile(mapped_dimensions_output_path):
        print(f"File '{mapped_dimensions_output_path}' not found.")
        return
    if not os.path.isfile(analysis_framework_path):
        print(f"File '{analysis_framework_path}' not found.")
        return

    mapped_dimensions = read_json_file(mapped_dimensions_output_path)

    with open(analysis_framework_path, "r", encoding="utf-8") as f:
        benchmarking_framework = f.read().strip()

    combined_overviews_parts = []
    for reg_number, data_dict in reg_data_dict.items():
        overview = read_regulation_overview(data_dict)
        combined_overviews_parts.append(
            f"Regulation {reg_number} Overview:\n{overview}"
        )

    combined_overviews = "\n\n".join(combined_overviews_parts)

    dimensions_to_skip = identify_non_core_dimensions(mapped_dimensions)
    print("Non-core dimensions identified:", dimensions_to_skip)

    analysis_results = []

    for dimension_key, dimension_data in mapped_dimensions.items():
        if dimension_key in dimensions_to_skip:
            print(f"Skipping dimension '{dimension_key}' as non-core.")
            continue

        dim_name = dimension_data.get("dimension_name", "N/A")

        dimension_description = f"Dimension Name: {dim_name}\n\nMapped Provisions:\n\n"
        for key, regs_units in dimension_data.items():
            if key.startswith("regulation_") and isinstance(regs_units, list):
                dimension_description += (
                    f"From {key}:\n{render_logical_units(regs_units)}\n\n"
                )

        prompt = get_prompt_to_prepare_comparative_analysis(
            dimension_description=dimension_description,
            benchmarking_framework=benchmarking_framework,
            combined_overviews=combined_overviews,
        )

        content = get_openai_response(
            prompt=prompt, model="o1", response_format={"type": "json_object"}
        )
        if "Error occurred" not in content:
            print(f"Received content: {content}")
            try:
                parsed_response = json.loads(content)
            except json.JSONDecodeError:
                print(
                    f"Could not parse response for dimension '{dim_name}' as JSON. Skipping."
                )
                continue
        else:
            print(f"Failed to retrieve valid response: {content}")
            return

        benchmarking_analysis = parsed_response.get("benchmarking_analysis", {})
        country_provisions = benchmarking_analysis.get("country_provisions", {})
        comparative_analysis = benchmarking_analysis.get("comparative_analysis", "")

        analysis_results.append(
            {
                "dimension_name": dim_name,
                "country_provisions": country_provisions,
                "comparative_analysis": comparative_analysis,
            }
        )

    final_output = {"benchmarking_analysis": analysis_results}

    write_to_json_file(final_analysis_output_path, final_output, indent=2)

    print(f"Benchmarking analysis JSON created: {final_analysis_output_path}")
    return final_analysis_output_path
