from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.controllers.document_controller import (
    handle_document_upload,
    get_document_controller,
    handle_document_delete,
)
from app.db.database import get_db
from app.schemas.document_schema import DocumentListItem


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return handle_document_upload(file, db)


@router.get("", response_model=list[DocumentListItem])
def list_documents(db: Session = Depends(get_db)):
    return get_document_controller(db)

@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    return handle_document_delete(document_id, db)