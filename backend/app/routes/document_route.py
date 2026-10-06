from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session

from app.controllers.document_controller import handle_document_upload
from app.db.database import get_db


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


@router.post("/upload")
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    
    return handle_document_upload(file, db, background_tasks)