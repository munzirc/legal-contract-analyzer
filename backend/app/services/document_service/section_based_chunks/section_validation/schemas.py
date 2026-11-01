from pydantic import BaseModel, ConfigDict, Field


class DocumentSubsection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identifier: str | None = None
    title: str | None = None
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int


class DocumentSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identifier: str | None = None
    title: str | None = None
    start_line: int
    end_line: int
    start_offset: int
    end_offset: int
    subsections: list[DocumentSubsection] = Field(
        default_factory=list
    )