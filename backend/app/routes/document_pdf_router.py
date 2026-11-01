
import re
from collections.abc import Iterator
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from app.controllers.document_pdf_controller import (
    get_document_pdf_response,
)


router = APIRouter(
    prefix="/api/pdf",
    tags=["PDF"]
)

CHUNK_SIZE = 64 * 1024


def parse_byte_range(
    range_header: str | None,
    file_size: int,
) -> tuple[int, int] | None:
    """Return an inclusive byte range, or None for a full response."""

    if range_header is None:
        return None

    # This implementation supports one byte range per request.
    # For unsupported or malformed range syntax, ignore the header
    # and return the complete file.
    match = re.fullmatch(
        r"bytes=(\d*)-(\d*)",
        range_header.strip(),
    )

    if match is None:
        if "," in range_header:
            return None

        return None

    first, last = match.groups()

    if not first and not last:
        return None

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail="The requested byte range is not satisfiable.",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    if not first:
        # Suffix range: bytes=-500 means the last 500 bytes.
        suffix_length = int(last)

        if suffix_length <= 0:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="The requested byte range is not satisfiable.",
                headers={"Content-Range": f"bytes */{file_size}"},
            )

        start = max(file_size - suffix_length, 0)
        end = file_size - 1
    else:
        start = int(first)
        end = int(last) if last else file_size - 1

        if start >= file_size or start > end:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                detail="The requested byte range is not satisfiable.",
                headers={"Content-Range": f"bytes */{file_size}"},
            )

        end = min(end, file_size - 1)

    return start, end


def stream_file(
    file_path: Path,
    start: int,
    end: int,
) -> Iterator[bytes]:
    """Stream an inclusive byte range from disk in bounded chunks."""

    with file_path.open("rb") as file:
        file.seek(start)
        remaining = end - start + 1

        while remaining > 0:
            chunk = file.read(min(CHUNK_SIZE, remaining))

            if not chunk:
                break

            remaining -= len(chunk)
            yield chunk


@router.get("/{document_id}")
def get_document_pdf(
    document_id: UUID,
    range_header: str | None = Header(default=None, alias="Range"),
):
    pdf = get_document_pdf_response(document_id)
    
    print("Processing pdf")

    byte_range = parse_byte_range(range_header, pdf.file_size)

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Disposition": "inline",
        "Content-Length": str(pdf.file_size),
    }

    if byte_range is None:
        return StreamingResponse(
            stream_file(pdf.file_path, 0, pdf.file_size - 1)
            if pdf.file_size > 0
            else iter(()),
            media_type=pdf.content_type,
            headers=headers,
        )

    start, end = byte_range
    headers.update(
        {
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{pdf.file_size}",
        }
    )

    return StreamingResponse(
        stream_file(pdf.file_path, start, end),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        media_type=pdf.content_type,
        headers=headers,
    )
