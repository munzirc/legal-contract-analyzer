from typing import Any, Literal
from pydantic import BaseModel


class ToolError(BaseModel):
    code: str
    message: str


class ToolResult(BaseModel):
    success: bool
    tool: str
    data: Any = None
    error: ToolError | None = None


class FunctionResultContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class FunctionResult(BaseModel):
    type: Literal["function_result"] = "function_result"
    name: str
    call_id: str
    result: list[FunctionResultContent]


class ToolRoundResult(BaseModel):
    results: list[FunctionResult]
    executed_count: int