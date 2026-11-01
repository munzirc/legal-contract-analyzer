from pydantic import BaseModel


class DetectedSubsection(BaseModel):
    identifier: str | None = None
    title: str | None = None
    start_line: int
    end_line: int


class DetectedSection(BaseModel):
    identifier: str | None = None
    title: str | None = None
    start_line: int
    end_line: int

    subsections: list[DetectedSubsection]


class DocumentStructure(BaseModel):
    sections: list[DetectedSection]