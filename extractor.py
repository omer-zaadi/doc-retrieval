import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text(file_path: str) -> str:
    """Extract clean text from a PDF or DOCX file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    match path.suffix.lower():
        case ".pdf":
            return _from_pdf(path)
        case ".docx":
            return _from_docx(path)
        case _:
            raise ValueError(f"Unsupported file type: '{path.suffix}'. Expected .pdf or .docx.")


def _from_pdf(path: Path) -> str:
    import pdfplumber

    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            if text := page.extract_text():
                pages.append(text.strip())

    if not pages:
        raise ValueError(f"No extractable text in: {path.name}")

    logger.debug("Extracted %d pages from %s", len(pages), path.name)
    return "\n\n".join(pages)


def _from_docx(path: Path) -> str:
    import docx

    doc = docx.Document(str(path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        raise ValueError(f"No extractable text in: {path.name}")

    logger.debug("Extracted %d paragraphs from %s", len(paragraphs), path.name)
    return "\n\n".join(paragraphs)
