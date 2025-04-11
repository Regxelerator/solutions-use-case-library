from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken
import numpy as np

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tokenizer = tiktoken.get_encoding("cl100k_base")
MAX_TOKENS = 8191


def generate_embedding(
        text: str,
        model: str = "text-embedding-ada-002",
        encoding_format: str = "float"
):
    """
    Generates an embedding for the given text, handling token limits.
    If the text is too long, it will be chunked and averaged.
    """
    try:
        tokens = tokenizer.encode(text)
        if len(tokens) <= MAX_TOKENS:
            response = client.embeddings.create(
                model=model, input=text, encoding_format=encoding_format
            )
            return response.data[0].embedding

        chunks = [
            tokenizer.decode(tokens[i:i + MAX_TOKENS])
            for i in range(0, len(tokens), MAX_TOKENS)
        ]

        embeddings = []
        for chunk in chunks:
            response = client.embeddings.create(
                model=model, input=chunk, encoding_format=encoding_format
            )
            embeddings.append(response.data[0].embedding)

        avg_embedding = np.mean(embeddings, axis=0)
        return avg_embedding.tolist()

    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []
