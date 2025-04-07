import os
import pandas as pd
import concurrent.futures
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Optional


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text_embedding(text: str) -> Optional[List[float]]:
    """
    Generates a vector embedding for a given text using OpenAI's embedding model.

    Args:
        text (str): The input text to be converted into an embedding.

    Returns:
        Optional[List[float]]: The vector embedding of the text or None if an error occurs.
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002", input=text, encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding for text: {e}")
        return None


def create_reference_embeddings(input_file: str) -> None:
    """
    Generates embeddings for labeled complaints and stores them in an Excel file.

    Args:
        input_file (str): Path to the reference complaints dataset (Excel file).
    """
    df = pd.read_excel(input_file)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        df["embeddings"] = list(executor.map(generate_text_embedding, df["Complaint"]))

    df.to_excel(input_file, index=False)
