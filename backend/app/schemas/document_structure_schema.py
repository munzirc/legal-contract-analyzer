from pydantic import BaseModel


class SubsectionInfo(BaseModel):
    identifier: str | None = None
    title: str | None = None


class SectionInfo(BaseModel):
    identifier: str | None = None
    title: str | None = None
    subsections: list[SubsectionInfo]


class DocumentStructureItem(BaseModel):
    document_id: str
    filename: str
    has_structure: bool
    sections: list[SectionInfo]


class DocumentStructureResult(BaseModel):
    documents: list[DocumentStructureItem]