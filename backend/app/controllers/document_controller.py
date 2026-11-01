from uuid import UUID
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from pathlib import Path

from app.models.document_model import Document
from app.models.processing_job_model import ProcessingJob
from app.utils.app_exceptions import AppException
from app.services.document_service.save_document import save_document
from app.services.document_service.document_service import (
    delete_document as delete_document_service,
    get_documents as get_document_service
)


def handle_document_upload(
    file: UploadFile,
    db: Session
) -> dict[str, object] | JSONResponse:

    original_storage_path = None
    pdf_storage_path = None

    try:
        document = save_document(file, db)

        original_storage_path = document.original_storage_path
        pdf_storage_path = document.pdf_storage_path

        job = ProcessingJob(
            document_id=document.id
        )

        db.add(job)
        db.commit()
        db.refresh(document)

        return {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "status": document.status
        }

    except AppException as e:
        db.rollback()
        return JSONResponse(
            status_code=e.status_code,
            content={"message": str(e.message)}
        )

    except Exception as e:
        db.rollback()

        if original_storage_path:
            Path(original_storage_path).unlink(missing_ok=True)

        if (
            pdf_storage_path
            and pdf_storage_path != original_storage_path
        ):
            
            Path(pdf_storage_path).unlink(missing_ok=True)

        print(f"Error while creating document processing job: {e}")

        return JSONResponse(
            status_code=500,
            content={"message": "Failed to queue document for processing."}
        )


def get_document_controller(db: Session) -> list[Document]:
    return get_document_service(db)

def handle_document_delete(
    document_id: UUID,
    db: Session
):
    try:
        deleted = delete_document_service(document_id, db)

        if not deleted:
            return JSONResponse(
                status_code=404,
                content={"message": "Document not found."}
            )

        return JSONResponse(status_code=204, content=None)

    except Exception as e:
        print(f"Error while deleting document: {e}")

        return JSONResponse(
            status_code=500,
            content={"message": "Failed to delete document."}
        )