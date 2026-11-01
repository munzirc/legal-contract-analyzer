from app.services.document_service.section_based_chunks.section_validation.schemas import DocumentSection, DocumentSubsection
from app.services.document_service.section_based_chunks.structure_detection.schemas import DetectedSection, DetectedSubsection
from app.services.document_service.helper import get_offsets

def validate_sections(
    text: str,
    sections: list[DetectedSection],
    line_offsets: list[int],
    total_document_lines: int,
) -> list[DocumentSection]:
    
    valid_sections: list[DetectedSection] = []

    # Step 1: Validate section line boundaries.
    for section in sections:
        if not (
            1 <= section.start_line <= total_document_lines
            and section.start_line <= section.end_line <= total_document_lines
        ):
            continue

        valid_sections.append(section)

    # Step 2: Sort sections by their starting line.
    valid_sections.sort(key=lambda section: section.start_line)

    # Step 3: Discard overlapping sections.
    non_overlapping_sections: list[DetectedSection] = []

    for section in valid_sections:
        if non_overlapping_sections:
            previous_section = non_overlapping_sections[-1]

            if section.start_line <= previous_section.end_line:
                continue

        non_overlapping_sections.append(section)

    # Step 4: Map sections and calculate canonical text offsets.
    document_sections: list[DocumentSection] = []

    for section in non_overlapping_sections:
        start_offset, end_offset = get_offsets(
            text,
            line_offsets,
            section.start_line,
            section.end_line,
        )

        validated_subsections = validate_subsections(
            text=text,
            subsections=section.subsections,
            section_start_line=section.start_line,
            section_end_line=section.end_line,
            line_offsets=line_offsets,
            total_document_lines=total_document_lines,
        )

        document_section = DocumentSection(
            identifier=section.identifier,
            title=section.title,
            start_line=section.start_line,
            end_line=section.end_line,
            start_offset=start_offset,
            end_offset=end_offset,
            subsections=validated_subsections,
        )

        document_sections.append(document_section)

    return document_sections


def validate_subsections(
    text: str,
    subsections: list[DetectedSubsection],
    section_start_line: int,
    section_end_line: int,
    line_offsets: list[int],
    total_document_lines: int,
) -> list[DocumentSubsection]:
    
    valid_subsections: list[DetectedSubsection] = []

    # Step 1: Validate subsection boundaries and parent containment.
    for subsection in subsections:
        if not (
            1 <= subsection.start_line <= total_document_lines
            and subsection.start_line <= subsection.end_line <= total_document_lines
            and section_start_line <= subsection.start_line
            and subsection.end_line <= section_end_line
        ):
            continue

        valid_subsections.append(subsection)

    # Step 2: Sort subsections by their starting line.
    valid_subsections.sort(key=lambda subsection: subsection.start_line)

    # Step 3: Discard overlapping subsections.
    non_overlapping_subsections: list[DetectedSubsection] = []

    for subsection in valid_subsections:
        if non_overlapping_subsections:
            previous_subsection = non_overlapping_subsections[-1]

            if subsection.start_line <= previous_subsection.end_line:
                continue

        non_overlapping_subsections.append(subsection)

    # Step 4: Calculate offsets and map to DocumentSubsection.
    document_subsections: list[DocumentSubsection] = []

    for subsection in non_overlapping_subsections:
        start_offset, end_offset = get_offsets(
            text,
            line_offsets,
            subsection.start_line,
            subsection.end_line,
        )

        document_subsections.append(
            DocumentSubsection(
                identifier=subsection.identifier,
                title=subsection.title,
                start_line=subsection.start_line,
                end_line=subsection.end_line,
                start_offset=start_offset,
                end_offset=end_offset,
            )
        )

    return document_subsections