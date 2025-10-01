import typing as t
from pathlib import Path

try:
    import docx  # python-docx
except Exception:
    docx = None


def load_docx_text(path: t.Union[str, Path]) -> str:
    """Extract text from a DOCX file.

    Returns an empty string if python-docx is not installed.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"DOCX not found: {p}")

    if docx is None:
        return ""

    document = docx.Document(p.as_posix())
    return "\n".join(paragraph.text for paragraph in document.paragraphs)
