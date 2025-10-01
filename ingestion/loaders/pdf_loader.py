import typing as t
from pathlib import Path

try:
    import fitz  # PyMuPDF
except Exception as e:  # pragma: no cover
    fitz = None


def load_pdf_text(path: t.Union[str, Path]) -> str:
    """Extract text from a PDF file using PyMuPDF.

    Returns an empty string if PyMuPDF is not installed.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"PDF not found: {p}")

    if fitz is None:
        # Graceful degradation
        return ""

    text_parts: t.List[str] = []
    with fitz.open(p.as_posix()) as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts)
