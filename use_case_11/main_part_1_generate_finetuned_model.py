from pathlib import Path
from scripts.step_1A_create_training_dataset import create_training_dataset
from scripts.step_1B_create_finetuned_model import fine_tune_model


def main() -> None:

    """
    When this file is executed, the code will run in the following sequence:

    1. step_1A_create_training_dataset.py
    2. step_1B_create_finetuned_model.py

    """
    print(" -------------Step 1. Creating Training Dataset ------------------ \n")    
    
    create_training_dataset()

    project_root = Path(__file__).resolve().parent
    jsonl_path   = project_root / "output" / "training_data.jsonl"

    if not jsonl_path.is_file() or jsonl_path.stat().st_size == 0:
        print("training_data.jsonl is missing or empty - skipping fine-tune.")
        return

    print(" -------------Step 2. Creating Fine-tuned Model ------------------ \n")  
    
    print(f"Starting fine-tuning with {jsonl_path} …")
    model_id = fine_tune_model(str(jsonl_path))

    if model_id:
        print(f"Fine-tuned model ready: {model_id}")


if __name__ == "__main__":
    main()
