import logging
from typing import Callable

logger = logging.getLogger(__name__)


def chunk_fixed(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size character windows with overlap."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    step = chunk_size - overlap
    chunks = [
        text[i : i + chunk_size].strip()
        for i in range(0, len(text), step)
        if text[i : i + chunk_size].strip()
    ]
    logger.debug("fixed: %d chunks (size=%d, overlap=%d)", len(chunks), chunk_size, overlap)
    return chunks


def chunk_sentences(text: str, sentences_per_chunk: int = 5, overlap: int = 1) -> list[str]:
    """Split text into groups of sentences using NLTK."""
    import nltk

    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)

    sentences = nltk.sent_tokenize(text)
    step = sentences_per_chunk - overlap
    chunks = [
        " ".join(sentences[i : i + sentences_per_chunk]).strip()
        for i in range(0, len(sentences), step)
        if " ".join(sentences[i : i + sentences_per_chunk]).strip()
    ]
    logger.debug("sentence: %d chunks (%d per chunk)", len(chunks), sentences_per_chunk)
    return chunks


def chunk_paragraphs(text: str, min_length: int = 50) -> list[str]:
    """Split text on blank-line boundaries, filtering short fragments."""
    chunks = [p.strip() for p in text.split("\n\n") if len(p.strip()) >= min_length]
    logger.debug("paragraph: %d chunks", len(chunks))
    return chunks


_STRATEGIES: dict[str, Callable[..., list[str]]] = {
    "fixed": chunk_fixed,
    "sentence": chunk_sentences,
    "paragraph": chunk_paragraphs,
}

VALID_STRATEGIES = list(_STRATEGIES.keys())


def chunk_text(text: str, strategy: str, **kwargs) -> list[str]:
    """Dispatch text to the selected chunking strategy."""
    if strategy not in _STRATEGIES:
        raise ValueError(f"Unknown strategy '{strategy}'. Choose from: {', '.join(VALID_STRATEGIES)}")

    chunks = _STRATEGIES[strategy](text, **kwargs)

    if not chunks:
        raise ValueError(f"Strategy '{strategy}' produced no chunks.")

    return chunks
