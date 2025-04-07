import concurrent.futures
import os
import pandas as pd


from llm.llm_engine import (
    fine_tune_model,
    get_category,
)

from utils.file_handler import prepare_fine_tuning_data


def classify_complaints(input_excel: str, output_excel: str, model_name: str) -> None:
    """
    Loads complaints from an Excel file, classifies them, and saves the categorized results.

    Args:
        input_excel (str): Path to the uncategorized complaints file.
        output_excel (str): Path to save the categorized results.
        model_name (str): The fine-tuned model name.
    """
    df_unlabeled = pd.read_excel(input_excel)
    complaint_column = "Complaint"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        categories = list(
            executor.map(
                lambda complaint: get_category(complaint, model_name),
                df_unlabeled[complaint_column],
            )
        )

    df_unlabeled["Category"] = categories
    df_unlabeled.to_excel(output_excel, index=False)


def fine_tuning_classification(
    training_file: str, uncategorized_file_path: str, output_dir: str
) -> None:
    """
    Prepares and organizes file paths for fine-tuning a GPT-based classification model.

    Args:
        training_file (str): Path to the training dataset (Excel file).
        uncategorized_file_path (str) : path to the file with Complaints Data - Uncategorized
        output_dir (str):Path to directory where output files will be stored.

    Returns:
        None
    """

    jsonl_filename: str = "complaints_categorization_finetuning.jsonl"
    jsonl_file_path: str = os.path.join(output_dir, jsonl_filename)

    categorized_output_file: str = "complaint_data_categorized.xlsx"
    categorized_output_file_path: str = os.path.join(
        output_dir, categorized_output_file
    )

    print("Preparing fine-tuning data...")
    prepare_fine_tuning_data(training_file, jsonl_file_path)

    print("Starting fine-tuning process...")
    fine_tuned_model = fine_tune_model(jsonl_file_path)
    if fine_tuned_model:
        print("Classifying complaints using fine-tuned model...")
        classify_complaints(
            uncategorized_file_path, categorized_output_file_path, fine_tuned_model
        )

        print(
            "All complaints classified successfully! Results saved to:",
            categorized_output_file_path,
        )
