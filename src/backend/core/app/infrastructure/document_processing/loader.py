"""Document file loader using pdfplumber."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pdfplumber


@dataclass
class LoadedPage:
    """A single page of extracted text from a document."""

    content: str
    page_number: int
    source_document: str


def load_pdf(file_path: Path) -> list[LoadedPage]:
    """Load text from a PDF file page by page."""
    pages: list[LoadedPage] = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(
                    LoadedPage(
                        content=text, page_number=i + 1, source_document=file_path.name
                    )
                )
    return pages


def load_text(file_path: Path) -> list[LoadedPage]:
    """Load text from a plain text file."""
    content = file_path.read_text(encoding="utf-8")
    return [LoadedPage(content=content, page_number=1, source_document=file_path.name)]


def load_document(file_path: Path) -> list[LoadedPage]:
    """Load a document, dispatching to the appropriate loader by file extension."""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(file_path)
    return load_text(file_path)
