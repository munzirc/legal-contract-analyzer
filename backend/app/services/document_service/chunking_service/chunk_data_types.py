from dataclasses import dataclass, field


@dataclass
class ChunkStructureReference:
    identifier: str | None
    title: str | None
    start_offset: int
    end_offset: int


@dataclass
class BuiltChunk:
    chunk_index: int

    start_offset: int
    end_offset: int
    text: str

    page_start: int
    page_end: int

    region_type: str
    region_identifier: str | None
    region_title: str | None

    # Original section boundaries
    section_identifier: str | None = None
    section_title: str | None = None
    section_start_offset: int | None = None
    section_end_offset: int | None = None

    # Original boundaries of the section's subsections
    subsections: list[ChunkStructureReference] = field(
        default_factory=list
    )