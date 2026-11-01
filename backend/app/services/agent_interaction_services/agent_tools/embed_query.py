
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


MODEL_NAME = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def embed_query(query: str) -> list[float]:
    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=query,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    if not response.embeddings or response.embeddings[0].values is None:
        raise RuntimeError("The API did not return a query embedding.")

    embedding = response.embeddings[0].values

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"but received {len(embedding)}."
        )

    return embedding
