from app.services.document_service.section_based_chunks.chunking.schemas import BuiltChunk
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import PageTextRange
from app.services.document_service.chunking_service.helper import get_page_range

TEXT_SPLIT_MAX_LENGTH = 3000
TEXT_SPLIT_OVERLAP_RATIO = 0.15

def split_text_by_length(
    text: str,
    start_offset: int,
    max_length: int,
    overlap_ratio: float,
) -> list[tuple[str, int, int]]:
    pieces: list[tuple[str, int, int]] = []

    current_position = 0

    while current_position < len(text):
        remaining_text = text[current_position:]

        if len(remaining_text) <= max_length:
            split_at = len(text)
        else:
            limit = current_position + max_length

            paragraph_position = text.rfind(
                "\n\n", current_position, limit
            )

            if paragraph_position >= current_position:
                split_at = paragraph_position + 2
            else:
                newline_position = text.rfind(
                    "\n", current_position, limit
                )

                if newline_position >= current_position:
                    split_at = newline_position + 1
                else:
                    sentence_positions = [
                        position
                        for position in range(current_position, limit - 1)
                        if text[position] in ".?!"
                        and text[position + 1].isspace()
                    ]

                    if sentence_positions:
                        split_at = sentence_positions[-1] + 2
                    else:
                        # Otherwise, prefer a word boundary.
                        space_position = text.rfind(
                            " ", current_position, limit
                        )

                        if space_position >= current_position:
                            split_at = space_position + 1
                        else:
                            # No suitable boundary was found.
                            split_at = limit

        piece = text[current_position:split_at]

        piece_start = start_offset + current_position
        piece_end = start_offset + split_at

        pieces.append((piece, piece_start, piece_end))

        if split_at == len(text):
            break

        overlap_length = int(len(piece) * overlap_ratio)
        desired_position = split_at - overlap_length

        # Find whitespace near the desired overlap start.
        search_start = max(current_position + 1, desired_position - 20)
        search_end = min(split_at, desired_position + 21)

        boundary_positions = [
            position
            for position in range(search_start, search_end)
            if text[position].isspace()
        ]

        if boundary_positions:
            next_position = min(
                boundary_positions,
                key=lambda position: abs(position - desired_position),
            )
        else:
            next_position = max(current_position + 1, desired_position)

        current_position = next_position

    return pieces

def build_text_chunks(
    text: str,
    start_offset: int,
    page_ranges: list[PageTextRange],
    chunks: list[BuiltChunk],
    identifier: str | None = None,
    title: str | None = None,
) -> None:
    
    pieces = split_text_by_length(
        text=text,
        start_offset=start_offset,
        max_length=TEXT_SPLIT_MAX_LENGTH,
        overlap_ratio=TEXT_SPLIT_OVERLAP_RATIO,
    )

    for piece_text, piece_start, piece_end in pieces:
        if not piece_text.strip():
            continue

        page_start, page_end = get_page_range(
            text=text,
            start_offset=piece_start,
            end_offset=piece_end,
            page_ranges=page_ranges,
        )

        chunks.append(
            BuiltChunk(
                chunk_index=len(chunks),
                start_offset=piece_start,
                end_offset=piece_end,
                text=piece_text,
                page_start=page_start,
                page_end=page_end,
                identifier=identifier,
                title=title,
            )
        )