from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.controllers.document_controller import handle_document_upload
from app.db.database import get_db


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