from fastapi import UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.services.document_service.save_document import save_document
from app.utils.app_exceptions import AppException


def handle_document_upload(file: UploadFile, db: Session):

    try:
        document = save_document(file, db)
      
        print("Received file:", file.filename)

        return {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "status": document.status
        }
    except AppException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": str(e.message)}
        )