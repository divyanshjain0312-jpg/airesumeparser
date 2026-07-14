"""PDF extraction utilities using PyMuPDF (fitz)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Tuple

import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: Path) -> Tuple[str, int]:
    """Return (raw_text, page_count) for a PDF."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text_parts: list[str] = []
    with fitz.open(pdf_path) as doc:
        page_count = doc.page_count
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts), page_count


def clean_text(raw: str) -> str:
    """Collapse whitespace, drop control chars, normalize newlines."""
    if not raw:
        return ""
    # Remove non-printable control chars except newline/tab
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", raw)
    # Normalize line endings
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse runs of blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # Collapse runs of spaces/tabs on each line
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    # Strip trailing space per line
    cleaned = "\n".join(line.strip() for line in cleaned.split("\n"))
    return cleaned.strip()
