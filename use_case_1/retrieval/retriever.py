import os
import pandas as pd
import numpy as np
import concurrent.futures
from typing import List, Optional
from retrieval.embedder import generate_text_embedding


def load_reference_data_with_embeddings(file_path: str) -> pd.DataFrame:
    """
    Loads the reference dataset and converts stored embedding strings back into NumPy arrays.

    Args:
        file_path (str): Path to the Excel file containing reference complaints.

    Returns:
        pd.DataFrame: DataFrame with complaint text and corresponding embeddings.
    """
    df = pd.read_excel(file_path)
    if isinstance(df["embeddings"][0], str):
        df["embeddings"] = df["embeddings"].apply(
            lambda x: np.array(eval(x), dtype=float)
        )
    return df


def compute_cosine_similarity(
    vector_a: Optional[List[float]], vector_b: Optional[List[float]]
) -> float:
    """
    Computes the cosine similarity between two vectors.

    Args:
        vector_a (Optional[List[float]]): First vector.
        vector_b (Optional[List[float]]): Second vector.

    Returns:
        float: Cosine similarity score. Returns -1 if either vector is None.
    """
    if vector_a is None or vector_b is None:
        return -1
    return np.dot(vector_a, vector_b) / (
        np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    )


def categorize_complaints(
    reference_df: pd.DataFrame, uncategorized_file: str, output_path: str
) -> None:
    """
    Classifies complaints in the uncategorized dataset by comparing their embeddings to reference embeddings.

    Args:
        reference_df (pd.DataFrame): DataFrame containing labeled complaints and their embeddings.
        uncategorized_file (str): Path to the Excel file containing uncategorized complaints.
    """
    test_df = pd.read_excel(uncategorized_file)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        test_df["embedding"] = list(
            executor.map(generate_text_embedding, test_df["Complaint"])
        )

    reference_vectors = reference_df["embeddings"].tolist()
    reference_categories = reference_df["Issue_category_manual"].tolist()

    categories_assigned = []
    for emb in test_df["embedding"]:
        similarities = [
            compute_cosine_similarity(emb, ref_emb) for ref_emb in reference_vectors
        ]
        best_match_index = np.argmax(similarities)
        best_category = reference_categories[best_match_index]
        categories_assigned.append(best_category)

    test_df["category"] = categories_assigned

    output_file = "complaint_data_categorized.xlsx"
    output_file = os.path.join(output_path, "complaint_data_categorized.xlsx")
    test_df.to_excel(output_file, index=False)
