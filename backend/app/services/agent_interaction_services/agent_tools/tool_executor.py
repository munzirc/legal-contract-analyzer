import logging
from uuid import UUID

from google.genai.interactions import FunctionCallStep

from app.schemas.tool_result_schema import (
    ToolError,
    ToolResult,
)
from app.services.agent_interaction_services.agent_tools.tools.document_search import (
    document_search,
)
from app.services.agent_interaction_services.agent_tools.tools.get_document_structure import (
    get_document_structure,
)
from app.services.agent_interaction_services.agent_tools.tools.get_sections import (
    get_sections,
)
from app.services.agent_interaction_services.agent_tools.document_validation import validate_document_ids

logger = logging.getLogger(__name__)

MAX_SECTION_QUERIES_PER_CALL = 5


def execute_tool(
    function_call: FunctionCallStep,
    document_ids: list[UUID],
) -> ToolResult:

    tool_name = function_call.name
    arguments = function_call.arguments or {}

    try:
        # Only documents selected by the user are authorized.
        authorized_ids = set(document_ids)

        if tool_name == "document_search":
            query = arguments.get("query")
            requested_ids = arguments.get("document_ids")

            if not isinstance(query, str) or not query.strip():
                return ToolResult(
                    success=False,
                    tool=tool_name,
                    error=ToolError(
                        code="INVALID_QUERY",
                        message="A non-empty search query is required.",
                    ),
                )

            parsed_ids, error_code = validate_document_ids(
                requested_ids,
                authorized_ids,
            )

            if error_code:
                messages = {
                    "INVALID_DOCUMENT_IDS": (
                        "Document IDs must be a non-empty list of valid UUID strings."
                    ),
                    "UNAUTHORIZED_DOCUMENT": (
                        "Every requested document must have been selected by the user."
                    ),
                }

                return ToolResult(
                    success=False,
                    tool=tool_name,
                    error=ToolError(
                        code=error_code,
                        message=messages[error_code],
                    ),
                )

            result = document_search(
                query=" ".join(query.split()),
                document_ids=parsed_ids,
            )

        elif tool_name == "get_document_structure":
            result = get_document_structure(
                document_ids=document_ids,
            )


        elif tool_name == "get_sections":
            requested_id = arguments.get("document_id")
            section_queries = arguments.get("section_queries")

            if not isinstance(requested_id, str):
                return ToolResult(
                    success=False,
                    tool=tool_name,
                    error=ToolError(
                        code="INVALID_DOCUMENT_ID",
                        message="A selected document UUID is required.",
                    ),
                )

            try:
                parsed_id = UUID(requested_id)
            except (ValueError, AttributeError, TypeError):
                return ToolResult(
                    success=False,
                    tool=tool_name,
                    error=ToolError(
                        code="INVALID_DOCUMENT_ID",
                        message="The document ID must be a valid UUID.",
                    ),
                )

            if parsed_id not in authorized_ids:
                return ToolResult(
                    success=False,
                    tool=tool_name,
                    error=ToolError(
                        code="UNAUTHORIZED_DOCUMENT",
                        message="The document was not selected by the user.",
                    ),
                )

            if (
                not isinstance(section_queries, list)
                or not section_queries
                or not all(
                    isinstance(query, str) and query.strip()
                    for query in section_queries
                )
            ):
                return ToolResult(
                    success=False,
                    tool=tool_name,
                    error=ToolError(
                        code="INVALID_SECTION_QUERIES",
                        message="Section queries must be a non-empty list of non-empty strings.",
                    ),
                )

            # Remove exact duplicates without modifying the original queries.
            unique_queries = list(dict.fromkeys(section_queries))

            selected_queries = unique_queries[:MAX_SECTION_QUERIES_PER_CALL]
            remaining_queries = unique_queries[MAX_SECTION_QUERIES_PER_CALL:]

            section_results = get_sections(
                document_id=parsed_id,
                section_queries=selected_queries,
            )

            result = {
                "results": section_results,
                "executed_queries": selected_queries,
                "remaining_queries": remaining_queries,
            }


        else:
            return ToolResult(
                success=False,
                tool=tool_name,
                error=ToolError(
                    code="UNSUPPORTED_TOOL",
                    message="The requested tool is not supported.",
                ),
            )

        return ToolResult(
            success=True,
            tool=tool_name,
            data=result,
        )

    except Exception:
        # Log internal details for debugging, but do not expose them to Gemini.
        logger.exception("Tool execution failed: %s", tool_name)

        return ToolResult(
            success=False,
            tool=tool_name,
            error=ToolError(
                code="TOOL_EXECUTION_FAILED",
                message="The tool could not complete the request.",
            ),
        )