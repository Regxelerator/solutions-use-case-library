import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_prompt_for_extracting_ads() -> str:
    return """
        You are provided with a financial promotion posted on social media (Facebook). Your task is to return a detailed account of the financial promotion. 
        Extract and return all the text from the financial promotion verbatim, clearly distinguishing between the promotion text and the supporting Facebook post text.
        Provide a detailed description of the visual design of the promotion using neutral and objective language.
        The description should be specific enough to enable recreation of the visual design and also highlight differences in the prominence of individual items.

        # Output
        Your response consists of a valid JSON object with the following key-value pairs:
        facebook_post_text: The exact text from the Facebook post accompanying the promotion.
        promotion_text: The exact text from the financial promotion itself.
        visual_description: A detailed, neutral, and objective description of the visual design of the promotion.
    """


def call_openai_for_ad_content(base64_image, prompt):
    """
    Makes a call to the OpenAI API to extract ad content from a given base64-encoded image.

    Parameters:
    - base64_image: The base64-encoded string representing the ad image.
    - prompt: The prompt to send to OpenAI.

    Returns:
    - dict: The parsed ad content or None if an error occurred.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.01,
            max_tokens=2000,
        )

        if "choices" not in response or len(response["choices"]) == 0:
            raise ValueError("Invalid response from the model: No choices found")

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print(f"Error while calling OpenAI API: {e}")
        return None


def get_prompt_for_compliance_assessment(
    chunk_string: str, promotion_string: str
) -> str:
    """
    Generates the prompt for assessing the compliance of a financial promotion
    against regulatory principles using a language model.

    Parameters:
    - chunk_string (str): JSON-formatted string of the evaluation principles (subset).
    - promotion_string (str): JSON-formatted string of the promotion's content and visual attributes.

    Returns:
    - str: The fully formatted prompt string.
    """
    return f"""
            # Role:
            You are a financial supervision analyst with a specialization in consumer protection.
            Your task is to analyze financial promotions posted on social media (Facebook) for their compliance with prescribed regulatory requirements for financial promotions.

            # Instructions:
            1. Review in detail the promotion description in the JSON provided.
            2. Assess the content of the promotion and its visual design components vis-à-vis the stated regulatory principles
            3. Each principle is defined in terms of one or multiple attributes, providing additional clarity on implementation expectations. 
            3. For each principle, assign a quantitative score between 0 and 3, rounded to one decimal place, indicating how well the promotion aligns with that principle and its attributes, whereby 3 reflects the highest alignment.
            4. Provide a qualitative justification for the proposed score.
            
            # Additional guidance:
            * Strictly only rely on the promotion description in arriving at your conclusion.
            * Formulate your justification in the form of a single, detailed sentence, worded neutrally and objectively. 
            * If applicable, cite specific evidence to support your justification.
            * Do not offer any recommendations on the basis of the findings. Focus exclusively on stating the finding and supporting evidence.
            * Strictly return the JSON in the prescribed format

            # Principles:
            {chunk_string}

            # Input (Promotion):
            {promotion_string}

            # Output:
            Your output must be valid JSON.
            For each principle in the chunk, return an object with:
            {{
            "<principle_id>": {{
                "score": "decimal (0.0–3.0, one decimal place)",
                "justification": "string explanation"
            }}
            }}
    """


def get_openai_resp(prompt: str) -> dict:
    """
    Sends a prompt to the OpenAI API and returns the parsed JSON response.

    Parameters:
    - prompt (str): The prompt to send to the GPT model.

    Returns:
    - dict: Parsed JSON response from the model, or an empty dict if parsing fails.
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        api_response = completion.choices[0].message.content
        parsed_response = json.loads(api_response)
        return parsed_response

    except json.JSONDecodeError:
        print("Error decoding JSON response from OpenAI.")
        return {}

    except Exception as e:
        print(f"OpenAI API request failed: {e}")
        return {}


def get_prompt_for_score_with_justification(
    chunk_string: str, promotion_string: str
) -> str:
    """
    Generates a prompt to evaluate a promotion's compliance using a numerical score and detailed justification.

    Parameters:
    - chunk_string (str): JSON-formatted subset of the regulatory principles.
    - promotion_string (str): JSON-formatted string of the promotion's extracted content.

    Returns:
    - str: The formatted prompt for the OpenAI model.
    """
    return f"""
            # Role:
            You are a financial supervision analyst with a specialization in consumer protection.
            Your task is to analyze financial promotions posted on social media (Facebook) for their compliance with prescribed regulatory requirements for financial promotions.

            # Instructions:
            1. Review in detail the promotion description in the JSON provided.
            2. Assess the content of the promotion and its visual design components vis-à-vis the stated regulatory principles
            3. Each principle is defined in terms of one or multiple attributes, providing additional clarity on implementation expectations. 
            3. For each principle, assign a quantitative score (integer) between 0 and 3 indicating how well the promotion aligns with that principle and its attributes, whereby 3 reflects the highest alignment.
            4. Provide a qualitative justification for the proposed score.
            
            # Additional guidance:
            * Strictly only rely on the promotion description in arriving at your conclusion.
            * Formulate your justification in the form of a single, detailed sentence, worded neutrally and objectively. 
            * If applicable, cite specific evidence to support your justification.
            * Do not offer any recommendations on the basis of the findings. Focus exclusively on stating the finding and supporting evidence.

            # Principles:
            {chunk_string}

            # Input (Promotion):
            {promotion_string}

            # Output:
            Your output is a string consisting of the numerical compliance score (0, 1, 2, or 3), follwed by the justification in the following exact format:
            Numerical compliance score Justification: [Placeholder justification]
            You must not prepend the compliance score by anything else.
            """


def call_openai_with_logprobs(prompt: str):
    """
    Sends a prompt to OpenAI and returns the raw response with logprobs.

    Parameters:
    - prompt (str): The prompt to send to the model..

    Returns:
    - response: The raw OpenAI completion response object, or None if error.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            logprobs=True,
            top_logprobs=3,
        )
        return response
    except Exception as e:
        print(f"[ERROR] Failed to call OpenAI: {e}")
        return None
