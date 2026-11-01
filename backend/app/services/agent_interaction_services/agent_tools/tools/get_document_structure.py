from uuid import UUID

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.document_model import Document
from app.schemas.document_structure_schema import (
    DocumentStructureItem,
    DocumentStructureResult,
    SectionInfo,
    SubsectionInfo,
)
from app.services.document_service.section_based_chunks.section_validation.serialize_data import (
    deserialize_sections,
)


def get_document_structure(
    document_ids: list[UUID],
) -> DocumentStructureResult:
    unique_document_ids = list(dict.fromkeys(document_ids))

    if not unique_document_ids:
        return DocumentStructureResult(documents=[])

    statement = (
        select(
            Document.id,
            Document.filename,
            Document.validated_structure,
        )
        .where(Document.id.in_(unique_document_ids))
    )

    with SessionLocal() as db:
        rows = db.execute(statement).all()

    rows_by_id = {row.id: row for row in rows}

    missing_ids = [
        document_id
        for document_id in unique_document_ids
        if document_id not in rows_by_id
    ]

    if missing_ids:
        raise ValueError(
            "Documents not found: "
            + ", ".join(str(document_id) for document_id in missing_ids)
        )

    documents: list[DocumentStructureItem] = []

    for document_id in unique_document_ids:
        row = rows_by_id[document_id]
        sections = deserialize_sections(row.validated_structure)

        documents.append(
            DocumentStructureItem(
                document_id=str(row.id),
                filename=row.filename,
                has_structure=bool(sections),
                sections=[
                    SectionInfo(
                        identifier=section.identifier,
                        title=section.title,
                        subsections=[
                            SubsectionInfo(
                                identifier=subsection.identifier,
                                title=subsection.title,
                            )
                            for subsection in section.subsections
                        ],
                    )
                    for section in sections
                ],
            )
        )

    return DocumentStructureResult(documents=documents)