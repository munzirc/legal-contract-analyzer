from uuid import UUID
import json
from google.genai.interactions import FunctionCallStep

from app.services.agent_interaction_services.agent_tools.tool_executor import execute_tool
from app.schemas.tool_result_schema import ToolResult,ToolError, FunctionResult, FunctionResultContent



def execute_tool_round(
    function_calls: list[FunctionCallStep],
    document_ids: list[UUID],
    max_tool_calls: int
) -> list[FunctionResult]:
    function_results: list[FunctionResult] = []

    for index, function_call in enumerate(function_calls):
        if index >= max_tool_calls:
            result = ToolResult(
                success=False,
                tool=function_call.name,
                error=ToolError(
                    code="ROUND_TOOL_CALL_LIMIT_EXCEEDED",
                    message=(
                        "The maximum number of tool calls for this round "
                        "has been reached. Answer using the evidence "
                        "already retrieved, or continue in another round "
                        "if available."
                    ),
                ),
            )
        else:
            result = execute_tool(function_call, document_ids)

        function_results.append(
            FunctionResult(
                name=function_call.name,
                call_id=function_call.id,
                result=[
                    FunctionResultContent(
                        text=json.dumps(result.model_dump(mode="json"))
                    )
                ],
            )
        )

    return function_results