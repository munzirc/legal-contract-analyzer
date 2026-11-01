from pydantic import BaseModel


class DetectedSubsection(BaseModel):
    identifier: str | None
    title: str | None
    start_line: int
    end_line: int


class DetectedSection(BaseModel):
    identifier: str | None
    title: str | None
    start_line: int
    end_line: int
    subsections: list[DetectedSubsection]


class DetectedRegion(BaseModel):
    region_type: str
    identifier: str | None
    title: str | None
    start_line: int
    end_line: int
    sections: list[DetectedSection]


class DocumentStructure(BaseModel):
    regions: list[DetectedRegion]