from pathlib import Path

from pypdf import PdfReader


def load_pdf_pages(path: Path) -> list[str]:
    """Return a list of extracted text, one entry per page (1-indexed via enumerate)."""
    reader = PdfReader(str(path))
    return [page.extract_text() or "" for page in reader.pages]
