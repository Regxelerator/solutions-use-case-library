import os
import concurrent.futures
import pandas as pd
from llm.llm_engine import (
    get_prompt_for_few_short_classification,
    generate_gpt_response,
)


def get_category(complaint: str) -> str:
    """
    Classifies a financial consumer complaint using GPT.

    Args:
        complaint (str): The consumer complaint text.

    Returns:
        str: The predicted category label.
    """
    prompt = get_prompt_for_few_short_classification()
    user_message = f"Consumer complaint: {complaint}"
    return generate_gpt_response(prompt, user_message)


def few_shot_classification(input_file: str, output_path: str) -> str:
    """
    Classifies consumer complaints using a GPT-based few-shot learning approach
    and saves the categorized results to an Excel file.

    Args:
        input_file (str): path the input Excel file containing complaints.
        output_path (str): Path to save the categorized output file.

    Returns:
        str : path to file where classfication result file will be saved
    """
    df = pd.read_excel(input_file)
    complaint_column = "Complaint"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        categories = list(executor.map(get_category, df[complaint_column]))

    df.insert(loc=len(df.columns), column="Category_model_response", value=categories)
    output_file = os.path.join(
        output_path, "complaint_data_synthetic_categorized.xlsx"
    )

    df.to_excel(output_file, index=False)
    print("Classification completed and saved successfully.")
    return output_file
