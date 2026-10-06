import io
from dataclasses import dataclass

from pypdf import PdfReader


@dataclass
class ExtractedPage:
    page_number: int
    text: str


@dataclass
class ExtractedDocument:
    pages: list[ExtractedPage]


def extract_document(file_content: bytes) -> ExtractedDocument:
    document = extract_pdf(file_content)

    if not any(page.text.strip() for page in document.pages):
        raise ValueError("Document contains no readable text.")

    return document


def extract_pdf(file_content: bytes) -> ExtractedDocument:
    reader = PdfReader(io.BytesIO(file_content))

    pages: list[ExtractedPage] = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        pages.append(
            ExtractedPage(
                page_number=page_number,
                text=page_text
            )
        )

    return ExtractedDocument(pages=pages)