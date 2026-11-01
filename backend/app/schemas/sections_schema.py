
from pydantic import BaseModel, Field
from uuid import UUID


class SectionSubsection(BaseModel):
    identifier: str | None = None
    title: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None


class SectionMetadata(BaseModel):
    identifier: str | None = None
    title: str | None = None
    start_offset: int
    end_offset: int
    subsections: list[SectionSubsection]


class MatchedSection(BaseModel):
    chunk_id: str = Field(
        description="ID of the document chunk containing this section."
    )
    identifier: str | None
    level: str
    title: str | None
    start_offset: int
    end_offset: int
    text: str


class DocumentSectionsResult(BaseModel):
    document_id: str
    filename: str
    sections: list[MatchedSection]
    

class SectionQuery(BaseModel):
    document_id: UUID
    query: str = Field(min_length=1, max_length=200)
