import io
from dataclasses import dataclass


import pymupdf
import pymupdf4llm #type: ignore


@dataclass
class ExtractedPage:
    page_number: int
    text: str


@dataclass
class ExtractedDocument:
    pages: list[ExtractedPage]


def extract_document(pdf_storage_path: str) -> ExtractedDocument:
    
    with open(pdf_storage_path, "rb") as file:
        file_content = file.read()
            
    document = extract_pdf(file_content)

    if not any(page.text.strip() for page in document.pages):
        raise ValueError("Document contains no readable text.")

    return document


def extract_pdf(file_content: bytes) -> ExtractedDocument:
    pdf = pymupdf.open(stream=io.BytesIO(file_content), filetype="pdf")

    try:
        pages = pymupdf4llm.to_text(
            pdf,
            page_chunks=True,
            header=False,
            footer=False,
            use_ocr=False,
        )
        

        extracted_pages = [
            ExtractedPage(
                page_number=page["metadata"]["page_number"],
                text=page["text"],
            )
            for page in pages
        ]

        return ExtractedDocument(pages=extracted_pages)

    finally:
        pdf.close()