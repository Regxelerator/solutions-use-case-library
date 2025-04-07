from retrieval.embedder import create_reference_embeddings
from retrieval.retriever import (
    load_reference_data_with_embeddings,
    categorize_complaints,
)


def embedding_classification(
    reference_data_path: str, uncategorized_data_path: str, output_dir: str
) -> None:
    """
    perform the classification process using vector embeddings.
    Args:
        reference_data_path (str): Path to the Excel file containing reference complaint data with known categories.
        uncategorized_data_path (str): Path to the Excel file containing uncategorized complaints to be classified.
        output_dir (str): Path to the directory where the categorized output file will be saved.

    Returns:
        None: The function saves the categorized complaints to an Excel file in `output_dir`.
    """
    create_reference_embeddings(reference_data_path)

    reference_df = load_reference_data_with_embeddings(reference_data_path)

    categorize_complaints(reference_df, uncategorized_data_path, output_dir)
