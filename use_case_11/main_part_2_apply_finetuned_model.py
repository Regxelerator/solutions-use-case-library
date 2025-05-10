from pathlib import Path
from scripts.step_2A_generate_meeting_minutes import generate_minutes_dataset
from scripts.step_2B_create_meeting_minutes_document import generate_word_minutes

def main() -> None:
    """
    When this file is executed, the code will run in the following sequence:

    1. step_2A_generate_meeting_minutes.py — generate JSON drafts from transcript PDFs
    2. step_2B_create_meeting_minutes_document.py — generate Word files from JSON
    """
    print(" -------------Step 1. Generating Meeting Minutes Draft ------------------ \n")    

    meeting_date = input("Please enter the meeting date (YYYY-MM-DD): ").strip()

    if not meeting_date:
        print("Meeting date is required.")
        return

    
    model_name = "Placeholder for model"

    generate_minutes_dataset(model_name, meeting_date)

    print("\n -------------Step 2. Generating Word Document ------------------ \n")  
    generate_word_minutes("output/test_dataset")


if __name__ == "__main__":
    main()
