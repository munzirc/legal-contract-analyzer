import re
from typing import Any
from google.genai.interactions import FunctionCallStep

def clean_progress_query(query: str) -> str:
    """Clean escaped characters for user-facing progress messages."""

    query = query.replace("\\", "")

    # Remove unnecessary surrounding quotation marks.
    query = query.strip().strip('"').strip("'")

    # Normalize repeated whitespace.
    query = re.sub(r"\s+", " ", query)

    return query.strip()


def get_progress_message(
    function_call: FunctionCallStep,
) -> str:
    """Return a user-friendly message for an agent tool call."""

    tool_name: str = function_call.name
    arguments: dict[str, Any] = function_call.arguments or {}

    if tool_name == "get_document_structure":
        return "Reviewing document structure"

    if tool_name == "get_sections":
        return "Retrieving relevant contract clauses"

    if tool_name == "document_search":
        query = clean_progress_query(
            str(arguments.get("query", ""))
        )

        if query:
            return f'Searching contracts for "{query}"'

        return "Searching the selected contracts"

    return "Analyzing your contracts"