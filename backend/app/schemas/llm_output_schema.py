from pydantic import BaseModel

class DocumentRegion(BaseModel):
    region_type: str
    identifier: str | None
    title: str | None
    start_line: int


class DocumentStructure(BaseModel):
    regions: list[DocumentRegion]