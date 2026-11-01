from dataclasses import dataclass

from app.schemas.llm_output_schema import DocumentStructure, DetectedRegion, DetectedSection

from app.services.document_service.helper import get_offsets


@dataclass
class BuiltDocumentRegion:
    region_type: str
    identifier: str | None
    title: str | None
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int
    sections: list[DetectedSection]



def build_regions(
    text: str,
    structure: DocumentStructure,
    line_offsets: list[int],
    total_lines : int
) -> list[BuiltDocumentRegion]:
    
        
    # An empty document has no line boundaries to calculate.
    if not text:
        return [
            BuiltDocumentRegion(
                region_type="UNSTRUCTURED",
                identifier=None,
                title=None,
                start_line=1,
                end_line=1,
                start_offset=0,
                end_offset=0,
                sections=[],
            )
        ]
    
    # If the analyzer found no regions, treat the whole document as one region.
    if not structure.regions:
        return [
            BuiltDocumentRegion(
                region_type="UNSTRUCTURED",
                identifier=None,
                title=None,
                start_line=1,
                end_line=total_lines,
                start_offset=0,
                end_offset=len(text),
                sections=[],
            )
        ]
    
    
       

  
            
    # Sort by starting line. If two regions start together, process the
    # longer region first so its metadata remains the primary metadata.
    detected_regions = sorted(
        structure.regions,
        key=lambda region: (region.start_line, -region.end_line),
    )
            
    valid_regions: list[DetectedRegion] = []

    for index,region in enumerate(detected_regions):
        # Skip regions that start outside the document.
        if region.start_line < 1 or region.start_line > total_lines:
            continue

        # Skip regions with an invalid ending line.
        if region.end_line < region.start_line:
            continue
        
        # Keep the end boundary within the document.
        end_line = min(region.end_line, total_lines)
        
        # Copy the region rather than modifying the original model.
        region = region.model_copy(update={"end_line": end_line})
        
        # Ignore whitespace-only regions as structural regions.
        # Their text will still be covered by neighboring regions below.
        start_offset, end_offset = get_offsets(
            text=text,
            line_offsets=line_offsets,
            start_line=region.start_line,
            end_line=region.end_line,
        )
        
        if not text[start_offset:end_offset].strip():
            continue

        valid_regions.append(region)
        
            
    # Keep the first region when regions overlap.
    # Discard later regions that overlap a previously kept region.
    non_overlapping_regions: list[DetectedRegion] = []

    for region in valid_regions:
        # The first region has nothing to overlap with.
        if not non_overlapping_regions:
            non_overlapping_regions.append(region)
            continue

        previous_region = non_overlapping_regions[-1]

        # Discard this region if it overlaps the previous kept region.
        if region.start_line <= previous_region.end_line:
            continue

        non_overlapping_regions.append(region)
            
            
                    
    # If every detected region was invalid or contained only whitespace,
    # preserve the document as one unstructured region.
    if not non_overlapping_regions:
        return [
            BuiltDocumentRegion(
                region_type="UNSTRUCTURED",
                identifier=None,
                title=None,
                start_line=1,
                end_line=total_lines,
                start_offset=0,
                end_offset=len(text),
                sections=[],
            )
        ]
    
    # Cover the entire document without creating separate regions for gaps.
    # Preserve meaningful text before the first detected region.
    first_region = non_overlapping_regions[0]
    first_start_offset, _ = get_offsets(
        text=text,
        line_offsets=line_offsets,
        start_line=first_region.start_line,
        end_line=first_region.end_line,
    )
    leading_text = text[:first_start_offset]

    if leading_text.strip():
        # Keep introductory content separate from the detected region.
        non_overlapping_regions.insert(
            0,
            DetectedRegion(
                region_type="UNSTRUCTURED",
                identifier=None,
                title=None,
                start_line=1,
                end_line=first_region.start_line-1,
                sections=[],
            ),
        )
    else:
        # Leading whitespace belongs to the first detected region.
        non_overlapping_regions[0] = first_region.model_copy(
            update={"start_line": 1}
        )
    
    # Text between regions belongs to the next region.
    for index in range(1, len(non_overlapping_regions)):
        previous_region = non_overlapping_regions[index - 1]
        current_region = non_overlapping_regions[index]

        non_overlapping_regions[index] = current_region.model_copy(
            update={"start_line": previous_region.end_line + 1}
        )
        
    # Trailing text belongs to the last region.
    non_overlapping_regions[-1] = non_overlapping_regions[-1].model_copy(
        update={"end_line": total_lines}
    )
    
    # Convert the detected-region models into the dataclasses used
    # by the next processing stage. Section conversion happens later.
    document_regions: list[BuiltDocumentRegion] = []

    for index, region in enumerate(non_overlapping_regions):
        start_offset, end_offset = get_offsets(
            text=text,
            line_offsets=line_offsets,
            start_line=region.start_line,
            end_line=region.end_line,
        )
       
        

        document_regions.append(
            BuiltDocumentRegion(
                region_type=region.region_type,
                identifier=region.identifier,
                title=region.title,
                start_line=region.start_line,
                end_line=region.end_line,
                start_offset=start_offset,
                end_offset=end_offset,
                sections=region.sections,
            )
        )
        
         
        # region_text = text[start_offset:end_offset]
    
        # print(
        #     f"Region {index + 1}: "
        #     f"lines {document_regions[index].start_line}-{document_regions[index].end_line}, "
        #     f"offsets {document_regions[index].start_offset}-{document_regions[index].end_offset}, "
        #     f"characters={len(region_text)}"
        # )

    return document_regions

   
    






