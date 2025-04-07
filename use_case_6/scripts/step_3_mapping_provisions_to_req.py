from typing import List, Dict
from utils.file_handler import load_json_file, write_to_json_file
import os
import math


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Computes the cosine similarity between two vectors.

    :param vec1: First vector as a list of floats.
    :param vec2: Second vector as a list of floats.
    :return: Cosine similarity score (range: -1 to 1, where 1 means identical direction).
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def find_threshold_matches(
    requirement_embedding: List[float], segments: List[Dict], threshold: float = 0.77
) -> List[Dict]:
    """
    Finds segments with cosine similarity above the threshold.

    Args:
        requirement_embedding (List[float]): Embedding vector of the requirement.
        segments (List[Dict]): List of segment dictionaries with embeddings.
        threshold (float, optional): Similarity threshold. Defaults to 0.77.

    Returns:
        List[Dict]: Matched segments with similarity scores.
    """
    matches = []
    for seg in segments:
        seg_emb = seg["logical_unit_content_full_embedding"]
        sim = cosine_similarity(requirement_embedding, seg_emb)
        if sim >= threshold:
            matches.append(
                {
                    "logical_unit_id": seg["logical_unit_id"],
                    "logical_unit_content_full": seg["logical_unit_content_full"],
                    "similarity": sim,
                }
            )
    return matches


def map_requirements_to_agreement(
    agreement_file: str,
    requirements_file: str,
    output_dir: str = "Requirements_Agreement_Matches.json",
) -> str:
    """
    Maps regulatory requirements to agreement sections based on embedding similarity.

    Args:
        agreement_file (str): Path to the agreement embeddings file.
        requirements_file (str): Path to the requirements embeddings file.
        output_dir (str):  path to output dir to  save "Requirements_Agreement_Matches.json".
    return:
        str:path to file Requirements_Agreement_Matches.json
    """
    agreement_data = load_json_file(agreement_file)
    requirements_data = load_json_file(requirements_file)
    segments = agreement_data.get("segmented_logical_units", [])
    if not segments:
        print("No segmented_logical_units found in the agreement data. Exiting.")
        return

    match_output = []
    mapped_lu_ids = set()

    for req in requirements_data:
        requirement_embedding = req["requirement_description_embedding"]
        threshold_matches = find_threshold_matches(
            requirement_embedding, segments, threshold=0.77
        )
        for match in threshold_matches:
            mapped_lu_ids.add(match["logical_unit_id"])
        match_output.append(
            {
                "id": req.get("id", ""),
                "requirement_label": req.get("requirement_label", ""),
                "requirement_description": req.get("requirement_description", ""),
                "number_matches": len(threshold_matches),
                "matches": threshold_matches,
            }
        )
    req_agreement_match_file_path = os.path.join(
        output_dir, "Requirements_Agreement_Matches.json"
    )
    write_to_json_file(req_agreement_match_file_path, match_output, indent=4)
    return req_agreement_match_file_path
