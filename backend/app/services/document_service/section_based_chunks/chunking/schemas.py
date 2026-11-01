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

    # Logical chunk identification
    identifier: str | None = None
    title: str | None = None

    # Original section boundaries, when applicable
    section_start_offset: int | None = None
    section_end_offset: int | None = None

    # Subsection boundaries in the canonical document
    subsections: list[ChunkStructureReference] = field(
        default_factory=list
    )