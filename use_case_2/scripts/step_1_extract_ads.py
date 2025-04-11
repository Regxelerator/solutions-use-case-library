import os
import json
import base64
from utils.file_handler import read_json_file, write_to_json_file
from llm.llm_engine import call_openai_for_ad_content, get_prompt_for_extracting_ads


def encode_image(image_path):
    """
    Encodes an image file to a base64 string.

    Args:
        image_path (str): The file path of the image to be encoded.

    Returns:
        str: A base64-encoded string representation of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extracting_text_and_visuals(promotion_dir: str, output_dir: str) -> str | None:
    """
    Extracts text and visual elements from promotion files.

    Args:
        promotion_dir (str): Path to the directory containing promotion files.
        output_dir (str): Path to the directory where 'promotion_descriptions.json' will be saved.

    Returns:
        str: Path to the results file('promotion_descriptions.json).
    """

    results_file = os.path.join(output_dir, "results_output.json")
    if not os.path.exists(results_file):
        with open(results_file, "w") as f:
            json.dump([], f)

    for filename in os.listdir(promotion_dir):
        image_path = os.path.join(promotion_dir, filename)
        base64_image = encode_image(image_path)

        prompt = get_prompt_for_extracting_ads()
        parsed_content = call_openai_for_ad_content(base64_image, prompt)

        if parsed_content:
            parsed_content["image_name"] = filename
        else:
            print(f"OpenAI Failed to extract ad content from {filename}")
            return None

        if os.path.exists(results_file):
            results = read_json_file(results_file)
        else:
            results = []
        results.append(parsed_content)
        write_to_json_file(results_file, results, indent=4)
    return results_file
