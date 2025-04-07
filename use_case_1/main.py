from scripts.few_shot_classifier import few_shot_classification
from scripts.fine_tuning import fine_tuning_classification
from scripts.vector_embedding import embedding_classification
from utils.file_handler import check_file_exists
import os
import sys
import argparse


def main():
    """
    perform the classification by allowing the user to choose a technique.

    - Few-Shot Classification (Using prompt-based approaches)
    - Fine-Tuning (Training a model on labeled complaints)
    - Vector Embeddings (Using cosine similarity for classification)
    """
    current_dir = os.getcwd()
    input_dir = os.path.join(current_dir, "input")
    output_dir = os.path.join(current_dir, "output")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    parser = argparse.ArgumentParser(
        description="Choose a complaint classification technique."
    )
    parser.add_argument(
        "--technique",
        choices=["few-shot", "fine-tuning", "vector-embedding"],
        required=True,
        help="Select the classification technique to use.",
    )

    args = parser.parse_args()

    if args.technique == "few-shot":
        print("\n Running Few-Shot Classification...\n")
        try:
            input_file = "complaint_data_synthetic.xlsx"
            file_path = check_file_exists(input_dir, input_file)
            few_shot_classification(file_path, output_dir)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    elif args.technique == "fine-tuning":
        print("\n Running Fine-Tuning Classification...\n")
        try:
            input_file = "complaint_data_training.xlsx"
            complaints_data_path = check_file_exists(input_dir, input_file)

            uncategorized_file: str = "Complaints Data - Uncategorized.xlsx"
            uncategorized_file_path = check_file_exists(input_dir, uncategorized_file)
            fine_tuning_classification(
                complaints_data_path, uncategorized_file_path, output_dir
            )
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    elif args.technique == "vector-embedding":
        print("\n Running Vector Embedding Classification...\n")
        try:
            reference_data_path = "complaint_data_reference_examples.xlsx"
            reference_data_path = check_file_exists(input_dir, reference_data_path)

            uncategorized_data_path = "complaint_data_synthetic.xlsx"
            uncategorized_data_path = check_file_exists(
                input_dir, uncategorized_data_path
            )

            embedding_classification(
                reference_data_path, uncategorized_data_path, output_dir
            )

        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    print("\n Classification process completed!\n")


if __name__ == "__main__":
    main()
