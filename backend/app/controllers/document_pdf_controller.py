
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status

from app.services.document_service.document_pdf_service import (
    DocumentPdf,
    get_document_pdf,
)


@dataclass(frozen=True)
class DocumentPdfResponse:
    document_id: UUID
    file_path: Path
    file_size: int
    content_type: str = "application/pdf"


def get_document_pdf_response(
    document_id: UUID,
) -> DocumentPdfResponse:
    
    document_pdf: DocumentPdf | None = get_document_pdf(document_id)

    if document_pdf is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or PDF file not found.",
        )

    try:
        file_size = document_pdf.file_path.stat().st_size
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to access the PDF file.",
        ) from exc

    return DocumentPdfResponse(
        document_id=document_pdf.document_id,
        file_path=document_pdf.file_path,
        file_size=file_size,
    )
