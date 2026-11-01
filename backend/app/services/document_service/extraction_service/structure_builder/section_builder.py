from dataclasses import dataclass
from app.services.document_service.extraction_service.structure_builder.region_builder import BuiltDocumentRegion
from app.schemas.llm_output_schema import DetectedSection, DetectedSubsection
from app.services.document_service.helper import get_offsets

@dataclass
class DocumentSubsection:
    identifier: str | None
    title: str | None
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int


@dataclass
class DocumentSection:
    identifier: str | None
    title: str | None
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int
    subsections: list[DocumentSubsection]
    
@dataclass
class DocumentRegion:
    region_type: str
    identifier: str | None
    title: str | None
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int
    sections: list[DocumentSection]
    
def build_sections(
    text: str,
    regions: list[BuiltDocumentRegion],
    line_offsets: list[int],
    total_document_lines: int,
) -> list[DocumentRegion]:
    
    validated_regions: list[DocumentRegion] = []
    
    for region in regions:
        
        if not region.sections:
            validated_regions.append(
                DocumentRegion(
                    region_type=region.region_type,
                    identifier=region.identifier,
                    title=region.title,
                    start_line=region.start_line,
                    end_line=region.end_line,
                    start_offset=region.start_offset,
                    end_offset=region.end_offset,
                    sections=[],
                )
            )
            continue
        
        validated_region = DocumentRegion(
            region_type=region.region_type,
            identifier=region.identifier,
            title=region.title,
            start_line=region.start_line,
            end_line=region.end_line,
            start_offset=region.start_offset,
            end_offset=region.end_offset,
            sections=[],
        )
        
        validated_sections: list[DocumentSection] = []
        
        valid_detected_sections : list[DetectedSection] = []
        
        for section in region.sections:
            
            if (
                not 1 <= section.start_line <= total_document_lines
                or not section.start_line <= section.end_line <= total_document_lines
            ):
                continue
            
            if (
                section.start_line < region.start_line
                or section.end_line > region.end_line
            ):
                continue
            
            valid_detected_sections.append(section)
        
        valid_detected_sections.sort(key=lambda section: section.start_line)
        
        non_overlapping_sections: list[DetectedSection] = []
        
        for section in valid_detected_sections:
            if not non_overlapping_sections:
                non_overlapping_sections.append(section)
                continue
            
            previous_section = non_overlapping_sections[-1]

            if section.start_line <= previous_section.end_line:
                continue
            
            non_overlapping_sections.append(section)
        
        for section in non_overlapping_sections:
            section_start_offset, section_end_offset  = get_offsets(
                text=text,
                line_offsets=line_offsets,
                start_line=section.start_line,
                end_line=section.end_line,
            )
            
            validated_subsections: list[DocumentSubsection] = []
            
            valid_detected_subsections : list[DetectedSubsection] = []
            
            for subsection in section.subsections:
                if (
                    not 1 <= subsection.start_line <= total_document_lines
                    or not subsection.start_line <= subsection.end_line <= total_document_lines
                ):
                    continue
                
                if (
                    subsection.start_line < section.start_line
                    or subsection.end_line > section.end_line
                ):
                    continue
                
                valid_detected_subsections.append(subsection)
                
            valid_detected_subsections.sort(key=lambda subsection: subsection.start_line)
            
            non_overlapping_subsections: list[DetectedSubsection] = []
            
            for subsection in valid_detected_subsections:
                if not non_overlapping_subsections:
                    non_overlapping_subsections.append(subsection)
                    continue
                
                previous_subsection = non_overlapping_subsections[-1]

                if subsection.start_line <= previous_subsection.end_line:
                    continue
                
                non_overlapping_subsections.append(subsection)
                
            for subsection in non_overlapping_subsections:
                subsection_start_offset, subsection_end_offset = get_offsets(
                    text=text,
                    line_offsets=line_offsets,
                    start_line=subsection.start_line,
                    end_line=subsection.end_line,
                )
                
                validated_subsections.append(
                    DocumentSubsection(
                        identifier=subsection.identifier,
                        title=subsection.title,
                        start_line=subsection.start_line,
                        end_line=subsection.end_line,
                        start_offset=subsection_start_offset,
                        end_offset=subsection_end_offset,
                    )
                )
                
            validated_sections.append(
                DocumentSection(
                    identifier=section.identifier,
                    title=section.title,
                    start_line=section.start_line,
                    end_line=section.end_line,
                    start_offset=section_start_offset,
                    end_offset=section_end_offset,
                    subsections=validated_subsections,
                )
            )
            
        validated_region.sections = validated_sections
        validated_regions.append(validated_region)
        
    return validated_regions