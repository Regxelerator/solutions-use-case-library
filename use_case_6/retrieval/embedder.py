from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_embedding(
    text: str, model: str = "text-embedding-ada-002", encoding_format: str = "float"
) -> List[float]:
    """
    Generates an embedding for the given text using OpenAI's embedding model.

    :param client: OpenAI client instance.
    :param text: The text input to generate embeddings for.
    :param model: The embedding model to use (default: "text-embedding-ada-002").
    :param encoding_format: The encoding format of the embedding (default: "float").
    :return: A list of float values representing the text embedding.
    """
    try:
        response = client.embeddings.create(
            model=model, input=text, encoding_format=encoding_format
        )
        return response.data[0].embedding

    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []
