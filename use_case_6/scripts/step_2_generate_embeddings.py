import json
from typing import List, Dict, Any, Tuple
import sys
import os
from utils.file_handler import load_json_file, write_to_json_file
from retrieval.embedder import generate_embedding


def parse_outsourcing_doc(json_file: str, output_dir: str) -> None:
    """
    Reads  JSON file, generates embeddings for its logical units, and saves the updated data.

    :param json_file: JSON file containing segmented logical units.
    :param output_dir: where updated JSON with embeddings will be saved.
    """
    try:
        data: Dict[str, Any] = load_json_file(json_file)

        filtered_segments: List[Dict[str, Any]] = []

        for lu in data.get("segmented_logical_units", []):
            content_str = "".join(lu.get("logical_unit_content", []))

            if len(content_str) >= 50:
                heading = lu.get("logical_unit_heading", "")
                lu["logical_unit_content_full"] = (
                    f"{heading} {content_str}".strip()
                )
                embedding_vector = generate_embedding(lu["logical_unit_content_full"])
                if not embedding_vector:
                    print(
                        f"Warning: Failed to generate embedding for logical units: {lu['logical_unit_content_full']}"
                    )

                lu["logical_unit_content_full_embedding"] = embedding_vector
                filtered_segments.append(lu)

        data["segmented_logical_units"] = filtered_segments
        agreement_embeddings_path = os.path.join(
            output_dir, "Outsourcing_Agreement_Embeddings.json"
        )
        write_to_json_file(agreement_embeddings_path, data, indent=4)
        print(f"Embeddings successfully saved to {agreement_embeddings_path}")
    except FileNotFoundError:
        print(f"Error: The file '{json_file}' was not found.")
    except json.JSONDecodeError:
        print(
            f"Error: Failed to decode JSON in '{json_file}'. Ensure it's correctly formatted."
        )
    except Exception as e:
        print(f"Unexpected error: {e}")


def parse_requirement_docs(doc: str, output_dir: str) -> None:
    """
    Reads requirement document to generate and save embeddings.

    :param doc: requirements file in JSON format.
    :param output_dir: path to save output embeddings.
    """
    try:
        requirements: List[Dict[str, Any]] = load_json_file(doc)

        for req in requirements:
            if "requirement_description" in req and isinstance(
                req["requirement_description"], str
            ):
                embedding_vector = generate_embedding(req["requirement_description"])
                if not embedding_vector:
                    print(
                        f"Warning: Failed to generate embedding for requirement: {req['requirement_description']}"
                    )
                req["requirement_description_embedding"] = embedding_vector
        requirements_embeddings_path = os.path.join(
            output_dir, "Outsourcing_Requirements_Embeddings.json"
        )
        write_to_json_file(requirements_embeddings_path, requirements, indent=4)
        print(f"Embeddings successfully saved to {requirements_embeddings_path}")
    except FileNotFoundError:
        print(f"Error: The file '{doc}' was not found.")
    except json.JSONDecodeError:
        print(
            f"Error: Failed to decode JSON in '{doc}'. Ensure it's correctly formatted."
        )
    except Exception as e:
        print(f"Unexpected error: {e}")


def create_embeddings(
    agreement_json_path: str, requirements_json: str, output_dir: str
) -> Tuple[str, str]:
    """
    Generates embeddings for both the outsourcing agreement and requirements.

    params:-
        agreement_json_path: Path to the input outsourcing agreement JSON file.
        requirements_json: Path to the input outsourcing requirements JSON file.
        output_dir: Path to save the requirements embeddings and agreement embeddings.
    return:
         tuple :- path to json files of requirements embeddings and agreement embeddings.
    """
    agreement_embeddings_path = os.path.join(
        output_dir, "Outsourcing_Agreement_Embeddings.json"
    )
    requirements_embedding_path = os.path.join(
        output_dir, "Outsourcing_Requirements_Embeddings.json"
    )
    parse_outsourcing_doc(agreement_json_path, output_dir)
    parse_requirement_docs(requirements_json, output_dir)

    if not (
        os.path.exists(agreement_embeddings_path)
        and os.path.exists(requirements_embedding_path)
    ):
        print("Embeddings file not found. Execution Stopped")
        sys.exit(0)

    return agreement_embeddings_path, requirements_embedding_path
