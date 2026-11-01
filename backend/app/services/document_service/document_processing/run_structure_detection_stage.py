
from app.services.document_service.helper import build_line_offsets
from app.services.document_service.section_based_chunks.structure_detection.structure_detector import (
    detect_sections,
)
from app.services.document_service.section_based_chunks.section_validation.validate_sections import (
    validate_sections,
)
from app.services.document_service.section_based_chunks.section_validation.serialize_data import (
    serialize_sections,
)


def run_structure_detection_stage(
    canonical_text: str,
) -> list[dict]:
    if not canonical_text or not canonical_text.strip():
        raise ValueError("Canonical text is missing or empty.")

    # Detect the document's structure.
    structure = detect_sections(canonical_text)

    # Calculate line positions required for validation.
    line_offsets, total_lines = build_line_offsets(canonical_text)

    # Validate the detected sections against the canonical text.
    validated_sections = validate_sections(
        canonical_text,
        structure.sections,
        line_offsets=line_offsets,
        total_document_lines=total_lines,
    )

    # An empty list is valid when no sections are detected.
    return serialize_sections(validated_sections)
