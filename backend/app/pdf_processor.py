
from pathlib import Path

import pymupdf


def extract_pdf_text(file_path: str) -> dict:
    """Extract text and page count from a PDF."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    pages = []

    with pymupdf.open(path) as pdf:
        page_count = len(pdf)

        for page in pdf:
            text = page.get_text("text")
            pages.append(text)

    full_text = "\n\n".join(pages)

    return {
        "content": full_text,
        "page_count": page_count
    }
