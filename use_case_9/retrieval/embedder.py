import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str, model: str) -> List[float]:
    """
    Generates an embedding for a given text using the specified OpenAI model.

    Args:
        text (str): The input text to be embedded.
        model (str): The model to use for generating the embedding.

    Returns:
        List[float]: The embedding vector as a list of floats.
    """
    text = text.replace("\n", " ")
    try:
        response = client.embeddings.create(input=[text], model=model)
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error generating embedding for text: {e}")
        raise

