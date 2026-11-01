from app.services.document_service.section_based_chunks.section_validation.schemas import (
    DocumentSection,
)

def serialize_sections(
    sections: list[DocumentSection],
) -> list[dict]:
    return [
        section.model_dump(mode="json")
        for section in sections
    ]


def deserialize_sections(
    data: list[dict] | None,
) -> list[DocumentSection]:
    if not data:
        return []

    return [
        DocumentSection.model_validate(section_data)
        for section_data in data
    ]