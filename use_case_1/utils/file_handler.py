import pandas as pd
import json
import os
from llm.llm_engine import get_prompt_for_fine_tuned_classification, create_user_prompt


def prepare_fine_tuning_data(training_file: str, jsonl_filename: str) -> None:
    """
    Reads an Excel file containing training data and converts it into a JSONL format
    required for fine-tuning OpenAI models.

    Args:
        training_file (str): Path to the training dataset (Excel).
        jsonl_filename (str): Path to save the JSONL formatted file.
    """
    df = pd.read_excel(training_file)

    with open(jsonl_filename, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            complaint_text = str(row["Complaint"])
            category_label = str(row["Issue_category_manual"])
            example = {
                "messages": [
                    {
                        "role": "system",
                        "content": get_prompt_for_fine_tuned_classification(),
                    },
                    {"role": "user", "content": create_user_prompt(complaint_text)},
                    {"role": "assistant", "content": category_label},
                ]
            }
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def check_file_exists(directory: str, filename: str) -> str:
    """Check if a file exists in the given directory and return the full path."""
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Error: The file '{filename}' was not found in the '{directory}' directory."
        )
    return file_path
