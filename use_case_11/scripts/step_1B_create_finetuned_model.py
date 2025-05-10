import time
from openai import OpenAI
from openai.types.fine_tuning import SupervisedMethod, SupervisedHyperparameters

client = OpenAI()           

def fine_tune_model(jsonl_filename: str) -> str:
    """
    Uploads the JSONL training file and initiates the fine-tuning process.

    Args:
        jsonl_filename (str): Path to the JSONL file.

    Returns:
        str: The ID of the fine-tuned model.
    """
    upload_response = client.files.create(
        file=open(jsonl_filename, "rb"), purpose="fine-tune"
    )
    file_id = upload_response.id

    finetune_response = client.fine_tuning.jobs.create(
        training_file=file_id, 
        model="gpt-4.1-2025-04-14",
        method={
            "type": "supervised",
            "supervised": SupervisedMethod(
                hyperparameters=SupervisedHyperparameters(
                n_epochs=2
            )
            )
        }
    )
    job_id = finetune_response.id

    print("Fine-tuning in progress.")

    while True:
        retrieved_job = client.fine_tuning.jobs.retrieve(job_id)
        status = retrieved_job.status

        if status in ["succeeded", "failed", "cancelled"]:
            break

        time.sleep(600) 

    if status == "succeeded":
        print("Fine-tuning completed successfully!")
        return retrieved_job.fine_tuned_model
    else:
        print(f"Fine-tuning failed or was cancelled. Status: {status}")
        return ""