import uuid
import io
import zipfile
from pathlib import Path

from docx2pdf import convert # type: ignore[import-untyped]
from fastapi import UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.enums.document_file_type import DocumentFileType
from app.enums.document_status import DocumentStatus
from app.models.document_model import Document
from app.utils.app_exceptions import AppException


UPLOAD_DIR = Path("uploads")

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

MIN_TEXT_LENGTH = 100


def save_document(file: UploadFile, db: Session) -> Document:

    if not file.filename:
        raise AppException(
            status_code=400,
            message="Filename is required."
        )

    extension: str = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise AppException(
            "Only PDF and DOCX files are supported.",
            400
        )

    try:
        file_content = file.file.read()
    except Exception as e:
        print(f"Error while reading uploaded file: {e}")
        raise AppException(
            "Failed to read uploaded file.",
            400
        )
        
    if extension == ".docx":
        verify_docx_file(file_content)

    document_id = uuid.uuid4()

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    original_storage_path = (
        UPLOAD_DIR / f"{document_id}{extension}"
    )


    try:
        with open(original_storage_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        print(f"Error while saving file: {e}")
        raise AppException(
            "Failed to save file.",
            500
        )
        
    


    if extension == ".pdf":
        pdf_storage_path = original_storage_path

    else:
        pdf_storage_path = UPLOAD_DIR / f"{document_id}.pdf"

        try:
            convert(
                str(original_storage_path),
                str(pdf_storage_path)
            )
        except Exception as e:
            original_storage_path.unlink(missing_ok=True)
            pdf_storage_path.unlink(missing_ok=True)

            print(f"Error while converting DOCX to PDF: {e}")

            raise AppException(
                "Failed to convert DOCX to PDF.",
                400
            )

  
    try:
        page_count = verify_pdf(pdf_storage_path)
    except AppException:
        original_storage_path.unlink(missing_ok=True)

        if pdf_storage_path != original_storage_path:
            pdf_storage_path.unlink(missing_ok=True)

        raise
    except Exception as e:
        original_storage_path.unlink(missing_ok=True)

        if pdf_storage_path != original_storage_path:
            pdf_storage_path.unlink(missing_ok=True)

        print(f"Error while verifying PDF: {e}")

        raise AppException(
            "The document is invalid or corrupted.",
            400
        )

    file_type = (
        DocumentFileType.PDF
        if extension == ".pdf"
        else DocumentFileType.DOCX
    )

    document = Document(
        id=document_id,
        filename=file.filename,
        file_type=file_type,
        original_storage_path=str(original_storage_path),
        pdf_storage_path=str(pdf_storage_path),
        status=DocumentStatus.UPLOADED,
        page_count=page_count
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)

    except Exception as e:
        db.rollback()

        original_storage_path.unlink(missing_ok=True)

        if pdf_storage_path != original_storage_path:
            pdf_storage_path.unlink(missing_ok=True)

        print(f"Database error while saving document: {e}")

        raise AppException(
            "Failed to save document.",
            500
        )

    return document


def verify_pdf(pdf_path: Path) -> int:
    reader = PdfReader(pdf_path)

    full_text: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        full_text.append(page_text)

    text = "\n".join(full_text)

    pdf_content = "".join(text.split())

    if len(pdf_content) < MIN_TEXT_LENGTH:
        raise AppException(
            "The document does not contain enough readable text.",
            400
        )

    return len(reader.pages)

def verify_docx_file(file_content: bytes) -> None:
    try:
        with zipfile.ZipFile(io.BytesIO(file_content)) as archive:
            required_files = {
                "[Content_Types].xml",
                "word/document.xml",
            }

            file_names = set(archive.namelist())

            if not required_files.issubset(file_names):
                raise AppException(
                    "The uploaded DOCX file is invalid.",
                    400
                )

    except zipfile.BadZipFile:
        raise AppException(
            "The uploaded DOCX file is invalid.",
            400
        )