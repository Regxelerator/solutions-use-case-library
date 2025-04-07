import json
import os
from agents import Runner, trace
from llm.llm_engine import Outline_Agent, Outline_Reviewer_Agent, OutlineReview, Outline
from utils.file_handler import write_to_json_file
from typing import Optional


async def outlining_formulation(output_dir: str) -> Optional[dict]:
    """
    Generates an outline formulation

    Args:
    - output_dir (str): The directory where the search results and outline will be saved.
    """
    input_file = os.path.join(output_dir, "search_results.json")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"file at '{input_file}' not found.")
    topic = "Supervision of AI in financial services"
    max_chars = 200_000

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)

            if not isinstance(json_data, dict):
                raise ValueError("Unexpected JSON format. Expected a dictionary.")

            content_str = json.dumps(json_data, indent=4)
            truncated_content = content_str[:max_chars]
            base_input = f"Topic: {topic} Content:{truncated_content}"

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{input_file}' contains invalid JSON.")
        return
    except ValueError as e:
        print(f"Error: {e}")
        return

    with trace("Step 4: Outline Drafting and Review"):
        max_attempts = 4
        attempt = 1
        while attempt <= max_attempts:
            print(f">>> Attempt {attempt}: Calling Outline Agent")
            outline_result = await Runner.run(Outline_Agent, input=base_input)
            outline = outline_result.final_output_as(Outline)

            review_input = (
                f"Topic: {topic}\n"
                f"Content: {truncated_content}\n"
                f"Current Outline:\n{json.dumps(outline.dict(), indent=2)}"
            )

            print(">>> Calling Reviewer Agent")
            review_result = await Runner.run(Outline_Reviewer_Agent, input=review_input)
            review = review_result.final_output_as(OutlineReview)

            if review.status == "pass":
                print(">>> Reviewer passed the outline.")

                output_file = os.path.join(output_dir, "outline.json")
                write_to_json_file(output_file, outline.dict(), indent=4)
                print(">>> Outline saved to outline.json")
                break

            print(">>> Reviewer requested improvements.")
            print("Feedback:", review.feedback)

            base_input = (
                f"Topic: {topic}"
                f"Content:{truncated_content}"
                f"Current Outline:{json.dumps(outline.dict(), indent=2)}"
                f"Feedback for revision:{review.feedback}"
            )
            attempt += 1
        else:
            print(
                ">>> Outline could not be approved after multiple attempts. Review feedback:"
            )
            print(review.feedback)
