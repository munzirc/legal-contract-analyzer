from dataclasses import dataclass

from app.services.document_service.extraction_service.extract_document import ExtractedDocument


@dataclass
class PageTextRange:
    page_number: int
    start_offset: int
    end_offset: int


@dataclass
class CanonicalDocument:
    text: str
    page_ranges: list[PageTextRange]


def build_canonical_text(
    extracted_document: ExtractedDocument,
) -> CanonicalDocument:

    parts: list[str] = []
    page_ranges: list[PageTextRange] = []

    current_offset = 0

    for page in extracted_document.pages:

        page_text = page.text

        start_offset = current_offset

        parts.append(page_text)

        current_offset += len(page_text)

        end_offset = current_offset

        page_ranges.append(
            PageTextRange(
                page_number=page.page_number,
                start_offset=start_offset,
                end_offset=end_offset,
            )
        )

        # Add a newline between PDF pages.
        parts.append("\n")
        current_offset += 1

    text = "".join(parts)

    return CanonicalDocument(
        text=text,
        page_ranges=page_ranges,
    )