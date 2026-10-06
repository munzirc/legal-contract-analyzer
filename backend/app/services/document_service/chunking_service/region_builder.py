from dataclasses import dataclass
from app.schemas.llm_output_schema import DocumentStructure

@dataclass
class DocumentRegion:
    region_type: str
    identifier: str | None
    title: str | None
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int


def build_regions(
    text: str,
    structure: DocumentStructure
) -> list[DocumentRegion]:

    if not text:
        return []

    lines = text.splitlines(keepends=True)

    document_line_count = len(lines)

    line_offsets: list[int] = []

    offset = 0

    for line in lines:
        line_offsets.append(offset)
        offset += len(line)

    valid_regions = [
        region
        for region in structure.regions
        if 1 <= region.start_line <= document_line_count
    ]


    valid_regions.sort(key=lambda region: region.start_line)

    regions: list[DocumentRegion] = []

  
    current_line = 1

    for index, region in enumerate(valid_regions):

        start_line = region.start_line

        if start_line > current_line:
            regions.append(
                DocumentRegion(
                    region_type="UNSTRUCTURED",
                    identifier=None,
                    title=None,
                    start_line=current_line,
                    end_line=start_line - 1,
                    start_offset=line_offsets[current_line - 1],
                    end_offset=line_offsets[start_line - 1],
                )
            )


        if index + 1 < len(valid_regions):

            next_start_line = valid_regions[index + 1].start_line

            end_line = next_start_line - 1
            end_offset = line_offsets[next_start_line - 1]

        else:
            end_line = document_line_count
            end_offset = len(text)


        regions.append(
            DocumentRegion(
                region_type=region.region_type,
                identifier=region.identifier,
                title=region.title,
                start_line=start_line,
                end_line=end_line,
                start_offset=line_offsets[start_line - 1],
                end_offset=end_offset,
            )
        )

        current_line = end_line + 1


    if not valid_regions:
        return [
            DocumentRegion(
                region_type="UNSTRUCTURED",
                identifier=None,
                title=None,
                start_line=1,
                end_line=document_line_count,
                start_offset=0,
                end_offset=len(text),
            )
        ]

    return regions