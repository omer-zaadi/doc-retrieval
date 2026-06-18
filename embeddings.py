import logging
import os

import google.generativeai as genai

logger = logging.getLogger(__name__)

_MODEL = "models/gemini-embedding-001"


def _client() -> None:
    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of document chunks for indexing."""
    _client()
    embeddings = []
    for i, text in enumerate(texts):
        try:
            result = genai.embed_content(model=_MODEL, content=text, task_type="retrieval_document", output_dimensionality=768)
            embeddings.append(result["embedding"])
        except Exception as exc:
            raise RuntimeError(f"Embedding failed at chunk {i}") from exc

    logger.debug("Embedded %d chunks (dim=%d)", len(embeddings), len(embeddings[0]))
    return embeddings


def embed_query(query: str) -> list[float]:
    """Embed a single search query."""
    _client()
    try:
        result = genai.embed_content(model=_MODEL, content=query, task_type="retrieval_query", output_dimensionality=768)
    except Exception as exc:
        raise RuntimeError("Query embedding failed") from exc

    return result["embedding"]
